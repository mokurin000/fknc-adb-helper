import os

from milky import MilkyClient, OutgoingTextSegment, TextSegmentData
from dotenv import load_dotenv

load_dotenv()


def init_client() -> MilkyClient:
    """
    初始化 QQ 推送客户端
    """

    token = os.environ.get("MILKY_TOKEN", None)
    timeout = float(os.environ.get("MILKY_TIMEOUT", 30))

    client = MilkyClient(
        "http://localhost:3010",
        access_token=token,
        timeout=timeout,
    )
    return client


BOT_CLIENT = init_client()
GROUPS_TO_SEND = list(map(int, os.environ.get("SUBSCRIBE_GROUPS", "").split(",")))


def send_message(msg: str):
    """
    向预配置的群组发送推送
    """

    global BOT_CLIENT
    for group in GROUPS_TO_SEND:
        segdata = TextSegmentData(text=msg)
        outgoing_seg = OutgoingTextSegment(data=segdata)
        BOT_CLIENT.send_group_message(
            group_id=group,
            message=[outgoing_seg],
        )
