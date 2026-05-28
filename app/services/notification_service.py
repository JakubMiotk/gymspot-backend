from typing import Iterable
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
