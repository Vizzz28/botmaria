import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Пути к файлам
ASSETS = "assets"
PATH_IMG_1600 = os.path.join(ASSETS, "img_1600.jpg")
PATH_CIRCLE_121025 = os.path.join(ASSETS, "circle_121025.mp4")   # видео для video note
PATH_CALL_VIDEO = os.path.join(ASSETS, "call_video.mp4")
PATH_QR_02042004 = os.path.join(ASSETS, "qr_02042004.png")
PATH_GREETING_AUDIO = os.path.join(ASSETS, "greeting_audio.ogg")  # опционально

GREETING_TEXT = "Умная система Сыщик Щуки (модель СЩ001) готова помочь в расследовании"


def _is_nonempty_file(path: str) -> bool:
    """True, если файл существует и размер > 0."""
    try:
        return os.path.exists(path) and os.path.getsize(path) > 0
    except Exception:
        return False


async def _send_or_placeholder(
    update: Update,
    path: str,
    send_coroutine,            # функция отправки: lambda f: update.message.reply_*(...)
    caption: str | None = None
):
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
            # Если при отправке упали — всё равно отправим плейсхолдер с описанием
            await update.message.reply_text(
                f"тут должен быть файл {filename}, а пока ЫЫЫ (ошибка отправки: {e})"
            )
            return
    # Файл отсутствует или пустой
    await update.message.reply_text(f"тут должен быть файл {filename}, а пока ЫЫЫ")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Приветствие текстом
    await update.message.reply_text(GREETING_TEXT)

    # Приветствие-аудио (если файл есть и не пустой) — голосовое пузырём
    await _send_or_placeholder(
        update,
        PATH_GREETING_AUDIO,
        send_coroutine=lambda f, **kw: update.message.reply_voice(voice=f, **kw),
        caption=None
    )


async def handle_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip().lower()

    # 1) 16:00 -> фото
    if text == "16:00":
        await _send_or_placeholder(
            update,
            PATH_IMG_1600,
            send_coroutine=lambda f, **kw: update.message.reply_photo(photo=f, **kw),
            caption="16:00"
        )

    # 2) 121025 -> кружочек-видео (video note). Если нужно обычное видео — смени на reply_video
    elif text == "121025":
        await _send_or_placeholder(
            update,
            PATH_CIRCLE_121025,
            send_coroutine=lambda f, **kw: update.message.reply_video_note(video_note=f, **kw),
            caption=None
        )

    # 3) созвон -> видео
    elif text == "созвон":
        await _send_or_placeholder(
            update,
            PATH_CALL_VIDEO,
            send_coroutine=lambda f, **kw: update.message.reply_video(video=f, **kw),
            caption="Созвон"
        )

    # 4) 1633 -> текст
    elif text == "1633":
        await update.message.reply_text(
            "В день убийства Алена вызвала полицию по адресу улица Строителей 7к1"
        )

    # 5) 02042004 -> QR-картинка
    elif text == "02042004":
        await _send_or_placeholder(
            update,
            PATH_QR_02042004,
            send_coroutine=lambda f, **kw: update.message.reply_photo(photo=f, **kw),
            caption="QR к первому посту"
        )

    else:
        # Мягкий ответ на неизвестный «шифр»
        await update.message.reply_text(
            "Не знаю такой команды. Доступно: 16:00, 121025, созвон, 1633, 02042004."
        )


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_codes))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
