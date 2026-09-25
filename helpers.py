from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantCreator
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantsMentions
from telethon import TelegramClient, events, Button
from telethon.errors import UserNotParticipantError
from dateutil.relativedelta import relativedelta
from datetime import datetime
from telethon import types
from client import *
import asyncio, json
wfffp = 1910015590
channels = [
    'ANYMOUSupdate', 
    'x04ou',
    ]
async def is_in_channel(user_id, channel_username):
    try:
        return await ABH(GetParticipantRequest(channel=channel_username, participant=user_id))
    except UserNotParticipantError:
        return False
    except:
        return False
async def is_user(e):
    if not e.is_private:raise events.StopPropagation
    uid = e.sender_id
    me = await ABH.get_me()
    key = f"users:{me.id}"
    if r.get(f"{me.id}:{uid}"):return True
    results = await asyncio.gather(
        *(is_in_channel(uid, ch) for ch in channels))
    buttons = [
        [Button.url(f"اشترك في {ch}", url=f"https://t.me/{ch}")]
        for ch, joined in zip(channels, results)
        if not joined]
    if buttons:
        await e.reply(
            "🔐 للوصول إلى خدمات البوت يجب الاشتراك في القنوات التالية:",
            buttons=buttons,)
        raise events.StopPropagation
    r.set(f"{me.id}:{uid}", 1, ex=120)
    if r.sismember(key, e.sender_id):return True
    r.sadd(key, e.sender_id)
    photo = await get_profile_photo(e.sender_id)
    caption = f'تم تسجيل مستخدم جديد \n اسمه ( {await ment(e)} )\n ايديه  ( `{e.sender_id}` )'
    if photo:
        await ABH.send_file(wfffp, file=photo, caption=caption, reply_to=e.id)
    else:
        await ABH.send_message(e.chat_id, message=caption, reply_to=e.id)
    return True
async def get_profile_photo(id, user=None):
    photos = []
    try:
        user = user if user else await ABH.get_entity(id)
        photos = await ABH.get_profile_photos(user, limit=1)
        if photos:
            return photos[0]
        else:
            return None
    except:
            return None
async def get_input_media(media_data):
    if not media_data or not isinstance(media_data, dict):return None
    m_id = int(media_data['id'])
    m_hash = int(media_data['hash'])
    m_ref = bytes.fromhex(media_data['ref'])
    if media_data['type'] == "doc":
        return types.InputDocument(id=m_id, access_hash=m_hash, file_reference=m_ref)
    return types.InputPhoto(id=m_id, access_hash=m_hash, file_reference=m_ref)
async def extract_media_data(e):
    if not e.media: return None
    if isinstance(e.media, types.MessageMediaDocument):
        doc = e.media.document
        return {"type": "doc", "id": doc.id, "hash": doc.access_hash, "ref": doc.file_reference.hex()}
    elif isinstance(e.media, types.MessageMediaPhoto):
        photo = e.media.photo
        return {"type": "photo", "id": photo.id, "hash": photo.access_hash, "ref": photo.file_reference.hex()}
    return None
async def ment(entity):
  if hasattr(entity, "sender"):
    user = await entity.get_sender()
  else:
    user = entity
  user_id = getattr(user, "id", getattr(entity, "sender_id", None))
  p = profile(user_id) if user_id else None
  first_name = getattr(user, "first_name", "مستخدم") if user else "مستخدم"
  name = p.get("name") if p and p.get("name") else first_name
  return f"[{name}](tg://user?id={user_id})"
def custom_emoji(emoji):
    selected = random.choice(emoji) if isinstance(emoji, (list, tuple)) else emoji
    return f'<tg-emoji emoji-id={selected}>⬆️</tg-emoji>'
def profile(user_id):
    data = r.get(f"user:{user_id}")
    return json.loads(data) if data else None
async def hint(text):
    await ABH.send_message(wfffp, text)
red = "danger"
green = "success"
blue = "primary"
def create(filename):
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
    with open(filename, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}
def get_years_months_days(past_date_str, date_format="%Y-%m-%d"):
    past_date = datetime.strptime(past_date_str, date_format).date()
    current_date = datetime.now().date()
    difference = relativedelta(current_date, past_date)
    years = difference.years
    months = difference.months
    days = difference.days        
    return years, months, days
async def get_profile_photo(id, user=None):
    photos = []
    try:
        user = user if user else await ABH.get_entity(id)
        photos = await ABH.get_profile_photos(user, limit=1)
        if photos:
            return photos[0]
        else:
            return None
    except:
            return None
async def get_input_media(media_data):
    if not media_data or not isinstance(media_data, dict):return None
    m_id = int(media_data['id'])
    m_hash = int(media_data['hash'])
    m_ref = bytes.fromhex(media_data['ref'])
    if media_data['type'] == "doc":
        return types.InputDocument(id=m_id, access_hash=m_hash, file_reference=m_ref)
    return types.InputPhoto(id=m_id, access_hash=m_hash, file_reference=m_ref)
async def get_channel_owner(chat):
    async for user in REACTBOT.iter_participants(chat, filter=ChannelParticipantsAdmins()):
        if isinstance(user.participant, ChannelParticipantCreator):
            return user
    return None
async def send(e, text, buttons=None, id=None):
    user_id = id or e.sender_id
    msg_id = getattr(e, 'message_id', None) or (e.message.id if hasattr(e, 'message') else e.id)
    msg = None
    try:
        user_entity = await ABH.get_entity(user_id)
        photos = await ABH.get_profile_photos(user_entity, limit=1)
        if photos:
            msg = await ABH.send_file(
                e.chat_id, 
                file=photos[0], 
                caption=text, 
                buttons=buttons, 
                reply_to=msg_id
            )
            return msg
    except Exception as err:
        await hint(f"فشلت محاولة إرسال افتار الـ ID: {err}")
    try:
        p = profile(user_id)
        if p and p.get('media'):
            input_media = await get_input_media(p.get('media'))
            if input_media:
                msg = await ABH.send_file(
                    e.chat_id, 
                    file=input_media, 
                    caption=text, 
                    buttons=buttons, 
                    reply_to=msg_id
                )
                return msg
    except Exception as err:
        await hint(f"فشلت محاولة إرسال ميديا الـ profile: {err}")
    msg = await e.reply(text, buttons=buttons)
    return msg
