from typing import Literal
from pydantic import BaseModel
from eth_account.messages import SignableMessage


class Character(BaseModel):
    Name: str
    id: str


class Challenge(BaseModel):
    challenge: SignableMessage


class ConvoMessage(BaseModel):
    sender: Literal["user", "ai"]
    message: str
    timestamp: int

    def format(self) -> str:
        match self.sender:
            case "user":
                prefix = "User"
            case "ai":
                prefix = "Assistant"

        return f"{prefix}: {self.message}"


class Conversation(BaseModel):
    conversation: list[ConvoMessage]
