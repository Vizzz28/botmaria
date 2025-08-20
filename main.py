import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# === Пути к файлам ===
ASSETS = "assets"
PATH_IMG_1600        = os.path.join(ASSETS, "img_1600.jpg")         # скрин переписки для 16:00
PATH_CIRCLE_121025   = os.path.join(ASSETS, "circle_121025.mp4")    # кружочек-видео (video note)
PATH_CALL_VIDEO      = os.path.join(ASSETS, "call_video(1).mp4")       # допрос Львов (видео)
PATH_QR_02042004     = os.path.join(ASSETS, "qr_02042004.jpg")      # QR на первый пост
PATH_GREETING_VIDEO  = os.path.join(ASSETS, "greeting_video.mp4")   # приветственное видео

GREETING_TEXT = "Умная система Сыщик Щуки (модель СЩ001) готова помочь в расследовании"
CALL_CAPTION  = "Секретный материал. Рассказ свидетеля о видеозвонке с пострадавшей №2 в день убийства в 19:00"

# === Утилиты ===
def _is_nonempty_file(path: str) -> bool:
    """True, если файл существует и размер > 0."""
    try:
        return os.path.exists(path) and os.path.getsize(path) > 0
    except Exception:
        return False

async def _send_or_placeholder(update: Update, path: str, send_coroutine, caption: str | None = None):
    """
    Пытаемся отправить файл, иначе пишем плейсхолдер:
    'тут должен быть файл <filename>, а пока ЫЫЫ'
    """
    filename = os.path.basename(path)
    if _is_nonempty_file(path):
        try:
            with open(path, "rb") as f:
                if caption is None:
                    await send_coroutine(f)
                else:
                    await send_coroutine(f, caption=caption)
            return
        except Exception as e:
            await update.message.reply_text(
                f"тут должен быть файл {filename}, а пока ЫЫЫ (ошибка отправки: {e})"
            )
            return
    await update.message.reply_text(f"тут должен быть файл {filename}, а пока ЫЫЫ")

# === Хендлеры ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Текст приветствия
    await update.message.reply_text(GREETING_TEXT)
    # Приветственное ВИДЕО (если есть)
    await _send_or_placeholder(
        update,
        PATH_GREETING_VIDEO,
        send_coroutine=lambda f, **kw: update.message.reply_video(video=f, **kw),
        caption=None
    )

async def handle_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text_raw = update.message.text.strip()
    text = text_raw.lower()

    # 1) 16:00 -> скрин переписки (фото)
    if text == "16:00":
        await _send_or_placeholder(
            update,
            PATH_IMG_1600,
            send_coroutine=lambda f, **kw: update.message.reply_photo(photo=f, **kw),
            caption=None
        )

    # 2) 121025 -> кружочек-видео (video note).
    elif text == "121025":
        await _send_or_placeholder(
            update,
            PATH_CIRCLE_121025,
            send_coroutine=lambda f, **kw: update.message.reply_video_note(video_note=f, **kw),
            caption=None
        )

    # 3) созвон -> видео + подпись
    elif text == "созвон":
        await _send_or_placeholder(
            update,
            PATH_CALL_VIDEO,
            send_coroutine=lambda f, **kw: update.message.reply_video(video=f, **kw),
            caption=CALL_CAPTION
        )

    # 4) 1633 -> текст (адрес скрыт спойлером)
    elif text == "1633":
        await update.message.reply_text(
            "В день убийства Алена вызвала полицию по адресу ||улица Строителей 7к1||",
            parse_mode="MarkdownV2"
        )

    # 5) 02042004 -> картинка с QR
    elif text == "02042004":
        await _send_or_placeholder(
            update,
            PATH_QR_02042004,
            send_coroutine=lambda f, **kw: update.message.reply_photo(photo=f, **kw),
            caption=None
        )

    # 7) base 64 -> текст
    elif text == "base 64":
        await update.message.reply_text("Осмотрите почтовый ящик, воспользуйтесь дешифратором")

    # 8) идиот 172 -> текст (учитываем регистр и пробел)
    elif text == "идиот 172":
        await update.message.reply_text("Сама вы идиотка. Ищите в библиотеке")

    else:
        await update.message.reply_text("Это ни о чем мне не говорит.")

def main():
    print("Бот запускается (polling)…")  # лог для Railway
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_codes))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
