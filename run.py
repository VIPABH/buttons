import asyncio
import os
from client import *
async def run_button():
    button_token = os.getenv("BUTTON_BOT")
    if not button_token:
        print("❌ خطأ: لم يتم العثور على توكن BUTTON_BOT في المتغيرات البيئية!")
        return
    try:
        await ABH.start(bot_token=button_token)
        print("✅ BUTTON_BOT يعمل الآن بنجاح!")
        await ABH.run_until_disconnected()
    except (KeyboardInterrupt, SystemExit, asyncio.CancelledError):
        pass
    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع في BUTTON_BOT: {e}")
    finally:
        print("\n🛑 جاري إغلاق بوت الأزرار...")
        if ABH.is_connected():
            await ABH.disconnect()
            print("✅ تم فصل التوصيل بنجاح.")
