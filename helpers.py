from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantCreator
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantsMentions
from telethon import TelegramClient, events, Button
from telethon.errors import UserNotParticipantError
from telethon.tl.types import (
    MessageExtendedMediaPreview, DocumentAttributeAudio, DocumentAttributeSticker,
    Message, MessageMediaPhoto, MessageMediaDocument, MessageMediaGeo,
    DocumentAttributeVideo, DocumentAttributeAnimated,
    MessageMediaPoll, MessageExtendedMedia,)
from dateutil.relativedelta import relativedelta
from datetime import datetime
import asyncio, json, inspect
from telethon import types
from client import *
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
def event_type(event):
    if isinstance(event, events.NewMessage.Event):
        return "NewMessage"
    elif isinstance(event, events.CallbackQuery.Event):
        return "callback"
_me = []
async def is_user(e):
    if not e.is_private: raise events.StopPropagation
    uid = e.sender_id
    etype = event_type(e)    
    print(etype)
    if _me:
        me = _me[0]
    else:
        me = await ABH.get_me()
        _me.append(me)
    key = f"users:{me.id}"
    if r.get(f"{me.id}:{uid}"): return True
    results = await asyncio.gather(
        *(is_in_channel(uid, ch) for ch in channels))
    buttons = [
        [Button.url(f"اشترك في {ch}", url=f"https://t.me/{ch}")]
        for ch, joined in zip(channels, results)
        if not joined]
    if buttons:
        if etype == 'callback':
            await e.edit(
                "🔐 للوصول إلى خدمات البوت يجب الاشتراك في القنوات التالية:",
                buttons=buttons
            )
        else:
            await e.reply(
                "🔐 للوصول إلى خدمات البوت يجب الاشتراك في القنوات التالية:",
                buttons=buttons
            )
        raise events.StopPropagation
    r.set(f"{me.id}:{uid}", 1, ex=120)
    if r.sismember(key, e.sender_id): return True
    r.sadd(key, e.sender_id)
    photo = await get_profile_photo(e.sender_id)
    caption = f'تم تسجيل مستخدم جديد \n اسمه ( {await ment(e)} )\n ايديه  ( `{e.sender_id}` )'    
    if photo:
        await ABH.send_file(wfffp, file=photo, caption=caption, reply_to=e.id)
    else:
        await ABH.send_message(e.chat_id, message=caption, reply_to=e.id)
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
  if isinstance(entity, (int, str)) and str(entity).lstrip('-').isdigit():
    user = await ABH.get_entity(int(entity))
  elif hasattr(entity, "sender"):
    user = await entity.get_sender()
  else:
    user = entity
  user_id = getattr(user, "id", getattr(entity, "sender_id", None))
  p = profile(user_id) if user_id else None
  first_name = getattr(user, "first_name", "مستخدم") if user else "مستخدم"
  name = p.get("name") if p and p.get("name") else first_name
  return f"[{name}](tg://user?id={user_id})"
async def custom_emoji(e, text, emoji, buttons=None):
    selected = random.choice(emoji) if isinstance(emoji, (list, tuple)) else emoji
    await e.reply(
        f'{text} <tg-emoji emoji-id="{selected}">⬆️</tg-emoji>', 
        buttons=buttons, parse_mode='html')
def profile(user_id):
    data = r.get(f"user:{user_id}")
    return json.loads(data) if data else None
async def hint(text):
    await ABH.send_message(wfffp, str(text))
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
    async for user in ABH.iter_participants(chat, filter=ChannelParticipantsAdmins()):
        if isinstance(user.participant, ChannelParticipantCreator):
            return user
    return None
async def send(e, text, buttons=None, id=None, edit=None):
    user_id = id or e.sender_id
    msg_id = getattr(e, 'message_id', None) or (e.message.id if hasattr(e, 'message') else e.id)
    msg = None
    try:
        user_entity = await ABH.get_entity(user_id)
        photos = await ABH.get_profile_photos(user_entity, limit=1)
        if photos:
            if edit:
                return await e.edit(text, file=photos[0], buttons=buttons)
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
                if edit:
                    return await e.edit(text, file=input_media, buttons=buttons)
                
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
    if edit:
        return await e.edit(text, buttons=buttons)
    msg = await e.reply(text, buttons=buttons)
    return msg
def chunk_list(lst, n=2):
    return [lst[i:i + n] for i in range(0, len(lst), n)]
def lprint(*args, **kwargs):
    formatted_args = [str(arg) for arg in args]
    formatted_kwargs = [f"{key}={value}" for key, value in kwargs.items()]
    all_items = formatted_args + formatted_kwargs
    print(" , ".join(all_items))
def print_all():
  caller_frame = inspect.currentframe().f_back
  func_name = caller_frame.f_code.co_name
  caller_locals = caller_frame.f_locals
  items = list(caller_locals.items())[1:]
  formatted_items = []
  for k, v in items:
    if not isinstance(v, (str, int, float, bool, list, dict, set, tuple)):
      continue
    formatted_items.append(f"{k}={v}")
  result = " , ".join(formatted_items)
  print(f"متغيرات دالة ( {func_name} ): \n{result}")
def ordinal_arabic_female(n):
    if not (1 <= n <= 100):
        return None
    ones = [
        "", "الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة",
        "السامة", "السابعة", "الثامنة", "التاسعة", "العاشرة"
    ]    
    tens = {
        20: "العشرون", 30: "الثلاثون", 40: "الأربعون", 
        50: "الخمسون", 60: "الستون", 70: "السبعون", 
        80: "الثمانون", 90: "التسعون"
    }
    if n == 100:
        return "المائة"
    if n <= 10:
        return ones[n]
    if n in tens:
        return tens[n]
    if 11 <= n <= 19:
        units_teen = [
            "", "الحادية", "الثانية", "الثالثة", "الرابعة", 
            "الخامسة", "السادسة", "السابعة", "الثامنة", "التاسعة"
        ]
        return f"{units_teen[n % 10]} عشرة"
    units_compound = [
        "", "الحادية", "الثانية", "الثالثة", "الرابعة", 
        "الخامسة", "السادسة", "السابعة", "الثامنة", "التاسعة"
    ]    
    ten_part = (n // 10) * 10
    one_part = n % 10
    return f"{units_compound[one_part]} و{tens[ten_part]}"
def get_message_type(_msg: Message) -> str:
    if _msg is None:
        return
    if isinstance(_msg.media, MessageExtendedMediaPreview) or isinstance(_msg.media, MessageExtendedMedia):
        inner = _msg.media.media
        return get_message_type(Message(id=_msg.id, media=inner))
    if isinstance(_msg.media, MessageMediaPhoto):
        return "الصور" 
    if isinstance(_msg.media, MessageMediaDocument):
        for attr in _msg.media.document.attributes:
            if isinstance(attr, DocumentAttributeAnimated):
                return "المتحركات"
        for attr in _msg.media.document.attributes:
            if isinstance(attr, DocumentAttributeVideo):
                if getattr(attr, "round_message", False):
                    return "الفويس نوت"
                return "الفيديوهات"  
        for attr in _msg.media.document.attributes:
            if isinstance(attr, DocumentAttributeSticker):
                return "الستيكرات" 
            if isinstance(attr, DocumentAttributeAudio):
                return "الفويسات" if getattr(attr, "voice", False) else "الصوتيات"
        mime = _msg.media.document.mime_type or ""
        if mime.startswith("image/"):
            return "الصور" 
        elif mime.startswith("video/"):
            return "الفيديوهات"  
        elif mime.startswith("audio/"):
            return "الصوتيات" 
