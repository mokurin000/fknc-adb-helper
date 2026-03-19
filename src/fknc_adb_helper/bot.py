import os

from milky import MilkyClient, OutgoingTextSegment, TextSegmentData
from dotenv import load_dotenv
from fknc_adb_helper.utils import utc8_time

load_dotenv()


def init_client() -> MilkyClient:
    """
    初始化 QQ 推送客户端
    """

    url = os.environ.get("MILKY_API", "http://localhost:3010")
    token = os.environ.get("MILKY_TOKEN", None)
    timeout = float(os.environ.get("MILKY_TIMEOUT", 30))

    client = MilkyClient(
        url,
        access_token=token,
        timeout=timeout,
    )
    return client


BOT_CLIENT = init_client()
GROUPS_REGULAR = list(map(int, os.environ.get("SUBSCRIBE_GROUPS", "").split(",")))
GROUPS_RAIN = list(map(int, os.environ.get("RAIN_GROUPS", "").split(",")))
NO_DISTURB = list(map(int, os.environ.get("NO_DISTURB", "").split(",")))


def send_message(msg: str, rain: bool = False):
    """
    向预配置的群组发送推送
    """

    global BOT_CLIENT

    segdata = TextSegmentData(text=msg)
    outgoing_seg = OutgoingTextSegment(data=segdata)

    for group in GROUPS_REGULAR if not rain else GROUPS_RAIN:
        if utc8_time().hour < 6 and group in NO_DISTURB:
            continue
        BOT_CLIENT.send_group_message(
            group_id=group,
            message=[outgoing_seg],
        )
