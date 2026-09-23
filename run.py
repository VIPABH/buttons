from client import *
async def run_button():
    button_token = os.getenv("BUTTON_BOT")
    if not button_token:
        print("❌ خطأ: لم يتم العثور على توكن BUTTON_BOT في المتغيرات البيئية!")
        return
    await BUTTON_BOT.start(bot_token=button_token)
    print("✅ BUTTON_BOT يعمل الآن بنجاح!")
    try:
        await BUTTON_BOT.run_until_disconnected()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        print("\n🛑 جاري إغلاق بوت الأزرار...")
        if BUTTON_BOT.is_connected():
            await BUTTON_BOT.disconnect()
