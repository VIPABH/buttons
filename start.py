from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin
from telethon.errors import UserNotParticipantError
from telethon.tl.types import Channel
from telethon.tl.types import (
    MessageExtendedMediaPreview, DocumentAttributeAudio, DocumentAttributeSticker,
    Message, MessageMediaPhoto, MessageMediaDocument, MessageMediaGeo,
    DocumentAttributeVideo, DocumentAttributeAnimated,
    MessageMediaPoll, MessageExtendedMedia,)
from telethon.tl.types import MessageEntityCustomEmoji
from datetime import datetime
import re, asyncio, os, json
from telethon import events
from io import BytesIO
from helpers import *
from client import *
info = create('info.json')
not_allowed = ['الفويسات', 'الستيكرات', 'الفويس نوت', 'المتحركات']
async def save_data():
    try:
        with open('info.json', 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        await hint(f"خطأ أثناء حفظ البيانات: {e}")
        return False
@ABH.on(events.NewMessage)
async def is_user_check(e):
    await is_user(e)
    await small_filter(e)
@ABH.on(events.NewMessage(pattern=r'^/start'))
async def start(e):
    button = [
        [Button.inline('اضف قناة', data='add_channel', style=green, icon=5280993797482750213)]
    ]
    if str(e.sender_id) in info:
        button.append([Button.inline('حذف قناة', data='deletenr_channel', style=red, icon=5258130763148172425)])
        button[1].append(Button.inline('القنوات', data='channels', style=blue, icon=5188311512791393083))
    await send(e, f'اهلا عزيزي ( {await ment(e)} ) اني بوت مال ازرار استخدامي سهل و بسيط \n ارسل `الاوامر` او أختر من بين الازرار', buttons=button)
message = {}
@ABH.on(events.CallbackQuery(pattern='(add|deletenr)_channel|channels'))
async def start_callback(e):
    data = e.data.decode('utf-8')
    id = e.sender_id
    async def return_names(ids):
        chats = await ABH.get_entity(list(ids))
        return chats
    if data == 'channels':
        if not id in info:return await e.edit('عذرا بس انت ماعندك قنوات مضافة')
        text = 'قنواتك المضافة'
        for num, ch in enumerate(info[id], start=1):
            text+=f'\n{num}- ( `{ch}` )'
        return await e.edit(text)
    elif data.startswith('add'):
        message.setdefault(e.sender_id, {})['step'] = data
        await e.edit('ارسل الان يوزر او ايدي القناة')
    else:
        if not id in info:return await e.edit('عذرا بس انت ماعندك قنوات مضافة')
        ids = list(id for id in info.get(id).keys())
        chats = await return_names(ids)        
        row_button = [Button.inline(ch.title, data=f"delete_channle:{ch.id}") for ch in chats]
        button = chunk_list(row_button, 2)
        await e.edit('اختر قناة لحذفها', buttons=button)
arg = {'text': 'ارسل الان النص', 'media': 'ارسل الان الميديا', 'buttons': 'ارسل الان الزر بالتنسيق الاتي \n اما اسم الزر بعده : وبعده الرابط \nمثال `ابن هاشم-https://t.me/wfffp` \n او اسم الزر بعده الرابط مفصول'}
def buttons(e):
    session = message.get(e.sender_id) or {}
    text = session.get('text') or []
    media = session.get('media') or []
    button = session.get('buttons') or []
    rows = []
    Type = session.get('type')
    if Type in not_allowed:
        if Type == 'الستيكرات':
            pass
        else:
            rows.append([
                Button.inline('إضافة نص', data='set_text', icon=5280993797482750213, style=green if not text else blue),])
    else:
        rows.append([
            Button.inline('إضافة نص', data='set_text', icon=5280993797482750213, style=green if not text else blue),
            Button.inline('إضافة ميديا', data='set_media', icon=5280993797482750213, style=green if not media else blue),])
    if len(media) <= 1:
        rows.append([
            Button.inline('إضافة زر', data='set_buttons', icon=5280993797482750213, style=green if not button else blue)])
    if any(session.values()):
        rows.append([
            Button.inline('حذف الكل', data='del_all', icon=5465665476971471368, style=red),
            Button.inline('حذف معين', data='delete', icon=5229113891081956317, style=red),])
    rows.append([
        Button.inline('تم', data='done', icon=5429501538806548545, style=green)])
    return rows
@ABH.on(events.NewMessage(pattern=r'^/creat_message|انشاء رسالة$'))
async def create_message(e):
    id = e.sender_id
    if id not in message:
        message[id] = {'text': [], 'media': [], 'buttons': []}
    await send(e, 'اهلا عزيزي وين تحب نبدي', buttons=buttons(e))
@ABH.on(events.CallbackQuery(pattern='(set_|del|edit_)'))
async def create_message_callback(e):
    data = e.data.decode('utf-8')
    if not e.sender_id in message:
        return await e.edit('جلسة انشاء الرساله حذفت , اعد المحاولة')
    session = message.get(e.sender_id, None)
    if data == 'del_all':
        del message[e.sender_id]
        return await e.edit('تم حذف الجلسة')
    if data == 'delete':
        text = session.get('text')
        media = session.get('media')
        buttons = session.get('buttons')
        if not text and not media and not buttons:return await e.reply('بعدك ما ضفت شيء حته تحذف ')
        button = []
        if text:
            button.append(Button.inline('تعديل النص', data='edit_text', style=red, icon=5229113891081956317))
        if media:
            button.append(Button.inline('تعديل الميديا', data='edit_media', style=red, icon=5229113891081956317))
        if buttons:
            button.append(Button.inline('تعديل الازرار', data='edit_buttons', style=red, icon=5229113891081956317))
        return await e.reply(f'اختر ما تريد حذفه \n عدد النصوص ( `{len(text)}` )\n عدد الميديا ( `{len(media)}` )\n عدد الأزرار ( `{len(buttons)}` )', buttons=button)
    if data.startswith('set_'):
        data = data.replace('set_', '')
        message[e.sender_id]['step'] = data
        return await e.edit(arg[data])
    if data.startswith('edit_'):
        data = data.replace('edit_', '')
        await callback_handler(e, data)
async def callback_handler(e, data):
    session = message.get(e.sender_id)
    if data == 'text':
        row_text = session.get('text')
        formated_text = [f'{n}- `{text}`' for n, text in enumerate(row_text, start=1)]
        caption == f'''
اختر من النصوص الاتية
{'\n'.join(formated_text)}
يرجى ارسال رقم النص لتعديله
        '''
        await e.edit(caption)
    elif data == 'media':
        media = session.get('media')
        await e.edit('اضغط على ازرار الفيديو للتخصيص')
        for num, item in enumerate(media, start=0):
            b = [
                Button.inline('تغيير الفيديو', data=f'media_change:{num}', style=blue, icon=5264727218734524899),
                Button.inline('حذف الفيديو', data=f'media_delete:{num}', style=blue, icon=5465665476971471368)]
            m = await get_input_media(item)
            await ABH.send_file(e.chat_id, file=m, buttons=b)
    elif data == 'buttons':
        await e.edit('اضغط على الازرار للتخصيص')
        button = session.get('buttons')
        for num, item in enumerate(button, start=0):
            formatted_buttons = []
            icon = None
            style = None
            coloer = None
            if len(item) == 4:
                name, url, coloer, icon = item
            else:
                name, url = item
            if icon:
                formatted_buttons.append([Button.url(name, url, style=coloer, icon=icon)])
            else:
                formatted_buttons.append([Button.url(name, url, style=coloer)])
            buttons_to_send = formatted_buttons if formatted_buttons else None
            b = [
                Button.inline('تعديل الزر', data=f'buttons_change:{num}', style=blue, icon=5264727218734524899),
                Button.inline('حذف الزر', data=f'buttons_delete:{num}', style=blue, icon=5465665476971471368)]
            buttons_to_send.append(b)
            await e.respond(f"**معلومات الزر**\n نص الزر ( {name} )\n الرابط ( {url} )\n لون الزر ( {coloer if coloer else 'شفاف'} )\n الأيقونة ( {icon if icon else 'بدون أيقونة'} )", buttons=formatted_buttons)
translate = {"media": 'الميديا', 'buttons': 'الزر'}
@ABH.on(events.CallbackQuery(pattern=r'^(media|buttons)_(change|delete):(\d+)$'))
async def handle_buttons_and_media(e):
    if not e.sender_id in message:
        return await e.edit('جلسة انشاء الرساله حذفت , اعد المحاولة')
    action_type, action_name, num = re.split(r'[_:]', e.data.decode('utf-8'))
    if action_name == 'change':
        message.setdefault(e.sender_id, {})['step'] = action_type
        del message[e.sender_id][action_type][int(num)]
        await e.edit(f'ارسل الان {translate[action_type]}')
    else:
        del message[e.sender_id]['buttons'][int(num)]
        await e.edit(f'تم ب نجاح حذف {translate[action_name]}')
async def _send(e):
    user_id = e.sender_id    
    if user_id not in message:return
    session = message[user_id]
    row_text = session.get('text') or ["معاينة الرسالة:"]
    text = ' \n '.join(row_text)
    raw_media = session.get('media', [])
    raw_buttons = session.get('buttons', [])
    formatted_buttons = []
    for item in raw_buttons:
        icon = None
        style = None
        coloer = None
        if len(item) == 4:
            name, url, coloer, icon = item
        else:
            name, url = item
        if icon:
            formatted_buttons.append(Button.url(name, url, style=coloer, icon=icon))
        else:
            formatted_buttons.append(Button.url(name, url, style=coloer))
    buttons_to_send = formatted_buttons if formatted_buttons else None
    try:
        if raw_media:
            processed_media = []
            for m in raw_media:
                item = await get_input_media(m) if callable(get_input_media) else m
                if item is not None:
                    processed_media.append(item)
            if not processed_media:
                await ABH.send_message(e.chat_id, message=text, buttons=buttons_to_send)
                return
            if len(processed_media) == 1:
                await ABH.send_file(
                    e.chat_id,
                    file=processed_media[0],
                    caption=text,
                    buttons=buttons_to_send)
            else:
                await ABH.send_file(
                    e.chat_id,
                    file=processed_media,
                    caption=text,
                    buttons=buttons_to_send
                )
        else:
            await ABH.send_message(e.chat_id, message=text, buttons=buttons_to_send)
    except Exception as error:
        await hint(f'error in **_send** \n session ( {session} )\n error ( {error} )')
allowed = ['الصور', 'الفيديوهات']
chat_info = {}
async def small_filter(e):
    session = message.get(e.sender_id) or {}
    if not session:return
    step = session.get('step')
    if not step:return
    text = e.text.strip() or None
    if text == 'انشاء رسالة':return
    if step == 'text':
        message[e.sender_id]['text'].append(text)
        await _send(e)
        await e.reply('تم اضافة النص', buttons=buttons(e))
        del message[e.sender_id]['step']
    elif step == 'media':
        if e.media:
            Type = get_message_type(e.message) or 'النوع غير معروف'
            old_type = session.get('type')
            if old_type:
                if Type != old_type and Type not in allowed and old_type not in allowed:
                    del message[e.sender_id]['step']
                    return await e.reply(f'عذرا بس ماكدر ارسل نوعين مختلفات')
            if len(message[e.sender_id]['media']) > 1 and Type in not_allowed:
                del message[e.sender_id]['step']
                return await e.reply(f'عذرا بس ماكدر ارسل 2 من {Type} ب رسالة وحدة')
            message[e.sender_id]['media'].append(await extract_media_data(e))
            message[e.sender_id]['type'] = Type
            if text:
                message[e.sender_id]['text'].append(text)
            gid = getattr(e, 'grouped_id', None)
            if e.media and gid:
                if gid in processed_groups:
                    return
                processed_groups.add(gid)
            await asyncio.sleep(0.1)
            await _send(e)
            await e.reply('تم اضافة الميديا', buttons=buttons(e))
            del message[e.sender_id]['step']
        else:
            await e.reply('عذرا عزيزي لازم ترسل ميديا مناسبة')
            del message[e.sender_id]['step']
    elif step == 'buttons':
        if '-' in text:
            name, url = text.split('-')
            if not url.startswith(('http://', 'https://', 't.me', 'tg://')):
                return await e.reply('الرابط غير صالح!')
            message[e.sender_id]['buttons'].append((name, url))
            await _send(e)
            await e.reply('تم اضافة الزر', buttons=buttons(e))
            del message[e.sender_id]['step']
        else:
            message[e.sender_id]['temp_btn_name'] = text
            message[e.sender_id]['step'] = 'url'
            await e.reply('تم اضافة اسم الزر\n ارسل الرابط')
    elif step == 'url':
        if not text.startswith(('http://', 'https://', 't.me', 'tg://')):
            return await e.reply('الرابط غير صالح!')
        message[e.sender_id]['url'] = text
        message[e.sender_id]['step'] = 'coloer_button'
        await e.reply('تم اضافة الرابط \n ارسل لون الزر')
    elif step == 'coloer_button':
        COLORS_NAME = {'ازرق': 'primary', 'احمر': 'danger', 'اخضر': 'success', 'شفاف': None}
        if text not in COLORS_NAME.keys():
            return await e.reply(f"عذرا صديقي لازم تختار لون مناسب\nالالوان المتاحة ( {' و '.join(COLORS_NAME.keys())} )")
        message[e.sender_id]['coloer_button'] = COLORS_NAME[text]
        message[e.sender_id]['step'] = 'icon'
        await e.reply('تم اضافة لون الزر \n ارسل ايقونه الزر')
    elif step == 'icon':
        if text == 'تخطي':
            await _send(e)
            await e.reply('تم تخطي الايقونه', buttons=buttons(e))
            temp_btn_name = message[e.sender_id]['temp_btn_name']
            button_name = message[e.sender_id]['url']
            coloer_button = message[e.sender_id]['coloer_button']
            message[e.sender_id]['icon'] = None
            del message[e.sender_id]['step']
            message[e.sender_id]['buttons'].append((temp_btn_name, button_name, coloer_button, message[e.sender_id]['icon']))
            return 
        entities = e.message.entities
        if not entities:
            return await e.reply('ارسل ايموجي مميز او اكتب تخطي!')
        for entity in entities:
            if isinstance(entity, MessageEntityCustomEmoji):
                message[e.sender_id]['icon'] = entity.document_id
                break
        temp_btn_name = message[e.sender_id]['temp_btn_name']
        button_name = message[e.sender_id]['url']
        coloer_button = message[e.sender_id]['coloer_button']
        icon = message[e.sender_id]['icon']
        message[e.sender_id]['buttons'].append((temp_btn_name, button_name, coloer_button, icon))
        await _send(e)
        await e.reply('تم اضافة الزر', buttons=buttons(e))
        del message[e.sender_id]['step']
    elif step == 'add_channel':
        if e.text.startswith('@') or e.text.isdigit() or e.text.startswith('https://'):
            target = e.text
        else:
            return await e.reply('عذرا الايدي او اليوزر غير صحيح')
        try:
            chat = await ABH.get_entity(target)
        except:return await e.edit('عذرا بس ماكدرت اوفر معلومات القناة هاي')
        if not chat:return await e.reply('عذرا بس ماكو هيج قناة')
        if not isinstance(chat, Channel) or not chat.broadcast:
            return await e.reply('صديقي اتفقنه تضيف قناة مو شيء اخر!')
        try:
            bot_user = await ABH.get_me()
            participant = await ABH(GetParticipantRequest(
                channel=chat,
                participant=bot_user.id
            ))    
            is_admin = isinstance(participant.participant, (ChannelParticipantAdmin))
            if not is_admin:
                return await e.reply("البوت مو مشرف! ارفعه مشرف بالاول وعيد المحاولة")
        except UserNotParticipantError:
            return await e.reply("❌ البوت غير موجود في القناة! يرجى إضافته ورفعه مشرفاً أولاً.")
        owner = await get_channel_owner(chat)
        photo_file = None
        if chat.photo:
            photo_bytes = await ABH.download_profile_photo(chat, file=bytes)
            if photo_bytes:
                photo_file = BytesIO(photo_bytes)
                photo_file.name = "photo.jpg"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chat_info.setdefault(e.sender_id, {})
        chat_info[e.sender_id][chat.id] = {
            'channel_name': chat.title,
            'owner': owner.id,
            'added_by': e.sender_id,
            'row_text': e.text,
            'at_time': current_time,
            }
        buttons = [
            Button.inline('نعم', data=f'yes:{chat.id}', style=green),
            Button.inline('لا', data=f'no:{chat.id}', style=red),
        ]
        if photo_file:
            return await e.reply("⚙️ **هل تريد حفظ القناة؟:**", file=photo_file, buttons=buttons)
        return await e.reply("⚙️ **هل تريد حفظ القناة؟:**", buttons=buttons)
@ABH.on(events.CallbackQuery(pattern=r'^(yes|no):(-?\d+)$'))
async def handle_yes_no(e):
    arg = e.pattern_match.group(1).decode('utf-8')
    chat = int(e.pattern_match.group(2))
    id = e.sender_id
    if not id in chat_info:return await e.edit("جلسة اضافة القناة حذفت, عيد المحاولة!")
    if arg == 'yes':
        info.setdefault(e.sender_id, {})
        info[id].update(chat_info[e.sender_id])
        await save_data()
        del chat_info[id]
        await e.edit('تم اضافة القناة ب نجاح')
    else:
        del chat_info[id]
        return await e.edit('تم حذف جلسة اضافة القناة')
commands = ['اضافة قناة', 'حذف قناة', 'انشاء رسالة', 'نشر رسالة', 'زر']
text = "\n".join(f'{n}- `{command}`' for n, command in enumerate(commands, start=1))
@ABH.on(events.NewMessage(pattern=r'^الاوامر'))
async def command(e):
    await e.reply(f'''
    **اوامر البوت📖**
{text}
    ''')
COLORS = {"ازرق": "primary", "blue": "primary",
          "احمر": "danger", "red": "danger",
          "اخضر": "success", "green": "success"}
MAX_BUTTONS = 20
MAX_LABEL_LEN = 64
def norm(w):
    return w.lower().strip().replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
def valid_url(url):
    if url.startswith("tg://"):
        return True
    try:
        p = urlparse(url)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False
def utf16_len(s):
    return len(s.encode("utf-16-le")) // 2
def split_pos(text, sep):
    parts, start = [], 0
    for chunk in text.split(sep):
        idx = text.index(chunk, start)
        parts.append((chunk, idx))
        start = idx + len(chunk)
    return parts
def custom_emoji_id(entities, raw_text, offset_cp, length):
    off = utf16_len(raw_text[:offset_cp])
    for ent in entities:
        if isinstance(ent, MessageEntityCustomEmoji) and ent.offset == off:
            return ent.document_id
    return None
@ABH.on(events.NewMessage(pattern=r"^زر(?:\s+(.+))?$"))
async def handler(event):
    full_text = event.pattern_match.group(1)
    if not full_text:
        return await event.reply(
            "يرجى كتابة الأزرار بعد الأمر، بصيغة:\n\n"
            "`زر اللون اسم الزر الرابط الايموجي`\n\n"
            "مثال:\n`زر ازرق المطور https://t.me/k_4x1 🌚`\n\n"
            "اللون والايموجي اختياريان. لإضافة زر جديد استخدم `|`"
        )
    if not event.is_reply:
        return await event.reply("يجب الرد على الرسالة التي تريد نسخها.")
    reply_msg = await event.get_reply_message()
    if reply_msg is None:
        return await event.reply("تعذّر العثور على الرسالة المردود عليها.")
    raw_text = event.raw_text or ""
    entities = event.message.entities or []
    base_offset = event.pattern_match.start(1)
    items = [(i, p) for i, p in split_pos(full_text, "|") if i.strip()]
    if len(items) > MAX_BUTTONS:
        return await event.reply(f"الحد الأقصى هو {MAX_BUTTONS} زرًا.")
    buttons, row, invalid = [], [], []
    for raw_item, item_pos in items:
        item = raw_item.strip()
        item_offset = item_pos + (len(raw_item) - len(raw_item.lstrip()))
        tokens = list(re.finditer(r"\S+", item))
        parts = [t.group(0) for t in tokens]
        url_index = next((i for i, v in enumerate(parts)
                           if v.startswith(("http://", "https://", "tg://"))), None)
        if url_index is None or not valid_url(parts[url_index]):
            invalid.append(raw_item)
            continue
        url = parts[url_index]
        before = parts[:url_index]
        style = None
        if before and norm(before[0]) in COLORS:
            style, before = COLORS[norm(before[0])], before[1:]
        label = " ".join(before).strip() or "اضغط هنا"
        if len(label) > MAX_LABEL_LEN:
            invalid.append(raw_item)
            continue
        after = parts[url_index + 1:]
        if len(after) > 1:
            invalid.append(raw_item)
            continue
        icon = None
        if after:
            icon_token, icon_match = after[0], tokens[url_index + 1]
            offset_cp = base_offset + item_offset + icon_match.start()
            cid = custom_emoji_id(entities, raw_text, offset_cp, len(icon_token))
            if cid is not None:
                icon = cid
            elif len(icon_token) <= 16:
                icon = icon_token
            else:
                invalid.append(raw_item)
                continue
        try:
            button = Button.url(label, url, style=style, icon=icon)
        except Exception:
            invalid.append(raw_item)
            continue
        row.append(button)
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    if not buttons:
        return await event.reply("لم يتم العثور على أي أزرار صالحة.")
    warning = ""
    if invalid:
        shown = "\n".join(f"• `{x.replace('`', chr(39))}`" for x in invalid[:5])
        warning = f"\n\n⚠️ تم تجاهل بعض الأزرار:\n{shown}"
        if len(invalid) > 5:
            warning += f"\n... و {len(invalid) - 5} أخرى."
    try:
        if reply_msg.media:
            await ABH.send_file(event.chat_id, reply_msg.media,
                                 caption=reply_msg.message or "", buttons=buttons)
        elif reply_msg.message:
            await ABH.send_message(event.chat_id, reply_msg.message, buttons=buttons)
        else:
            return await event.reply("لا يمكن نسخ نوع هذه الرسالة.")
        if warning:
            await ABH.send_message(event.chat_id, f"تم إنشاء الأزرار بنجاح.{warning}")
    except Exception:
        return await event.reply("حدث خطأ أثناء إنشاء الرسالة والأزرار.")
def get_message_type(msg: Message) -> str:
    if msg is None:
        return
    if isinstance(msg.media, MessageExtendedMediaPreview) or isinstance(msg.media, MessageExtendedMedia):
        inner = msg.media.media
        return get_message_type(Message(id=msg.id, media=inner))
    if isinstance(msg.media, MessageMediaPhoto):
        return "الصور" 
    if isinstance(msg.media, MessageMediaDocument):
        for attr in msg.media.document.attributes:
            if isinstance(attr, DocumentAttributeAnimated):
                return "المتحركات"
        for attr in msg.media.document.attributes:
            if isinstance(attr, DocumentAttributeVideo):
                if getattr(attr, "round_message", False):
                    return "الفويس نوت"
                return "الفيديوهات"  
        for attr in msg.media.document.attributes:
            if isinstance(attr, DocumentAttributeSticker):
                return "الستيكرات" 
            if isinstance(attr, DocumentAttributeAudio):
                return "الفويسات" if getattr(attr, "voice", False) else "الصوتيات"
        mime = msg.media.document.mime_type or ""
        if mime.startswith("image/"):
            return "الصور" 
        elif mime.startswith("video/"):
            return "الفيديوهات"  
        elif mime.startswith("audio/"):
            return "الصوتيات" 
