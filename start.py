from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import MessageEntityCustomEmoji
from telethon.tl.types import ChannelParticipantAdmin
from telethon.errors import UserNotParticipantError
from telethon.tl.types import Channel
from num2words import num2words
from datetime import datetime
from zoneinfo import ZoneInfo
import re, asyncio, os, json
from telethon import events
from io import BytesIO
from helpers import *
from client import *
info = create('info.json')
msg = create('message.json')
not_allowed = ['الفويسات', 'الستيكرات', 'الفويس نوت', 'المتحركات']
_me = []
def save_data():
    try:
        with open('info.json', 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        return False
def save_msg():
    try:
        with open('message.json', 'w', encoding='utf-8') as f:
            json.dump(msg, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        return False
back = [Button.inline('الرجوع', data='back', style=red, icon=5258130763148172425)]
_back = [Button.inline('أظهار الازرار', data='_back', style=green, icon=5974047570249387560)]
@ABH.on(events.NewMessage)
async def is_user_check(e):
    await is_user(e)
    await small_filter(e)
@ABH.on(events.CallbackQuery)
async def _(e):
    await is_user(e)
    if not _me:
        me = await ABH.get_me()
        _me.append(me)
    else:
        me = _me
    key = f"banned_users:{me.id}"
    user_id = e.sender_id
    if r.sismember(key, user_id):
        await e.reply('عذرا صديقي انت محظور من البوت \n تفضل راسل المطور لرفع الحظر @k_4x1')
        raise events.StopPropagation
def start_button(e):
    button = []
    if str(e.sender_id) in info and info[str(e.sender_id)].keys():
        button.append([Button.inline('القنوات', data='channels', style=blue, icon=5188311512791393083)])
        button.append([Button.inline('حذف قناة', data='remove_channel', style=red, icon=5258130763148172425)])
        button[1].append(Button.inline('اضف قناة', data='add_channel', style=green, icon=5280993797482750213))
    button.append([Button.inline('الرسائل المحفوظة', data="post_message", style=blue, icon=5328162777594868795), Button.inline('انشاء رسالة', data="create_message", style=blue, icon=5222040745665379997)])
    return button
wfffp_button =[
    Button.inline('عدد المستخدمين', data='users_count', style=blue, icon=5305355874187880345),
    Button.inline('المحظورين', data='banned_users', style=blue, icon=5305355874187880345),
    Button.inline('حظر شخص', data='ban_user', style=red, icon=5305355874187880345),
    Button.inline('الغاء حظر شخص', data='un_ban_user', style=green, icon=5305355874187880345),
]
chunked_button = chunk_list(wfffp_button)
chunked_button.append(_back)
back_to_button = [Button.inline('ارجع للازرار', data='back_button', style=red, icon=5305355874187880345)]
@ABH.on(events.NewMessage(pattern=r'^/start'))
async def start(e):
    if e.sendera_id == wfffp:return await send(e, 'اهلا عزيزي ابن هاشم , شنو تحب تسوي', buttons=chunked_button)
    await send(e, f'اهلا عزيزي ( {await ment(e)} ) اني بوت مال ازرار استخدامي سهل و بسيط', buttons=start_button(e))
ban_and_unban = {}
@ABH.on(events.CallbackQuery(pattern=b'^(users_count|banned_users|ban_user|un_ban_user|back_button)$'))
async def wfffp_callback(e):
    if e.sender_id != wfffp:return
    data = e.data.decode('utf-8')
    if not _me:
        me = await ABH.get_me()
        _me.append(me)
    else:
        me = _me
    key = f"users:{me.id}"
    users_count = r.scard(key)
    if data == 'users_count':return await e.edit(f'عدد مستخدمين البوت هو ( {users_count} )', buttons=back_to_button)
    elif data == "banned_users":
        mention = [f"( {await ment(id)} ) - ( `{id}` )" for id in r.smembers(key)]
        await e.edit(f"المستخدمين المحظورين:\n {'\n'.join(mention)}")
    elif data == 'back_button':await e.edit('تفضل ابنل الهاش', buttons=chunked_button)
    else:
        ban_and_unban[e.sender_id] = data
        await e.edit('ارسل الان ايدي او يوزر المستخدم', buttons=back_to_button)
message = {}
async def return_names(ids):
    return await ABH.get_entity(list(ids))
@ABH.on(events.CallbackQuery(pattern='(add|remove)_channel|channels|create_message|_back'))
async def start_callback(e):
    data = e.data.decode('utf-8')
    id = str(e.sender_id)
    if data == 'channels':
        if not id in info:return await e.edit('عذرا بس انت ماعندك قنوات مضافة', buttons=_back)
        text = 'قنواتك المضافة🗒️:\n'
        ids = []
        for ch in info[id]:
            ids.append(int(ch))
        chats = await return_names(ids)
        row_names = [
    f"القناة {ordinal_arabic_female(num) or num2words(num, lang='ar')} - "
    f"{f'( [{chat.title}](https://t.me/{chat.username}) )' if chat and chat.username else chat.title} "
    f"- (`{chat.id}`)"
    for num, chat in enumerate(chats, start=1)]
        text += '\n'.join(row_names)
        buttons = [Button.url(chat.title, f'https://t.me/{chat.username}' if chat and chat.username else f'https://t.me/c/{str(chat.id).replace("-100", "")}/1', icon=5877700484453634587, style=blue) for chat in chats]
        buttons = chunk_list(buttons, 2)
        buttons.append(_back)
        return await e.edit(text, buttons=buttons)
    elif data.startswith('add'):
        message.setdefault(e.sender_id, {})['step'] = data
        await e.edit('ارسل الان يوزر او ايدي القناة', buttons=_back)
    elif data == 'create_message':
        id = e.sender_id
        if id not in message:
            message[id] = {'text': [], 'media': [], 'buttons': [], 'poll': []}
        if message.get(id).get('post_num'):
            del message[id]['post_num']
        await send(e, 'اهلا عزيزي وين تحب نبدي', buttons=buttons(e), edit=True)
    elif data == '_back':
        if message.get(id):del message[id]['step']
        await e.edit('تفضل اختر من بين الازرار🌚', buttons=start_button(e))
    else:
        if not id in info or not info[id].keys():return await e.edit('عذرا بس انت ماعندك قنوات مضافة🌚', buttons=_back)
        ids = list(int(id) for id in info.get(id).keys())
        chats = await return_names(ids)
        row_button = [Button.inline(ch.title, data=f"ok_delete_channle:{ch.id}", style=red, icon=5258130763148172425) for ch in chats]
        button = chunk_list(row_button, 2)
        button.append(_back)
        await e.edit('اختر قناة لحذفها', buttons=button)
arg = {'text': 'ارسل الان النص', 'media': 'ارسل الان الميديا', 'buttons': 'يمكنك اضافة الزر ومعلوماته كالاتي\n `النص-https://t.me/wfffp-اللون-الايقونة` او ارسال كل معلومه على فراد\n امثله `ابن هاشم - https://t.me/wfffp - شفاف - تخطي` \n `ابن هاشم -https://t.me/wfffp - اخضر-🌚`\n ```الاسم: هو الاسم الذي يوضع بالزر ( 8 احرف او اقل )\n``````الرابط: هو محتوى الزر عند الضغط\n``````اللون: هو لون الزر والالوان المتاحه هي \n ( احمر اخضر ازرق شفاف ) ```الايقونه: هي الايموجي الذي يوضع داخل الزر ( للمستخدمين المميزين فقط! ) \n يمكنك تخطي الايقونه عبر كتابه تخطي\n```\n```\n مثلا ارسال اسم الزر وبعدها الرابط وبعدها الايقونه', 'poll': "ارسل الان نص (اقل من 8 احرف)"}
def buttons(e):
    id = e.sender_id
    if id not in message:
        message[id] = {'text': [], 'media': [], 'buttons': [], 'poll': []}
    session = message.get(e.sender_id) or {}
    text = session.get('text') or []
    media = session.get('media') or []
    button = session.get('buttons') or []
    poll = session.get('poll') or []
    post_num = session.get('post_num') or None
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
                Button.inline('إضافة تصويت', data='set_poll', icon=5280993797482750213, style=green if poll else blue)])
        else:
            rows.append([
                Button.inline('إضافة زر', data='set_buttons', icon=5280993797482750213, style=green if button else blue)])
    if any(session.values()):
        rows.append([
            Button.inline('حذف الكل', data='del_all', icon=5465665476971471368, style=red),
            Button.inline('تعديل معين', data='delete', icon=5229113891081956317, style=blue),
                ])
        if str(e.sender_id) in info and info[str(e.sender_id)].keys():
            if not post_num:
                rows.append([
                    Button.inline('تم', data='done', icon=5429501538806548545, style=green),
                    Button.inline('حفظ الرسالة', data='save_message', icon=5242683801598967626, style=green),
                    ])
            else:
                rows.append([
                    Button.inline('تم', data='done', icon=5429501538806548545, style=green),
                    Button.inline('حذف الرسالة', data=f'delete_message:{post_num}', icon=5408832111773757273, style=red),
                    ])
    rows.append(_back)
    return rows
