from telethon import events
from helpers import *
from client import *
import re
@ABH.on(events.NewMessage)
async def is_user_check(e):
    await is_user(e)
    await small_filter(e)
@ABH.on(events.NewMessage(pattern=r'^/start'))
async def start(e):
    await send(e, f'اهلا عزيزي ( {await ment(e)} ) اني بوت مال ازرار استخدامي سهل و بسيط \n ارسل `الاوامر`')
message = {}
arg = {'text': 'ارسل الان النص', 'media': 'ارسل الان الميديا', 'buttons': 'ارسل الان الزر بالتنسيق الاتي \n اما اسم الزر بعده : وبعده الرابط \nمثال `ابن هاشم:https://t.me/wfffp` \n او اسم الزر بعده الرابط مفصول'}
@ABH.on(events.NewMessage(pattern=r'^انشاء رسالة$'))
async def create_message(e):
    id = e.sender_id
    if id not in message:
        message[id] = {'text': '', 'media': [], 'buttons': []}
    session = message.get(e.sender_id)
    text = session.get('text')
    b = [[Button.inline('تعيين نص' if not text else 'اضف او تعديل النص' , data='set_text', icon=5280993797482750213, style=blue if not text else green),
        Button.inline('تعيين ميديا' if not text else 'اضف او تعديل الميديا' , data='set_media', icon=5280993797482750213, style= blue if not text else green),
        Button.inline('تعيين زر' if not text else 'اضف او تعديل الزر' , data='set_buttons', icon=5280993797482750213, style= blue if not text else green),],
        [Button.inline('حذف الكل', data='del_all', icon=5465665476971471368, style=red),
        Button.inline('حذف معين', data='delete', icon=5229113891081956317, style=red),],
        [Button.inline('تم', data='done', icon=5854724316385512963, style=green),]]
    await send(e, 'اهلا عزيزي وين تحب نبدي', buttons=b)
@ABH.on(events.CallbackQuery(data='(set_|del)'))
async def create_message_claaback(e):
    data = e.data.decode('utf-8')
    print(data)
    if e.sender_id not in message:
        return await e.edit('جلسة انشاء الرساله حذفت , اعد المحاولة')
    if data == 'del_all':
        del message[e.sender_id]
        return await e.edit('تم حذف الجلسة')
    elif data.startswith('set_'):
        data = data.replace('set_', '')
        message[e.sender_id]['step'] = data
        await e.edit(arg[data])
async def _send(e):
    id = e.sender_id
    if not id in message:return
    b = [Button.inline(button[0], button[1]) for button in message[e.sender_id]['buttons']]
    if message[e.sender_id]['media']:
        if len(message[e.sender_id]['media']) > 1:
            media = [await get_input_media(m) for m in message[e.sender_id]['media']]
        else:
            media = await get_input_media(message[e.sender_id]['media'])
        await ABH.send_file(e.chat_id, file=media, caption=message[e.sender_id]['text'], buttons=b)
    else:
        await ABH.send_message(e.chat_id, text=message[e.sender_id]['text'], buttons=b)
processed_groups = set()
async def small_filter(e):
    session = message.get(e.sender_id, None)
    if not session:return
    step = session.get('step')
    text = e.text
    if step == 'text':
        message[e.sender_id]['text'] += text
        await e.reply('تم اضافة النص')
        await _send(e)
        del message[e.sender_id]['step']
    elif step == 'media':
        if e.media:
            # gid = getattr(msg, 'grouped_id', None)
            # if msg.media and gid:
            #     if gid in processed_groups:
            #         return
            #     processed_groups.add(gid)
            message[e.sender_id]['media'].append(await extract_media_data(e))
            await e.reply('تم اضافة الميديا')
            await _send(e)
            del message[e.sender_id]['step']
        else:
            await e.reply('عذرا عزيزي لازم ترسل ميديا مناسبة')
            await _send(e)
            del message[e.sender_id]['step']
    elif step == 'buttons':
        if ':' in text:
            message[e.sender_id]['buttons'].append(text.split(':'))
            await e.reply('تم اضافة الزر')
            await _send(e)
            del message[e.sender_id]['step']
        else:
            message[e.sender_id]['temp_btn_name'] = text
            message[e.sender_id]['step'] = 'button_name'
            await e.reply('تم اضافة اسم الزر\n ارسل الرابط')
    elif step == 'button_name':
        button_name = message[e.sender_id]['temp_btn_name']
        del message[e.sender_id]['temp_btn_name']
        message[e.sender_id]['buttons'].append((button_name, text))
        await e.reply('تم اضافة الزر')
@ABH.on(events.NewMessage(pattern=r'^الاوامر'))
async def command(e):
    await e.reply(
        f"<b>📋 الأوامر المتاحة كالأتي:</b>\n\n"
        f"تكتب كلمة <code>زر</code> وبعدها رابط الزر، مثال:\n"
        f"<code>زر https://t.me/K_4x1</code>\n\n"
        f"يمكنك أيضاً إضافة لون للزر، مثال:\n"
        f"<code>زر https://t.me/K_4x1 ازرق</code>\n\n"
        f"ويمكنك إضافة إيموجي مميز للزر، مثال:\n"
        f"<code>زر https://t.me/K_4x1</code>{custom_emoji(5465374681915727405)}",
        
        parse_mode='html'
    )
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
