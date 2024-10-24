from server.types import ConvoMessage


def genConvoStr(convo: list[ConvoMessage]) -> str:
    return "\n".join(
        [f"{message.sender}: {message.message}" for message in convo]
    )