@ABH.on(events.NewMessage(pattern=r'^/create_message|انشاء رسالة$'))
async def create_message(e):
    id = e.sender_id
    if id not in message:
        message[id] = {'text': [], 'media': [], 'buttons': [], 'poll': []}
    await send(e, 'اهلا عزيزي وين تحب نبدي', buttons=buttons(e))
@ABH.on(events.CallbackQuery(pattern=r'^(?:(set|del|edit)_|done|back|delete|post_message)'))
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
    elif data == 'post_message':
        if not msg.get(str(e.sender_id)):return await e.edit('ماعندك رسالة محفوظة!!', buttons=[_back[0], Button.inline('انشاء رسالة', data="create_message", style=blue, icon=5222040745665379997)])
        b = [Button.inline(str(num), data=f'post_num:{num}', style=blue, icon=5242683801598967626) for num in msg[str(e.sender_id)]]
        _b = chunk_list(b, 2)
        _b.append(_back)
        return await e.edit('اختر الان بين الازرار لنشر الرسالة', buttons=_b)
    if not e.sender_id in message:
        return await e.edit('جلسة انشاء الرساله حذفت , اعد المحاولة', buttons=back)
    if data == 'del_all':
        del message[e.sender_id]
        return await e.edit('تم حذف الجلسة', buttons=back)
    if data == 'delete':
        text = session.get('text')
        media = session.get('media')
        row_buttons = session.get('buttons')
        row_poll = session.get('poll')
        if not any(session.values()):return await e.reply('بعدك ما ضفت شيء حته تحذف ', buttons=back)
        button = []
        if text:
            button.append(Button.inline('تعديل النص', data='edit_text', style=red, icon=5229113891081956317))
        if media:
            button.append(Button.inline('تعديل الميديا', data='edit_media', style=red, icon=5229113891081956317))
        if row_buttons:
            button.append(Button.inline('تعديل الازرار', data='edit_buttons', style=red, icon=5229113891081956317))
        if row_poll:
            button.append(Button.inline('حذف التصويت', data='edit_poll', style=red, icon=5408832111773757273))
        return await e.reply(f'اختر ما تريد حذفه \n عدد النصوص ( `{len(text)}` )\n عدد الميديا ( `{len(media)}` )\n عدد الأزرار ( `{len(row_buttons)}` ) \n حالة التصويت ( {"شغال" if row_poll else 'معطل'} )', buttons=button)
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
        b = [Button.inline(chat.title, data=f'post:{chat.id}', style=blue, icon=5305355874187880345) for chat in chats]
        button = chunk_list(b, 2)
        button.append(_back)
        await e.edit("اختار قناة للنشر فيها", buttons=button)
