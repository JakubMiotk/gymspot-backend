import os
import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.notification import (
    PushSubscriptionCreate,
    PushTestBroadcastRequest,
    PushUnsubscribeRequest,
)
from app.services.notification_service import (
    delete_push_subscription_by_endpoint,
    delete_push_subscriptions_by_endpoints,
    get_all_push_subscriptions,
    upsert_push_subscription,
)

router = APIRouter(tags=["notifications"])


@router.post("/push/subscribe")
def subscribe_push(
    payload: PushSubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    upsert_push_subscription(
        db,
        user_id=current_user.id,
        endpoint=payload.endpoint,
        p256dh=payload.keys.p256dh,
        auth=payload.keys.auth,
    )
    return {"msg": "Subskrypcja push zapisana"}


@router.post("/push/unsubscribe")
def unsubscribe_push(
    payload: PushUnsubscribeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = delete_push_subscription_by_endpoint(db, payload.endpoint)
    if not deleted:
        return {"msg": "Subskrypcja nie istniała"}
    return {"msg": "Subskrypcja push usunięta"}


@router.post("/push/test-broadcast")
def send_test_push_to_all(
    payload: PushTestBroadcastRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "trainer":
        raise HTTPException(status_code=403, detail="Tylko trener może wysyłać testowe powiadomienia push")

    vapid_private_key = os.getenv("VAPID_PRIVATE_KEY")
    vapid_public_key = os.getenv("VAPID_PUBLIC_KEY")
    vapid_email = os.getenv("VAPID_EMAIL", "admin@example.com")

    if not vapid_private_key or not vapid_public_key:
        raise HTTPException(
            status_code=500,
            detail="Brakuje VAPID_PRIVATE_KEY lub VAPID_PUBLIC_KEY w .env",
        )

    try:
        from pywebpush import WebPushException, webpush
    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail="Brakuje pakietu pywebpush. Zainstaluj: pip install pywebpush",
        ) from exc

    subscriptions = get_all_push_subscriptions(db)
    if not subscriptions:
        return {
            "msg": "Brak zapisanych subskrypcji push",
            "total": 0,
            "sent": 0,
            "failed": 0,
        }

    message: dict[str, Any] = {
        "title": payload.title,
        "body": payload.body,
        "url": payload.url,
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

    deleted_stale = delete_push_subscriptions_by_endpoints(db, stale_endpoints)

    return {
        "msg": "Wysłano testowe powiadomienie push",
        "total": len(subscriptions),
        "sent": sent,
        "failed": failed,
        "deleted_stale": deleted_stale,
    }
