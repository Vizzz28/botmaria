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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Приветствие текстом
    await update.message.reply_text(GREETING_TEXT)
    # Если хочешь — сразу добавить аудио приветствие (если файл есть)
    if os.path.exists(PATH_GREETING_AUDIO):
        # Голосовое (как в Telegram) — reply_voice; обычный аудио-файл — reply_audio
        try:
            with open(PATH_GREETING_AUDIO, "rb") as f:
                await update.message.reply_voice(voice=f)  # или reply_audio(audio=f)
        except Exception as e:
            await update.message.reply_text(f"Не удалось отправить аудио приветствия: {e}")

async def handle_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip().lower()

    # 1) 16:00 -> фото
    if text == "16:00".lower():
        if os.path.exists(PATH_IMG_1600):
            with open(PATH_IMG_1600, "rb") as f:
                await update.message.reply_photo(photo=f, caption="16:00")
        else:
            await update.message.reply_text("Картинка для 16:00 пока не загружена.")

    # 2) 121025 -> кружочек-видео (video note)
    elif text == "121025":
        if os.path.exists(PATH_CIRCLE_121025):
            with open(PATH_CIRCLE_121025, "rb") as f:
                # video_note требует квадратное видео (будет отображаться «кружочком»)
                await update.message.reply_video_note(video_note=f)
        else:
            await update.message.reply_text("Кружочек-видео пока не загружен.")

    # 3) созвон -> видео
    elif text == "созвон":
        if os.path.exists(PATH_CALL_VIDEO):
            with open(PATH_CALL_VIDEO, "rb") as f:
                await update.message.reply_video(video=f, caption="Созвон")
        else:
            await update.message.reply_text("Видео для 'созвон' пока не загружено.")

    # 4) 1633 -> текст
    elif text == "1633":
        await update.message.reply_text(
            "В день убийства Алена вызвала полицию по адресу улица Строителей 7к1"
        )

    # 5) 02042004 -> QR-картинка
    elif text == "02042004":
        if os.path.exists(PATH_QR_02042004):
            with open(PATH_QR_02042004, "rb") as f:
                await update.message.reply_photo(photo=f, caption="QR к первому посту")
        else:
            await update.message.reply_text("QR для '02042004' пока не загружен.")

    else:
        # Мягкий ответ на неизвестный «шифр»
        await update.message.reply_text("Не знаю такой команды. Доступно: 16:00, 121025, созвон, 1633, 02042004.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_codes))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