async def callback_handler(e, data):
    session = message.get(e.sender_id)
    if data == 'text':
        text = session.get('text')
        await e.edit('اضغط على ازرار النص للتخصيص', buttons=back)
        for num, item in enumerate(text, start=0):
            b = [
                Button.inline('تغيير النص', data=f'text_change:{num}:{len(message[e.sender_id]['text'])}', style=blue, icon=5264727218734524899),
                Button.inline('حذف النص', data=f'text_delete:{num}:{len(message[e.sender_id]['text'])}', style=blue, icon=5465665476971471368)]
            await e.reply(item, buttons=b)
    elif data == 'media':
        media = session.get('media')
        await e.edit('اضغط على ازرار الفيديو للتخصيص', buttons=back)
        for num, item in enumerate(media, start=0):
            b = [
                Button.inline('تغيير الفيديو', data=f'media_change:{num}:{len(message[e.sender_id]['media'])}', style=blue, icon=5264727218734524899),
                Button.inline('حذف الفيديو', data=f'media_delete:{num}:{len(message[e.sender_id]['media'])}', style=blue, icon=5465665476971471368)]
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
                Button.inline('تعديل الزر', data=f'buttons_change:{num}:{len(message[e.sender_id]['buttons'])}', style=blue, icon=5264727218734524899),
                Button.inline('حذف الزر', data=f'buttons_delete:{num}:{len(message[e.sender_id]['buttons'])}', style=blue, icon=5465665476971471368),
                back[0]]
            buttons_to_send.append(b)
            await e.respond(f"**معلومات الزر**\n نص الزر ( {name} )\n الرابط ( {url} )\n لون الزر ( {coloer if coloer else 'شفاف'} )\n الأيقونة ( {icon if icon else 'بدون أيقونة'} )", buttons=formatted_buttons)
    elif data == 'poll':
        if not session.get('poll'):return await e.edit('التصويت معطل من قبل!')
        session['poll'] = []
        return await e.edit('تم تعطيل التصويت')
