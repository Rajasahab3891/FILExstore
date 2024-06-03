# (c)rajasahab3891

import base64
import re
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from config import FORCE_SUB_CHANNEL, ADMINS
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait

async def is_subscribed(client, update):
    if not FORCE_SUB_CHANNEL:
        return True
    user_id = update.from_user.id
    if user_id in ADMINS:
        return True
    try:
        member = await client.get_chat_member(chat_id=FORCE_SUB_CHANNEL, user_id=user_id)
    except UserNotParticipant:
        return False

    if not member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
        return False
    else:
        return True

async def get_messages(client, message_ids):
    messages = []
    total_messages = 0
    chunk_size = 200
    while total_messages!= len(message_ids):
        temb_ids = message_ids[total_messages:total_messages + chunk_size]
        try:
            msgs = await client.get_messages(chat_id=client.channel_id, message_ids=temb_ids)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            msgs = await client.get_messages(chat_id=client.channel_id, message_ids=temb_ids)
        except pyrogram.errors.exceptions.bad_request_400.BadRequest:
            print("Error fetching messages")
            continue
        total_messages += len(temb_ids)
        messages.extend(msgs)
    return messages

async def get_message_id(client, message):
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.channel_id:
            return message.forward_from_message_id
        else:
            return 0
    elif message.forward_sender_name:
        return 0
    elif message.text:
        pattern = "https://t.me/(?:c/)?(.*)/(\d+)"
        matches = re.match(pattern, message.text)
        if not matches:
            return 0
        channel_id = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_id.isdigit():
            if f"-100{channel_id}" == str(client.channel_id):
                return msg_id
        else:
            if channel_id == client.channel_username:
                return msg_id
    else:
        return 0

def get_readable_time(seconds: int) -> str:
    time_suffix_list = ["s", "m", "h", "days"]
    time_list = []
    for i in range(4):
        remainder, result = divmod(seconds, 60) if i < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    time_list.reverse()
    up_time = ":".join(f"{x}{time_suffix_list[i]}" for i, x in enumerate(time_list))
    return up_time

subscribed = filters.create(is_subscribed)
