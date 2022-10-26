from pydantic import BaseModel


class ReceiverResponse(BaseModel):
    success: bool
    message: str
