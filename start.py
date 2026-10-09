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
from zoneinfo import ZoneInfo
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
back = [Button.inline('الرجوع', data='back', style=red, icon=5258130763148172425)]
_back = [Button.inline('أظهار الازرار', data='back', style=red, icon=5258130763148172425)]
@ABH.on(events.NewMessage)
async def is_user_check(e):
    await is_user(e)
    await small_filter(e)
@ABH.on(events.NewMessage(pattern=r'^/start'))
async def start(e):
    button = [
        [Button.inline('اضف قناة', data='add_channel', style=green, icon=5280993797482750213)]
    ]
    if str(e.sender_id) in info and info[str(e.sender_id)].keys():
        button.append([Button.inline('حذف قناة', data='remove_channel', style=red, icon=5258130763148172425)])
        button[1].append(Button.inline('القنوات', data='channels', style=blue, icon=5188311512791393083))
    button.append([Button.inline('انشاء رسالة', data="create_message", style=green, icon=5222040745665379997)])
    button.append([Button.inline('نشر رسالة', data="post_message", style=green, icon=5328162777594868795)])
    await send(e, f'اهلا عزيزي ( {await ment(e)} ) اني بوت مال ازرار استخدامي سهل و بسيط \n ارسل `الاوامر` او أختر من بين الازرار', buttons=button)
message = {}
async def return_names(ids):
    return await ABH.get_entity(list(ids))
@ABH.on(events.CallbackQuery(pattern='(add|remove)_channel|channels|create_message'))
async def start_callback(e):
    data = e.data.decode('utf-8')
    id = str(e.sender_id)
    if data == 'channels':
        if not id in info:return await e.edit('عذرا بس انت ماعندك قنوات مضافة', buttons=_back)
        text = 'قنواتك المضافة\n'
        ids = []
        for ch in info[id]:
            ids.append(int(ch))
        chats = await return_names(ids)
        row_names = [f'{num} - ( {chat.title} ) - ( `{chat.id}` )' for num, chat in enumerate(chats, start=1)]
        text += '\n'.join(row_names)
        return await e.edit(text, buttons=back)
    elif data.startswith('add'):
        message.setdefault(e.sender_id, {})['step'] = data
        await e.edit('ارسل الان يوزر او ايدي القناة', buttons=back)
    elif data == 'create_message':
        id = e.sender_id
        if id not in message:
            message[id] = {'text': [], 'media': [], 'buttons': [], 'poll': []}
        await send(e, 'اهلا عزيزي وين تحب نبدي', buttons=buttons(e), edit=True)
    else:
        if not id in info or not info[id].keys():return await e.edit('عذرا بس انت ماعندك قنوات مضافة')
        ids = list(int(id) for id in info.get(id).keys())
        chats = await return_names(ids)
        row_button = [Button.inline(ch.title, data=f"ok_delete_channle:{ch.id}", style=red, icon=5258130763148172425) for ch in chats]
        button = chunk_list(row_button, 2)
        await e.edit('اختر قناة لحذفها', buttons=button)
arg = {'text': 'ارسل الان النص', 'media': 'ارسل الان الميديا', 'buttons': 'ارسل الان الزر بالتنسيق الاتي \n اما اسم الزر بعده : وبعده الرابط \nمثال `ابن هاشم-https://t.me/wfffp` \n او اسم الزر بعده الرابط مفصول', 'poll': "ارسل الان نص (اقل من 5 احرف)"}
def buttons(e):
    id = e.sender_id
    if id not in message:
        message[id] = {'text': [], 'media': [], 'buttons': [], 'poll': []}
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
                Button.inline('إضافة نص', data='set_text', icon=5280993797482750213, style=green if text else blue),])
    else:
        rows.append([
            Button.inline('إضافة نص', data='set_text', icon=5280993797482750213, style=green if text else blue),
            Button.inline('إضافة ميديا', data='set_media', icon=5280993797482750213, style=green if media else blue),])
    if len(media) <= 1:
        if not session.get('icon'):
            rows.append([
                Button.inline('إضافة زر', data='set_buttons', icon=5280993797482750213, style=green if button else blue),
                Button.inline('إضافة تصويت', data='set_poll', icon=5280993797482750213, style=green if button else blue)])
        else:
            rows.append([
                Button.inline('إضافة زر', data='set_buttons', icon=5280993797482750213, style=green if button else blue)])
    if any(session.values()):
        rows.append([
            Button.inline('حذف الكل', data='del_all', icon=5465665476971471368, style=red),
            Button.inline('حذف معين', data='delete', icon=5229113891081956317, style=red),])
    rows.append([
        Button.inline('تم', data='done', icon=5429501538806548545, style=green)])
    return rows
