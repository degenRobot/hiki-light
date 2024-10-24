import datetime
import json
import sqlite3
from fastapi import FastAPI, Depends, HTTPException, Path, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated, Literal
from server.auth import (
    SignedChallenge,
    SignupInfo,
    generate_token,
    generate_challenge,
    get_address_name,
    verify_owner,
    # verify_token,
)
from server.chat import UserMessage, gen_reply, get_character
from server.db import (
    delete_nonce,
    get_conversation,
    get_nonce,
    get_sqlite_conn,
    set_nonce,
    signup_user,
)
from server.types import Challenge, Character, Conversation
from server.eth import verify_signature, address_regex
from server.string import generate_random_hexstring
from charsetup import setup
from sse_starlette.sse import EventSourceResponse

setup()

app = FastAPI(root_path="/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/chat/{user_address}/{character_id}", dependencies=[Depends(verify_owner)])
async def get_chat_history(
    user_address: Annotated[str, Path(regex=address_regex)],
    character_id: str,
    sqlite_conn: Annotated[sqlite3.Connection, Depends(get_sqlite_conn)],
    after: int = 0,
) -> Conversation:
    conv = get_conversation(
        con=sqlite_conn, address=user_address, char_id=character_id, cutoff=after
    )

    return Conversation(conversation=conv)


# TODO: Persist pending chats in the database
# TODO: Throw away new chat messages if there is a pending chat
# TODO: Add rate limits to API


# @app.post("/chat/{character_id}", dependencies=[Depends(verify_token), Depends(verify_owner)]) # with auth
@app.post(
    "/chat/{user_address}/{character_id}",
    dependencies=[Depends(verify_owner)],
    response_class=EventSourceResponse,
)
async def send_new_chat(
    user_address: Annotated[str, Path(regex=address_regex)],
    character_id: str,
    user_message: UserMessage,
    sqlite_conn: Annotated[sqlite3.Connection, Depends(get_sqlite_conn)],
):
    character_card = get_character(character_id)
    if not character_card:
        raise HTTPException(status_code=404, detail="Character not found")
    user_name = get_address_name(user_address)
    return EventSourceResponse(
        gen_reply(
            character_card=character_card,
            user_name=user_name,
            user_message=user_message.message,
            user_address=user_address,
            con=sqlite_conn,
        )
    )


@app.get("/characters/{address}")
async def get_characters(
    response: Response, address: Annotated[str, Path(regex=address_regex)]
) -> dict[str, Character]:
    # TODO: get address's characters from blockchain
    with open("characters.json", "r") as fp:
        characters = json.load(fp)

    response.headers["Content-Type"] = "application/json"
    return characters


@app.get("/auth/challenge")
async def get_challenge(
    address: Annotated[str, Query(regex=address_regex)],
    sqlite_conn: Annotated[sqlite3.Connection, Depends(get_sqlite_conn)],
) -> Challenge:
    nonce = generate_random_hexstring()
    set_nonce(sqlite_conn, address, nonce)
    typed_data = generate_challenge(nonce=nonce, address=address)
    return Challenge(challenge=typed_data)


@app.post("/auth/login")
async def login(
    signed_challenge: SignedChallenge,
    sqlite_conn: Annotated[sqlite3.Connection, Depends(get_sqlite_conn)],
    response: Response,
    signup_info: SignupInfo | None = None,
) -> Literal["OK"]:
    nonce = get_nonce(sqlite_conn, signed_challenge.address)

    if not nonce:
        raise HTTPException(
            status_code=401,
            detail="Challenge expired or never existed. Use /auth/challenge to obtain a new one.",
        )

    (nonce, expires_at) = nonce

    if expires_at < datetime.datetime.now().timestamp():
        raise HTTPException(
            status_code=401,
            detail="Challenge expired or never existed. Use /auth/challenge to obtain a new one.",
        )

    challenge = generate_challenge(address=signed_challenge.address, nonce=nonce)
    verified = verify_signature(
        address=signed_challenge.address,
        message=challenge,
        signature=signed_challenge.signature,
    )

    if not verified:
        raise HTTPException(status_code=401, detail="Invalid signature")

    delete_nonce(sqlite_conn, signed_challenge.address)

    token = generate_token(data={"sub": signed_challenge.address})

    signup_user(
        con=sqlite_conn,
        address=signed_challenge.address,
        name=signup_info.name if signup_info else None,
    )

    response.set_cookie(
        key="token", value=token, httponly=True, max_age=60 * 60 * 24 * 7
    )

    return "OK"
