import json
import os
from typing import Any, Iterable

from sqlalchemy.orm import Session
from app.models.push_subscription import PushSubscription


def upsert_push_subscription(
    db: Session,
    *,
    user_id: int | None,
    endpoint: str,
    p256dh: str,
    auth: str,
) -> PushSubscription:
    subscription = (
        db.query(PushSubscription)
        .filter(PushSubscription.endpoint == endpoint)
        .first()
    )

    if subscription:
        subscription.user_id = user_id
        subscription.p256dh = p256dh
        subscription.auth = auth
    else:
        subscription = PushSubscription(
            user_id=user_id,
            endpoint=endpoint,
            p256dh=p256dh,
            auth=auth,
        )
        db.add(subscription)

    db.commit()
    db.refresh(subscription)
    return subscription


def delete_push_subscription_by_endpoint(db: Session, endpoint: str) -> bool:
    subscription = (
        db.query(PushSubscription)
        .filter(PushSubscription.endpoint == endpoint)
        .first()
    )
    if not subscription:
        return False

    db.delete(subscription)
    db.commit()
    return True


def delete_push_subscriptions_by_endpoints(db: Session, endpoints: Iterable[str]) -> int:
    endpoint_list = list(endpoints)
    if not endpoint_list:
        return 0

    deleted_count = (
        db.query(PushSubscription)
        .filter(PushSubscription.endpoint.in_(endpoint_list))
        .delete(synchronize_session=False)
    )
    db.commit()
    return int(deleted_count)


def get_all_push_subscriptions(db: Session) -> list[PushSubscription]:
    return db.query(PushSubscription).all()


def get_push_subscriptions_for_user(db: Session, user_id: int) -> list[PushSubscription]:
    return (
        db.query(PushSubscription)
        .filter(PushSubscription.user_id == user_id)
        .all()
    )


def send_push_notification_to_user(
    db: Session,
    *,
    user_id: int,
    title: str,
    body: str,
    url: str = "/app/",
) -> dict[str, Any]:
    vapid_private_key = os.getenv("VAPID_PRIVATE_KEY")
    vapid_public_key = os.getenv("VAPID_PUBLIC_KEY")
    vapid_email = os.getenv("VAPID_EMAIL", "admin@example.com")

    if not vapid_private_key or not vapid_public_key:
        return {
            "total": 0,
            "sent": 0,
            "failed": 0,
            "deleted_stale": 0,
            "reason": "missing_vapid_config",
        }

    try:
        from pywebpush import WebPushException, webpush
    except ImportError:
        return {
            "total": 0,
            "sent": 0,
            "failed": 0,
            "deleted_stale": 0,
            "reason": "missing_pywebpush",
        }

    subscriptions = get_push_subscriptions_for_user(db, user_id)
    if not subscriptions:
        return {
            "total": 0,
            "sent": 0,
            "failed": 0,
            "deleted_stale": 0,
            "reason": "no_subscriptions",
        }

    message: dict[str, str] = {
        "title": title,
        "body": body,
        "url": url,
    }

    sent = 0
    failed = 0
    stale_endpoints: list[str] = []

    for subscription in subscriptions:
        subscription_info = {
            "endpoint": subscription.endpoint,
            "keys": {
                "p256dh": subscription.p256dh,
                "auth": subscription.auth,
            },
        }

        try:
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(message),
                vapid_private_key=vapid_private_key,
                vapid_claims={"sub": f"mailto:{vapid_email}"},
            )
            sent += 1
        except WebPushException as exc:
            failed += 1
            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            if status_code in {404, 410}:
                stale_endpoints.append(subscription.endpoint)
        except Exception:
            failed += 1

    deleted_stale = delete_push_subscriptions_by_endpoints(db, stale_endpoints)

    return {
        "total": len(subscriptions),
        "sent": sent,
        "failed": failed,
        "deleted_stale": deleted_stale,
    }