@ABH.on(events.NewMessage(pattern=r'^/create_message|انشاء رسالة$'))
async def create_message(e):
    id = e.sender_id
    if id not in message:
        message[id] = {'text': [], 'media': [], 'buttons': [], 'poll': []}
    await send(e, 'اهلا عزيزي وين تحب نبدي', buttons=buttons(e))
@ABH.on(events.CallbackQuery(pattern=r'^(?:(set|del|edit)_|done|back)'))
async def create_message_callback(e):
    data = e.data.decode('utf-8')
    session = message.get(e.sender_id, None)
    if data == 'back':
        if session:
            step = session.get('step')
            if step:
                del message[e.sender_id]['step']
                return await e.edit('تم الرجوع خطوة الى الخلف', buttons=buttons(e))
            else:
                return await e.edit('اختار من الازرار عزيزي', buttons=buttons(e))
        return await e.edit('اختار من الازرار عزيزي', buttons=buttons(e))
    if not e.sender_id in message:
        return await e.edit('جلسة انشاء الرساله حذفت , اعد المحاولة', buttons=back)
    if data == 'del_all':
        del message[e.sender_id]
        return await e.edit('تم حذف الجلسة')
    if data == 'delete':
        text = session.get('text')
        media = session.get('media')
        row_buttons = session.get('buttons')
        if not text and not media and not row_buttons:return await e.reply('بعدك ما ضفت شيء حته تحذف ')
        button = []
        if text:
            button.append(Button.inline('تعديل النص', data='edit_text', style=red, icon=5229113891081956317))
        if media:
            button.append(Button.inline('تعديل الميديا', data='edit_media', style=red, icon=5229113891081956317))
        if row_buttons:
            button.append(Button.inline('تعديل الازرار', data='edit_buttons', style=red, icon=5229113891081956317))
        return await e.reply(f'اختر ما تريد حذفه \n عدد النصوص ( `{len(text)}` )\n عدد الميديا ( `{len(media)}` )\n عدد الأزرار ( `{len(row_buttons)}` )', buttons=button)
    if data.startswith('set_'):
        data = data.replace('set_', '')
        message[e.sender_id]['step'] = data
        return await e.edit(arg[data], buttons=back)
    if data.startswith('edit_'):
        data = data.replace('edit_', '')
        return await callback_handler(e, data)
    if data == 'done':
        ids = [int(id) for id in info[str(e.sender_id)]]
        chats = await return_names(ids)
        b = [Button.inline(chat.title, data=f'post:{chat.id}') for chat in chats]
        await e.edit("اختار قناة للنشر فيها", buttons=b)
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
        await e.edit(caption, buttons=back)
    elif data == 'media':
        media = session.get('media')
        await e.edit('اضغط على ازرار الفيديو للتخصيص', buttons=back)
        for num, item in enumerate(media, start=0):
            b = [
                Button.inline('تغيير الفيديو', data=f'media_change:{num}', style=blue, icon=5264727218734524899),
                Button.inline('حذف الفيديو', data=f'media_delete:{num}', style=blue, icon=5465665476971471368)]
            m = await get_input_media(item)
            await ABH.send_file(e.chat_id, file=m, buttons=b)
    elif data == 'buttons':
        await e.edit('اضغط على الازرار للتخصيص', buttons=back)
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
                Button.inline('حذف الزر', data=f'buttons_delete:{num}', style=blue, icon=5465665476971471368),
                back[0]]
            buttons_to_send.append(b)
            await e.respond(f"**معلومات الزر**\n نص الزر ( {name} )\n الرابط ( {url} )\n لون الزر ( {coloer if coloer else 'شفاف'} )\n الأيقونة ( {icon if icon else 'بدون أيقونة'} )", buttons=formatted_buttons)
translate = {"media": 'الميديا', 'buttons': 'الزر'}
@ABH.on(events.CallbackQuery(pattern=r'^(media|buttons)_(change|delete):(\d+)$'))
async def handle_buttons_and_media(e):
    if not e.sender_id in message:
        return await e.edit('جلسة انشاء الرساله حذفت , اعد المحاولة', buttons=back)
    action_type, action_name, num = re.split(r'[_:]', e.data.decode('utf-8'))
    if action_name == 'change':
        message.setdefault(e.sender_id, {})['step'] = action_type
        del message[e.sender_id][action_type][int(num)]
        await e.edit(f'ارسل الان {translate[action_type]}', buttons=back)
    else:
        del message[e.sender_id]['buttons'][int(num)]
        await e.edit(f'تم ب نجاح حذف {translate[action_name]}', buttons=back)