@ABH.on(events.CallbackQuery(pattern=r'(post_num|delete_message):'))
async def final_callback2(e):
    arg, num = e.data.decode('utf-8').split(':')
    id = e.sender_id
    if arg == "post_num":
        if str(id) not in msg:return await e.edit('عذرا صديقي انت ماعندك رساله محفوظة', buttons=_back)
        if not message.get(id):
            message[id] = msg.get(str(id)).get(num)
        message[id]['post_num'] = num  
        await e.edit('تم اظهار المعاينة في بدايه المحادثه')
        await _send(e)
        return await e.respond("هل تريد تعديل شيء معين؟", buttons=buttons(e))
    else:
        if not msg.get(str(id)) or not msg.get(str(id), {}).get(num):return await e.edit('ماتكدر تحذف الرسالة هاي لان اصلا مو مخزنة', buttons=back)
        del msg[str(id)][num]
        if message.get(id).get('post_num'):
            del message[id]['post_num']
        save_msg()
        return await e.edit('تم حذف الرسالة من الرسائل المحفوظة👍', buttons=back)
translate = {"media": 'الميديا', 'buttons': 'الزر', 'text': 'النص'}
@ABH.on(events.CallbackQuery(pattern=r'^(media|buttons|text)_(change|delete):(\d+):(\d+)$'))
async def handle_buttons_and_media(e):
    if not e.sender_id in message:
        return await e.edit('جلسة انشاء الرساله حذفت , اعد المحاولة', buttons=back)
    action_name, action_type, target_num, old_len = re.split(r'[_:]', e.data.decode('utf-8'))
    target_num = int(target_num)
    old_len = int(old_len)
    length = len(message[e.sender_id][action_name])
    if length != old_len:return await e.edit(f' صار اختلاف معين بالجلسة (ممكن حذفت شيء سابقا ب جلسة {translate[action_name]} ) \nلضمان الدقة عيد جلسة  🌚', buttons=back)
    if action_type == 'change':
        message.setdefault(e.sender_id, {})['step'] = action_name
        del message[e.sender_id][action_name][target_num]
        if message.get(e.sender_id).get('type'):
            del message[e.sender_id]['type']
        await e.edit(f'ارسل الان {translate[action_name]}', buttons=back)
    else:
        if length != old_len:
            difference = old_len - length
            target_num = difference - target_num
            if target_num < 0:
                return await e.edit('فشل معالجة العملية بسبب ان الجلسة مختلفة كليا', buttons=back)
        del message[e.sender_id][action_name][target_num]
        if message.get(e.sender_id).get('type'):
            del message[e.sender_id]['type']
        await e.edit(f'تم بنجاح حذف {translate[action_name]}', buttons=back)
