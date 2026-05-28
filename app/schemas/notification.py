from pydantic import BaseModel, Field


class PushSubscriptionKeys(BaseModel):
    p256dh: str
    auth: str


class PushSubscriptionCreate(BaseModel):
    endpoint: str
    keys: PushSubscriptionKeys


class PushUnsubscribeRequest(BaseModel):
    endpoint: str


class PushTestBroadcastRequest(BaseModel):
    title: str = Field(default="Test push", max_length=120)
    body: str = Field(default="To jest testowe powiadomienie push.", max_length=500)
    url: str = Field(default="/app/", max_length=255)