DB_FILE = 'poll.json'
def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
polldb = create('poll.json')
async def _send(e, chat=None):
    user_id = e.sender_id    
    if user_id not in message:
        return
    chat_id = chat if chat else e.chat_id
    session = message[user_id]
    row_text = session.get('text') or ["BY - @itsButtonBot"]
    text = ' \n '.join(row_text)
    raw_media = session.get('media', [])
    raw_buttons = session.get('buttons', [])
    row_poll = session.get('poll', [])
    formatted_buttons = []
    for item in raw_buttons:
        if len(item) == 4:
            name, url, coloer, icon = item
            formatted_buttons.append(Button.url(name, url, style=coloer, icon=icon))
        else:
            name, url = item
            formatted_buttons.append(Button.url(name, url, style=coloer))
    name1, name2 = None, None
    if row_poll:
        name1, name2 = row_poll[0]
        formatted_buttons.append([
            Button.inline(f'{name1} ( 0 )', data=f'poll_agree:{user_id}:0', style=green, icon=5449683594425410231),
            Button.inline(f'{name2} ( 0 )', data=f'poll_disagree:{user_id}:0', style=red, icon=5447183459602669338)
        ])
    buttons_to_send = formatted_buttons if formatted_buttons else None
    sent_msg = None
    try:
        if raw_media:
            processed_media = []
            for m in raw_media:
                item = await get_input_media(m) if callable(get_input_media) else m
                if item is not None:
                    processed_media.append(item)
            if not processed_media:
                sent_msg = await ABH.send_message(chat_id, message=text, buttons=buttons_to_send)
            elif len(processed_media) == 1:
                sent_msg = await ABH.send_file(chat_id, file=processed_media[0], caption=text, buttons=buttons_to_send)
            else:
                sent_msg = await ABH.send_file(chat_id, file=processed_media, caption=text, buttons=buttons_to_send)
        else:
            sent_msg = await ABH.send_message(chat_id, message=text, buttons=buttons_to_send)
        if row_poll and sent_msg:
            real_msg_id = str(sent_msg.id)
            user_id_str = str(user_id)
            polldb.setdefault(user_id_str, {})[real_msg_id] = {
                "options": {name1: [], name2: []},
                "names": [name1, name2]
            }
            save_db(polldb)
            updated_poll_buttons = [
                Button.inline(f'{name1} ( 0 )', data=f'poll_agree:{user_id}:{real_msg_id}', style=green, icon=5449683594425410231),
                Button.inline(f'{name2} ( 0 )', data=f'poll_disagree:{user_id}:{real_msg_id}', style=red, icon=5447183459602669338)
            ]
            if formatted_buttons:
                formatted_buttons[-1] = updated_poll_buttons
                await sent_msg.edit(buttons=formatted_buttons)
    except Exception as error:
        await hint(f'error in **_send** \n session ( {session} )\n error ( {error} )')
@ABH.on(events.CallbackQuery(pattern=r'^(poll_agree|poll_disagree):([^:]+):([^:]+)$'))
async def poll_callBack(e):
    row_data = e.data.decode('utf-8')
    data = row_data.split(':')[0]
    sender_id = str(int(e.pattern_match.group(2)))
    message_id = str(int(e.pattern_match.group(3)))
    num = 0 if data == 'poll_agree' else 1
    if sender_id not in polldb or message_id not in polldb[sender_id]:
        return await e.answer('التصويت غير مسجل!')
    db = polldb[sender_id][message_id]
    name1, name2 = db['names']
    a_db = db['options'][name1]
    b_db = db['options'][name2]
    user_id = e.sender_id
    msg_text = ""
    if num == 0:
        if user_id in a_db:
            a_db.remove(user_id)
            msg_text = 'تم حذف تصويتك'
        else:
            if user_id in b_db:
                b_db.remove(user_id)
            a_db.append(user_id)
            msg_text = 'تم إضافة تصويتك'
    else:
        if user_id in b_db:
            b_db.remove(user_id)
            msg_text = 'تم حذف تصويتك (لا)'
        else:
            if user_id in a_db:
                a_db.remove(user_id)
            b_db.append(user_id)
            msg_text = 'تم إضافة تصويتك (لا)'
    await e.answer(msg_text)
    b = [
        [
            Button.inline(f'{name1} ( {len(a_db)} )', data=f'poll_agree:{sender_id}:{message_id}'),
            Button.inline(f'{name2} ( {len(b_db)} )', data=f'poll_disagree:{sender_id}:{message_id}')
        ]
    ]
    await e.edit(buttons=b)