DB_FILE = 'poll.json'
def save_db():
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(polldb, f, ensure_ascii=False, indent=4)
polldb = create('poll.json')
async def _send(e, chat=None):
    user_id = e.sender_id    
    if user_id not in message:
        return
    chat_id = chat if chat else e.chat_id
    session = message.get(user_id)
    if not any(session.values()):
        return None
    row_text = session.get('text') or ["BY - @itsButtonBot"]
    text = '\n'.join(row_text)
    raw_media = session.get('media', [])
    raw_buttons = session.get('buttons', [])
    row_poll = session.get('poll', [])
    formatted_buttons = []
    for item in raw_buttons:
        if len(item) == 4:
            name, url, coloer, icon = item
            formatted_buttons.append([Button.url(name, url, style=coloer, icon=icon)])
        else:
            name, url = item
            formatted_buttons.append([Button.url(name, url)])
    name1, name2 = None, None
    if row_poll:
        name1, name2 = row_poll[0]
        formatted_buttons.append([
            Button.inline(name1, data=f'poll_agree:{user_id}:0', style=green, icon=5449683594425410231),
            Button.inline(name2, data=f'poll_disagree:{user_id}:0', style=red, icon=5447183459602669338)])
        updated_poll_buttons = [
        Button.inline(name1, data=f'poll_agree:{user_id}:{e.id}', style=green, icon=5449683594425410231),
        Button.inline(name2, data=f'poll_disagree:{user_id}:{e.id}', style=red, icon=5447183459602669338),]
        formatted_buttons.append(updated_poll_buttons)
        polldb.setdefault(str(user_id), {})[str(e.id)] = {
            "options": {name1: [], name2: []},
            "names": [name1, name2]}
        save_db()
    buttons_to_send = formatted_buttons if formatted_buttons else None
    try:
        if raw_media:
            processed_media = []
            for m in raw_media:
                item = await get_input_media(m)
                if item is not None:
                    processed_media.append(item)
            if not processed_media:
                sent_msg = await ABH.send_message(chat_id, message=text, buttons=buttons_to_send)
            elif len(processed_media) == 1:
                sent_msg = await ABH.send_file(chat_id, file=processed_media[0], caption=text, buttons=buttons_to_send)
            else:
                sent_msg = await ABH.send_file(chat_id, file=processed_media, caption=text)
                if buttons_to_send:
                    sent_msg = await ABH.send_message(chat_id, message=text, buttons=buttons_to_send)
        else:
            sent_msg = await ABH.send_message(chat_id, message=text, buttons=buttons_to_send)
        return sent_msg 
    except Exception as error:
        await hint(f'error in **_send** \n session ( {session} )\n error ( {error} )')
@ABH.on(events.CallbackQuery(pattern=r'^(poll_agree|poll_disagree):([^:]+):([^:]+)$'))
async def poll_callBack(e):
    if e.is_private:return await e.answer('تكدر تستخدم الامر بعد ما تنشره')
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
            msg_text = f'تم حذف تصويتك ( {name1} )'
        else:
            if user_id in b_db:
                b_db.remove(user_id)
            a_db.append(user_id)
            msg_text = f'تم إضافة تصويتك ( {name1} )'
    else:
        if user_id in b_db:
            b_db.remove(user_id)
            msg_text = f'تم حذف تصويتك ( {name2} )'
        else:
            if user_id in a_db:
                a_db.remove(user_id)
            b_db.append(user_id)
            msg_text = f'تم إضافة تصويتك ( {name2} )'
    await e.answer(msg_text)
    b = [[Button.inline(f'{name1} ( {len(a_db)} )', data=f'poll_agree:{sender_id}:{message_id}', style=green, icon=5449683594425410231),
         Button.inline(f'{name2} ( {len(b_db)} )', data=f'poll_disagree:{sender_id}:{message_id}', style=red, icon=5447183459602669338)]]
    save_db()
    await e.edit(buttons=b)
