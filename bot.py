from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import logging
import sqlite3

# Logging konfiguratsiyasi
logging.basicConfig(level=logging.INFO)

# Bot va dispatcherni ishga tushirish
bot = Bot(token="7353521621:AAHK_1dRQuyzW0r-5aJBggkIn9HJNOstlFY")  # Tokenni o'zgartiring
dp = Dispatcher(bot)

# Ma'lumotlar bazasini ishga tushirish
db = sqlite3.connect("db.db", check_same_thread=False)
cursor = db.cursor()


# Komanda: /start
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🔍 So'rovchi topish"))
    await message.reply(
        f"Salom, {message.from_user.first_name}! Xush kelibsiz anonim chatga! So'rovchi topish tugmasini bosing.",
        reply_markup=markup,
    )

# Komanda: /menu
@dp.message_handler(commands=["menu"])
async def menu_command(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🔍 So'rovchi topish"))
    await message.reply("📋 Menu:", reply_markup=markup)

# Komanda: /stop
@dp.message_handler(commands=["stop"])
async def stop_command(message: types.Message):
    cursor.execute("SELECT * FROM chats WHERE chat_one = ? OR chat_two = ?", (message.chat.id, message.chat.id))
    chat_info = cursor.fetchone()
    if chat_info:
        chat_one, chat_two = chat_info
        other_user = chat_two if chat_one == message.chat.id else chat_one

        # Chatni ma'lumotlar bazasidan o'chirish
        cursor.execute("DELETE FROM chats WHERE chat_one = ? OR chat_two = ?", (message.chat.id, message.chat.id))
        db.commit()

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton("🔍 So'rovchi topish"))

        await bot.send_message(other_user, "❌ So'rovchi chatni tark etdi", reply_markup=markup)
        await message.reply("❌ Siz chatni tark etdiz.", reply_markup=markup)
    else:
        await message.reply("❌ Siz chat boshlamadingiz!")

# Xabarlarni boshqarish
@dp.message_handler(content_types=["text"])
async def text_message_handler(message: types.Message):
    if message.chat.type == "private":
        if message.text == "🔍 So'rovchi topish":
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(KeyboardButton("❌ Qidiruvni to'xtatish"))

            # Mavjud suhbatdoshi borligini tekshirish
            cursor.execute("SELECT chat_id FROM queue WHERE chat_id != ?", (message.chat.id,))
            chat_two = cursor.fetchone()

            if chat_two:
                chat_two = chat_two[0]
                # Navbatdan olib tashlash va chat yaratish
                cursor.execute("DELETE FROM queue WHERE chat_id = ?", (chat_two,))
                cursor.execute("INSERT INTO chats (chat_one, chat_two) VALUES (?, ?)", (message.chat.id, chat_two))
                db.commit()

                await bot.send_message(chat_two, "🔗 So'rovchi topildi! Anonim suhbatni boshlang.")
                await message.reply("🔗 So'rovchi topildi! Anonim suhbatni boshlang.")
            else:
                # Foydalanuvchini navbatga qo'shish
                cursor.execute("INSERT OR IGNORE INTO queue (chat_id) VALUES (?)", (message.chat.id,))
                db.commit()
                await message.reply("⌛ So'rovchi kutilyapti...", reply_markup=markup)
        else:
            # Xabarni faol chatdoshi ga yuborish
            cursor.execute("SELECT * FROM chats WHERE chat_one = ? OR chat_two = ?", (message.chat.id, message.chat.id))
            chat_info = cursor.fetchone()
            if chat_info:
                chat_one, chat_two = chat_info
                recipient = chat_two if chat_one == message.chat.id else chat_one
                await bot.send_message(recipient, message.text)
            else:
                await message.reply("❌ Siz chat boshlamadingiz!")

# Qo'shimcha Funksiya 1: Faol chatorlarni ko'rish
@dp.message_handler(commands=["active_chats"])
async def active_chats(message: types.Message):
    cursor.execute("SELECT * FROM chats")
    chats = cursor.fetchall()
    if chats:
        active_chats_list = "\n".join([f"Chat {chat[0]} va {chat[1]} o'rtasida" for chat in chats])
        await message.reply(f"💬 Faol chatlar:\n{active_chats_list}")
    else:
        await message.reply("❌ Faol chatlar mavjud emas.")

# Qo'shimcha Funksiya 2: Navbatni tark etish
@dp.message_handler(commands=["leave_queue"])
async def leave_queue(message: types.Message):
    cursor.execute("DELETE FROM queue WHERE chat_id = ?", (message.chat.id,))
    db.commit()
    await message.reply("❌ Siz navbatni tark etdiz.")

# Qo'shimcha Funksiya 3: Barcha foydalanuvchilarni ko'rsatish
@dp.message_handler(commands=["queue_list"])
async def queue_list(message: types.Message):
    cursor.execute("SELECT chat_id FROM queue")
    users_in_queue = cursor.fetchall()
    if users_in_queue:
        user_list = "\n".join([str(user[0]) for user in users_in_queue])
        await message.reply(f"📝 Navbatdagi foydalanuvchilar:\n{user_list}")
    else:
        await message.reply("❌ Navbatda hech kim yo'q.")

# Qo'shimcha Funksiya 4: Barcha chatlarni o'chirish (Admin)
@dp.message_handler(commands=["delete_all_chats"])
async def delete_all_chats(message: types.Message):
    # Admin tekshiruvi (foydalanuvchi ID sini o'zgartiring)
    if message.from_user.id == 6812498519:  # Adminning user ID sini qo'yish
        cursor.execute("DELETE FROM chats")
        db.commit()
        await message.reply("✅ Barcha chatlar o'chirildi.")
    else:
        await message.reply("❌ Sizda bu komanda uchun huquq yo'q.")

# Qo'shimcha Funksiya 5: Barcha foydalanuvchilarga xabar yuborish (Admin)
@dp.message_handler(commands=["send_to_all"])
async def send_to_all(message: types.Message):
    # Admin tekshiruvi (foydalanuvchi ID sini o'zgartiring)
    if message.from_user.id == 6812498519:  # Adminning user ID sini qo'yish
        custom_message = message.text[12:]  # Komandadan keyingi matn
        cursor.execute("SELECT chat_id FROM queue")
        users_in_queue = cursor.fetchall()
        for user in users_in_queue:
            await bot.send_message(user[0], custom_message)
        await message.reply("✅ Xabar barcha foydalanuvchilarga yuborildi.")
    else:
        await message.reply("❌ Sizda bu komanda uchun huquq yo'q.")

# Botni ishga tushirish
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