allowed = ['الصور', 'الفيديوهات']
chat_info = {}
async def small_filter(e):
    user_key = str(e.sender_id)
    session = message.get(e.sender_id) or {}
    if not session:return
    step = session.get('step')
    if not step:return
    text = e.text.strip() or None
    if text == 'انشاء رسالة':return
    if step == 'text':
        message.setdefault(e.sender_id, {}).setdefault('text', [])
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
                    return await e.reply('عذرا بس ماكدر ارسل نوعين مختلفات', buttons=back)
            
            message.setdefault(e.sender_id, {}).setdefault('media', [])
            if len(message[e.sender_id]['media']) > 1 and Type in not_allowed:
                del message[e.sender_id]['step']
                return await e.reply(f'عذرا بس ماكدر ارسل 2 من {Type} ب رسالة وحدة', buttons=back)
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
            await e.reply('عذرا عزيزي لازم ترسل ميديا مناسبة', buttons=back)
            del message[e.sender_id]['step']
    elif step == 'buttons':
        if not text:
            return await e.reply('ارسل اسم الزر!')
        message.setdefault(e.sender_id, {}).setdefault('buttons', [])
        if '-' in text:
            name, url = text.split('-', 1)
            name, url = name.strip(), url.strip()
            if not url.startswith(('http://', 'https://', 't.me', 'tg://')):
                return await e.reply('الرابط غير صالح!')
            message[e.sender_id]['buttons'].append((name, url))
            await _send(e)
            await e.reply('تم اضافة الزر', buttons=buttons(e))
            del message[e.sender_id]['step']
        else:
            message[e.sender_id]['temp_btn_name'] = text
            message[e.sender_id]['step'] = 'url'
            await e.reply('تم اضافة اسم الزر\n ارسل الرابط', buttons=back)
    elif step == 'url':
        if not text or not text.startswith(('http://', 'https://', 't.me', 'tg://')):
            return await e.reply('الرابط غير صالح!', buttons=back)
        message[e.sender_id]['url'] = text
        message[e.sender_id]['step'] = 'coloer_button'
        await e.reply('تم اضافة الرابط \n ارسل لون الزر')
    elif step == 'coloer_button':
        COLORS_NAME = {'ازرق': 'primary', 'احمر': 'danger', 'اخضر': 'success', 'شفاف': None}
        if text not in COLORS_NAME:
            return await e.reply(
                f"عذرا صديقي لازم تختار لون مناسب\nالالوان المتاحة ( {' و '.join(COLORS_NAME.keys())} )", buttons=back)
        message[e.sender_id]['coloer_button'] = COLORS_NAME[text]
        message[e.sender_id]['step'] = 'icon'
        await e.reply('تم اضافة لون الزر \n ارسل ايقونه الزر')
    elif step == 'icon':
        temp_btn_name = message[e.sender_id]['temp_btn_name']
        button_url = message[e.sender_id]['url']
        coloer_button = message[e.sender_id]['coloer_button']
        if text == 'تخطي':
            icon = None
            done_msg = 'تم تخطي الايقونه'
        else:
            icon = None
            for entity in (e.message.entities or []):
                if isinstance(entity, MessageEntityCustomEmoji):
                    icon = entity.document_id
                    break
            if icon is None:
                return await e.reply('ارسل ايموجي مميز او اكتب تخطي!')
            done_msg = 'تم اضافة الزر'
        message[e.sender_id]['icon'] = icon
        message[e.sender_id]['buttons'].append((temp_btn_name, button_url, coloer_button, icon))
        del message[e.sender_id]['step']
        await _send(e)
        await e.reply(done_msg, buttons=buttons(e))
    elif step == 'add_channel':
        raw = e.text.strip()
        if raw.startswith('@') or raw.isdigit() or raw.startswith('https://'):
            target = raw
        else:
            return await e.reply('عذرا الايدي او اليوزر غير صحيح', buttons=back)
        try:
            chat = await ABH.get_entity(target)
        except Exception:
            return await e.reply('عذرا بس ماكدرت اوفر معلومات القناة هاي', buttons=back)
        if not chat:
            return await e.reply('عذرا بس ماكو هيج قناة', buttons=back)
        if not isinstance(chat, Channel) or not chat.broadcast:
            return await e.reply('صديقي اتفقنه تضيف قناة مو شيء اخر!', buttons=back)
        chan_key = str(chat.id)
        if not isinstance(info.get(user_key), dict):
            info[user_key] = {}
        if chan_key in info[user_key]:
            return await e.reply('عذرا بس القناة هاي ضايفها انت من قبل', buttons=back)
        try:
            bot_user = await ABH.get_me()
            participant = await ABH(GetParticipantRequest(
                channel=chat,
                participant=bot_user.id
            ))
            is_admin = isinstance(participant.participant, ChannelParticipantAdmin)
            if not is_admin:
                return await e.reply("البوت مو مشرف! ارفعه مشرف بالاول وعيد المحاولة", buttons=back)
        except UserNotParticipantError:
            return await e.reply("❌ البوت غير موجود في القناة! يرجى إضافته ورفعه مشرفاً أولاً.", buttons=back)
        owner = await get_channel_owner(chat)
        photo_file = None
        if chat.photo:
            photo_bytes = await ABH.download_profile_photo(chat, file=bytes)
            if photo_bytes:
                photo_file = BytesIO(photo_bytes)
                photo_file.name = "photo.jpg"
        current_time = datetime.now(ZoneInfo("Asia/Baghdad")).strftime("%Y-%m-%d %H:%M:%S")
        participants = await ABH.get_participants(chat, limit=0)
        members_count = participants.total
        chat_info.setdefault(user_key, {})
        chat_info[user_key][chan_key] = {
            'channel_name': chat.title,
            'owner': owner.id,
            'added_by': e.sender_id,
            'count': members_count,
            'row_text': raw,
            'at_time': current_time,
        }
        confirm_buttons = [
            Button.inline('نعم', data=f'yes:{chat.id}', style=green),
            Button.inline('لا', data=f'no:{chat.id}', style=red),
        ]
        del message[e.sender_id]['step']
        caption = (
            f"القناة ( {chat.title} )\n"
            f" مشتركينها ( {members_count} )\n"
            f" ⚙️ **هل تريد حفظ القناة؟:**"
        )
        if photo_file:
            return await e.reply(caption, file=photo_file, buttons=confirm_buttons)
        return await e.reply(caption, buttons=confirm_buttons)
    elif step == 'poll':
        if len(text) > 5:return await e.reply('لازم يكون النص اقل من 5 احرف')
        message[e.sender_id]['f_poll_name'] = text
        message[e.sender_id]['step'] = 's_poll_name'
        return await e.reply('تم اضافة نص الزر الاول\nارسل نص الزر الثاني')
    elif step == 's_poll_name':
        if len(text) > 5:return await e.reply('لازم يكون النص اقل من 5 احرف')
        message[e.sender_id]['poll'].append((message[e.sender_id]['f_poll_name'], text))
        del message[e.sender_id]['step']
        await _send(e)
        return await e.reply('تم اضافة نص الزر الثاني', buttons=buttons(e))