allowed = ['الصور', 'الفيديوهات']
chat_info = {}
processed_groups = set()
async def small_filter(e):
    user_key = str(e.sender_id)
    session = message.get(e.sender_id) or {}
    if not session:return
    step = session.get('step')
    post_num = session.get('post_num', None)
    if step and post_num:
        del message[e.sender_id]['post_num']
    if not step:return
    text = e.text.strip() or None
    if text == 'انشاء رسالة':return
    if step == 'text':
        message.setdefault(e.sender_id, {}).setdefault('text', [])
        message[e.sender_id]['text'].append(text)
        await _send(e)
        await custom_emoji(e, 'تم اضافة النص ', 5469770542288478598, buttons=buttons(e))
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
                return await custom_emoji(e, f'عذرا بس ماكدر ارسل 2 من {Type} ب رسالة وحدة ', 5465665476971471368, buttons=buttons(e))
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
        if '-' in text:
            name, url, color, emoji = text.split('-')
            if len(name) > 8:return await e.reply('صديقي لازم يكون الاسم اقل من 8 احرف')
            url = url.strip()
            if not url.startswith(('http://', 'https://', 't.me', 'tg://')):
                return await e.reply('الرابط غير صالح!')
            if color not in ('احمر', 'ازرق', 'اخضر', 'شفاف'):return await e.reply(f"{' أو '.join([f'`{item}`' for item in ['احمر', 'ازرق', 'اخضر', 'شفاف']])}")
            icon = None
            if not emoji == 'تخطي':
                for entity in (e.message.entities or []):
                    if isinstance(entity, MessageEntityCustomEmoji):
                        icon = entity.document_id
                        break
                if icon is None:
                    return await e.reply('ارسل ايموجي مميز او اكتب تخطي!')
                message[e.sender_id]['buttons'].append((name, url, color, icon))
            await _send(e)
            await e.reply('تم اضافة الزر', buttons=buttons(e))
            del message[e.sender_id]['step']
        else:
            if len(text) > 8:return await e.reply('صديقي لازم يكون الاسم اقل من 8 احرف')
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
        message[e.sender_id]['buttons'].append((temp_btn_name, button_url, coloer_button, icon))
        del message[e.sender_id]['step']
        await _send(e)
        await e.reply(done_msg, buttons=buttons(e))
    elif step == 'add_channel':
        raw = e.text.strip()
        if raw.startswith('@') or raw.isdigit() or raw.startswith('https://'):
            target = raw
        else:
            return await e.reply('عذرا الايدي او اليوزر غير صحيح', buttons=_back)
        try:
            chat = await ABH.get_entity(target)
        except Exception:
            return await e.reply('عذرا بس ماكدرت اوفر معلومات القناة هاي', buttons=_back)
        if not chat:
            return await e.reply('عذرا بس ماكو هيج قناة', buttons=_back)
        if not isinstance(chat, Channel) or not chat.broadcast:
            return await e.reply('صديقي اتفقنه تضيف قناة مو شيء اخر!', buttons=_back)
        chan_key = str(chat.id)
        if not isinstance(info.get(user_key), dict):
            info[user_key] = {}
        if chan_key in info[user_key]:
            return await e.reply('عذرا بس القناة هاي ضايفها انت من قبل', buttons=_back)
        try:
            bot_user = await ABH.get_me()
            participant = await ABH(GetParticipantRequest(
                channel=chat,
                participant=bot_user.id
            ))
            is_admin = isinstance(participant.participant, ChannelParticipantAdmin)
            if not is_admin:
                return await e.reply("البوت مو مشرف! ارفعه مشرف بالاول وعيد المحاولة", buttons=_back)
        except UserNotParticipantError:
            return await e.reply("❌ البوت غير موجود في القناة! يرجى إضافته ورفعه مشرفاً أولاً.", buttons=_back)
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
        if len(text) > 8:return await e.reply('لازم يكون النص اقل من 8 احرف')
        message[e.sender_id]['f_poll_name'] = text
        message[e.sender_id]['step'] = 's_poll_name'
        return await e.reply('تم اضافة نص الزر الاول\nارسل نص الزر الثاني')
    elif step == 's_poll_name':
        if len(text) > 8:return await e.reply('لازم يكون النص اقل من 8 احرف')
        message[e.sender_id]['poll'].append((message[e.sender_id]['f_poll_name'], text))
        del message[e.sender_id]['step']
        await _send(e)
        return await e.reply('تم اضافة نص الزر الثاني', buttons=buttons(e))
    elif step == 'message_name':
        if len(text) > 8:return await e.reply('صديقي حتى تكون العملية دقيقة لازم تضيف الاسم ب اقل من 8 احرف')
        b = [Button.inline('احفظ', data=f'ok_save:{text}', style=green, icon=5469770542288478598), Button.inline('الغاء', data='unsave_message', style=red, icon=5465665476971471368)]
        return await e.reply(f'هل تريد حفظ الرسالة ب اسم ( {text} )', buttons=b)
    step = ban_and_unban.get(e.sender_id, None)
    if step in ('ban_user', 'un_ban_user'):
        text = e.text.strip()
        target = None
        if text.isdigit():
            target = int(text)
        elif text.startswith(('@', 'https://t.me/')):
            target = text            
        if not target:
            return await e.reply('⚠️ عذراً، يرجى إرسال أيدي المستخدم أو يوزره بشكل صحيح.', buttons=back_to_button)
        try:
            user = await ABH.get_entity(target)
        except Exception:
            return await e.reply('❌ عذراً، لم أتمكن من العثور على حساب هذا المستخدم.')
        if not _me:
            me = await ABH.get_me()
            _me.append(me)
        else:
            me = _me
        key = f"banned_users:{me.id}"
        user_id = user.id
        ban_and_unban.pop(e.sender_id, None)
        if step == "ban_user":
            r.sadd(key, user_id)
            return await e.reply(f'✅ تم حظر ( {await ment(user)} ) بنجاح.')
        else:
            r.srem(key, user_id)
            return await e.reply(f'✅ تم إلغاء حظر ( {await ment(user)} ) بنجاح.')
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
            return await e.edit("جلسة اضافة القناة حذفت, عيد المحاولة!", buttons=_back)
        if chan_key in info[user_key]:
            chat_info.get(user_key, {}).pop(chan_key, None)
            return await e.edit('القناة مضافة من قبل', buttons=_back)
        info[user_key][chan_key] = pending
        save_data()
        chat_info[user_key].pop(chan_key, None)
        if not chat_info[user_key]:
            del chat_info[user_key]
        return await e.edit('تم اضافة القناة بنجاح🌚', buttons=_back)
    elif arg == 'no':
        if chan_key not in chat_info.get(user_key, {}):
            return await e.edit("جلسة اضافة القناة انتهت, عيد المحاولة!", buttons=_back)
        chat_info[user_key].pop(chan_key, None)
        if not chat_info[user_key]:
            del chat_info[user_key]
        return await e.edit('تم الغاء اضافة القناة', buttons=_back)
    elif arg == 'ok_delete_channle':
        info[user_key].pop(chan_key, None)
        save_data()
        return await e.edit('تم حذف القناة ب نجاح', buttons=_back)
    elif arg == 'post':
        if not message.get(e.sender_id, None):
            return await e.edit('ماعندك جلسة رسالة نشطة', buttons=_back)
        await _send(e, int(chan_key))
        return await e.edit('تم النشر ب نجاح', buttons=_back)
