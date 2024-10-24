from typing import Annotated
from fastapi import HTTPException, Depends, Body, Path, Query
from fastapi.security import APIKeyCookie
from eth_account import messages
from pydantic import BaseModel
from .eth import address_regex, verify_owner_blockchain
from datetime import timedelta, datetime
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
assert SECRET_KEY is not None
ALGORITHM = "HS256"

cookie_scheme = APIKeyCookie(
    name="token",
    auto_error=False,
    description="JWT auth token. Use /auth/challenge and /auth/login to obtain it.",
)


class SignedChallenge(BaseModel):
    address: Annotated[str, Body(regex=address_regex)]
    signature: str


class SignupInfo(BaseModel):
    name: str


def generate_challenge(
    nonce: str,
    address: Annotated[str, Query(regex=address_regex)],
    domain: str = "https://ai-waifus.com",
):
    challenge = f"Login to {domain} using your address {address} with secret {nonce}"
    return messages.encode_defunct(text=challenge)


def generate_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = (
        datetime.utcnow() + expires_delta if expires_delta else now + timedelta(days=30)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str = Depends(cookie_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")


def verify_owner(
    user_address: Annotated[str, Path(regex=address_regex)],
    character_id: str,
):
    return verify_owner_blockchain(user_address, character_id)


def get_address_name(address: Annotated[str, Path(regex=address_regex)]):
    # TODO: get address's name from sqlite db
    return "Anon"