@ABH.on(events.CallbackQuery(pattern=r'^(yes|no|ok_delete_channle|post):(-?\d+)$'))
async def handle_yes_no(e):
    arg = e.pattern_match.group(1).decode('utf-8')
    chan_key = e.pattern_match.group(2).decode('utf-8')
    user_key = str(e.sender_id)
    if not isinstance(info.get(user_key), dict):
        info[user_key] = {}
    if arg == 'yes':
        pending = chat_info.get(user_key, {}).get(chan_key)
        if not pending:
            return await e.edit("جلسة اضافة القناة حذفت, عيد المحاولة!", buttons=back)
        if chan_key in info[user_key]:
            chat_info.get(user_key, {}).pop(chan_key, None)
            return await e.edit('القناة مضافة من قبل', buttons=back)
        info[user_key][chan_key] = pending
        await save_data()
        chat_info[user_key].pop(chan_key, None)
        if not chat_info[user_key]:
            del chat_info[user_key]
        await e.edit('تم اضافة القناة ب نجاح', buttons=back)
    elif arg == 'ok_delete_channle':
        info[user_key].pop(chan_key, None)
        await save_data()
        return await e.edit('تم حذف القناة ب نجاح', buttons=back)
    elif arg == 'post':
        if not message.get(e.sender_id, None):
            return await e.edit('ماعندك جلسة رسالة نشطة', buttons=back)
        await _send(e, int(chan_key))
        await e.edit('تم النشر ب نجاح', buttons=back)
    else:
        if chan_key not in chat_info.get(user_key, {}):
            return await e.edit("جلسة اضافة القناة انتهت, عيد المحاولة!", buttons=back)
        chat_info[user_key].pop(chan_key, None)
        if not chat_info[user_key]:
            del chat_info[user_key]
        return await e.edit('تم الغاء اضافة القناة', buttons=back)
commands = ['اضافة قناة', 'حذف قناة', 'القنوات', 'انشاء رسالة', 'نشر رسالة', 'زر']
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