@ABH.on(events.CallbackQuery(pattern=b'^(ok_save|unsave_message|save_message)'))
async def final_callback(e):
    data = e.data.decode('utf-8')
    if not message.get(e.sender_id):
        return await e.edit('الجلسة حذفت, عيد المحاولة')
    if data == 'unsave_message':
        del message[e.sender_id]['step']
        return await e.edit('تم تجاهل الحفظ')
    elif data == 'save_message':
        if not message.get(e.sender_id):
            return await e.edit('ماعندك جلسة نشطة حاليا فماتكدر تحفظ رسالة', buttons=button(e))
        message[e.sender_id]['step'] = 'message_name'
        b = [Button.inline('احفظ', data='ok_save', style=green, icon=5469770542288478598), Button.inline('الغاء', data='unsave_message', style=red, icon=5465665476971471368)]
        return await e.edit(f'سيتم حفظ الرسالة ب رقم ( {e.message_id} ) \n او ارسل اسم مخصص', buttons=b)
    elif data.startswith('ok'):
        if ':' in data:
            name = data.split(':')[1] 
        else:
            name = e.message_id
        del message[e.sender_id]['step']
        if str(e.sender_id) not in msg:
            msg[str(e.sender_id)] = {}
        msg[str(e.sender_id)][name] = message.get(e.sender_id)
        save_msg()
        b = [Button.inline('نعم', data=f'done', style=green, icon=5305355874187880345), _back[0]]
        return await e.edit('تم حفظ الرسالة هل تريد نشرها؟', buttons=b)
