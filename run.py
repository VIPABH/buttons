import asyncio
import os
import traceback
from client import *
from start import *
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
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)    
    try:
        loop.run_until_complete(run_button())
    except KeyboardInterrupt:
        print("\nتم إيقاف البوت يدوياً.")
    except Exception:
        print(traceback.format_exc())
    finally:
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        if pending:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.close()
