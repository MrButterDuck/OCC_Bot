import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ErrorEvent, Message
from aiogram.enums.chat_type import ChatType
from aiogram import BaseMiddleware
from aiogram.filters import Command
import os
from dotenv import load_dotenv
from json_storage import JsonStorage
import traceback
from typing import Callable, Dict, Awaitable, Any

load_dotenv()

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s — %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

# Вставьте ваш API токен
API_TOKEN = os.getenv("TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Клавиатура для главного меню
main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Написать обращение")
        ],
        [
            KeyboardButton(text="Предложение или инициатива")
        ]],
    resize_keyboard=True
)

canteen_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Проживание 🛏️"),
            KeyboardButton(text="Стипендия и материальная помощь 💸")
        ],
        [
            KeyboardButton(text="Инфраструктура 🏗️"),
            KeyboardButton(text="International student 🌍")
        ],
        [
            KeyboardButton(text="Студобъединения и мероприятия 🎉"),
            KeyboardButton(text="Обучение 📚")
        ],
        [
            KeyboardButton(text="Рапорты и акты 📄"),
            KeyboardButton(text="Другое ❓")
        ],
        [
            KeyboardButton(text="Вернуться в начало 🔙")
        ]
    ],
    resize_keyboard=True
)

# Клавиатура для пропуска медиа
media_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Пропустить отправку медиа 📵")
        ],
        [
            KeyboardButton(text="Вернуться в начало 🔙")
        ]
    ],
    resize_keyboard=True
)

# Клавиатура для отправки обращения
end_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отправить обращение ✅"),
            KeyboardButton(text="Вернуться в начало 🔙")
        ]
    ],
    resize_keyboard=True
)

# Клавиатура только с кнопкой возврата
back_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Вернуться в начало 🔙")
        ]
    ],
    resize_keyboard=True
)

# Словарь для хранения данных пользователей
user_data = JsonStorage()


# Обработка чатов
class ChatFilterMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        chat = event.chat

        if chat.type == ChatType.PRIVATE:
            return await handler(event, data)

        if chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}:
            if chat.id == GROUP_ID:
                return 
            else:
                try:
                    await self.bot.leave_chat(chat.id)
                    print(f"Left unauthorized group: {chat.title} ({chat.id})")
                except Exception as e:
                    print(f"Failed to leave chat {chat.id}: {e}")
                return 

        return


dp.message.middleware(ChatFilterMiddleware(bot=bot))


# Основная команда /start
@dp.message(lambda message: message.text == 'Вернуться в начало 🔙')
async def goBack(message: types.Message):
    await send_welcome(message)


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    user_data.delete(user_id)
    user_data.set(user_id, {"stage": "main_menu"})  # Начальный этап
    await message.answer(
        "Вас приветствует Объединённый совет студентов!\n\n"
        "Здесь вы можете обратиться за помощью в трудной ситуации, с решением проблемы "
        "или за консультацией по любым вопросам, касающимся Университета.\n\n"
        "💡 Кроме того, вы можете внести предложение по любому вопросу, затрагивающему студентов.\n\n"
        "Мы рассмотрим ваше предложение или инициативу, начнём работу над ней либо дадим обратную связь "
        "и поможем с реализацией.\n\n"
        "По экстренным вопросам пишите [Герману](https://t.me/herman_east) — председателю "
        "Объединённого совета студентов.",
        reply_markup=main_menu_keyboard,
        parse_mode='Markdown'
    )


# Обработка выбора действия
@dp.message(lambda message: message.text in [
    "Написать обращение",
    "Предложение или инициатива"
])
async def handle_action_selection(message: types.Message):
    user_id = message.from_user.id
    cur_user_data = user_data.get(user_id)
    cur_user_data["action"] = message.text
    cur_user_data["stage"] = "choose_canteen"
    user_data.set(user_id, cur_user_data)
    await message.answer(
        "Пожалуйста, выберите тему:",
        reply_markup=canteen_keyboard
    )


# Обработка выбора столовой
@dp.message(lambda message: user_data.get(
        message.from_user.id, {}).get("stage") == "choose_canteen"
)
async def handle_canteen_selection(message: types.Message):
    user_id = message.from_user.id
    cur_user_data = user_data.get(user_id)
    cur_user_data["canteen"] = message.text
    cur_user_data["stage"] = "text_input"
    user_data.set(user_id, cur_user_data)
    if user_data.get(user_id)["action"] == "Написать обращение":
        await message.answer(
            "Напишите текст обращения\n\n"
            "(медиафайлы вы можете приложить в следующем шаге)",
            reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer(
            "Напишите текст предложения\n\n"
            "(медиафайлы вы можете приложить в следующем шаге)",
            reply_markup=types.ReplyKeyboardRemove())


# Обработка текста отзыва или жалобы
@dp.message(lambda message: user_data.get(
        message.from_user.id, {}).get("stage") == "text_input"
)
async def handle_text_input(message: types.Message):
    if message.photo or message.video or message.document or message.audio or message.animation:
        await message.answer(
            "Пожалуйста, сначала отправьте только текст без вложений. \n"
            "Медиафайлы можно прикрепить на следующем этапе."
        )
        return

    user_id = message.from_user.id
    cur_user_data = user_data.get(user_id)
    cur_user_data["text"] = message.text
    cur_user_data["media_files"] = []
    cur_user_data["sending_files"] = False
    cur_user_data["stage"] = "media"
    user_data.set(user_id, cur_user_data)
    await message.answer(
        "К сообщению вы можете приложить фото или видео\n\n"
        "Если вы не хотите прикладывать фото или видео - "
        "нажмите «Пропустить отправку медиа 📵» для завершения\n\n"
        "После отправки всех медиа, нужно нажать на «Отправить обращение ✅», "
        "чтобы перейти к следующему шагу",
        reply_markup=media_keyboard
    )


# Обработка отправки медиа или пропуска
@dp.message(lambda message: user_data.get(
        message.from_user.id, {}).get("stage") == "media"
)
async def handle_media(message: types.Message):
    user_id = message.from_user.id
    cur_user_data = user_data.get(user_id)
    cur_user_data["sending_files"] = True
    # Если пользователь нажал "Пропустить отправку медиа"
    if message.text in ("Пропустить отправку медиа 📵", "Отправить обращение ✅"):
        await finalize_survey(message)
        return

    if message.photo or message.video:
        file_id = (message.photo[-1].file_id if message.photo
                   else message.video.file_id)
        media_type = 'photo' if message.photo else 'video'
        print(file_id)
        if len(cur_user_data["media_files"]) < 10:
            cur_user_data["media_files"].append({
                'type': media_type,
                'file_id': file_id
            })

    if message.media_group_id:
        await asyncio.sleep(1.5)

    if len(cur_user_data["media_files"]) >= 10 and cur_user_data["sending_files"] == True:
        cur_user_data["sending_files"] = False
        await message.answer(
            "Добавлено максимальное количество файлов.\n"
            "Нажмите 'Отправить обращение ✅' для завершения.",
            reply_markup=end_keyboard
        )
    elif cur_user_data["sending_files"] == True:
        cur_user_data["sending_files"] = False
        await message.answer(
            f'Файлов добавлено: {len(cur_user_data["media_files"])}/10\n'
            "Вы можете добавить еще файлы при их наличии.",
            reply_markup=end_keyboard
        )
    user_data.set(user_id, cur_user_data)


@dp.message()
async def fallback_handler(message):
    await message.answer(
        "Упс, что-то пошло не так."
        "Попробуйте ввести /start и следовать инструкциям"
    )


@dp.error()
async def global_error_handler(event: ErrorEvent):
    error_text = (
            "⚠️ *Произошла ошибка у бота:*\n"
            f"`{type(event).__name__}: {event.exception}`\n\n"
            "*Traceback:*\n"
            f"```{traceback.format_exc()[-1500:]}```"
        )
    await bot.send_message(GROUP_ID, error_text, parse_mode="Markdown")
    return True


# Завершение опроса и отправка данных
async def finalize_survey(message: types.Message):
    user_id = message.from_user.id
    data = user_data.get(user_id)
    result_text = (
        f"Отзыв пользователя @{message.from_user.username}\n\n"
        f"Действие: {data['action']}\n"
        f"Тема: {data['canteen']}\n"
        f"Текст: {data['text']}\n"
    )

    media_group = []

    for index, file in enumerate(data["media_files"]):
        # Определяем тип файла (фото или видео)
        if file["type"] == "photo":
            media_group.append(types.InputMediaPhoto(media=file["file_id"], caption=result_text if index == 0 else None))
        elif file["type"] == "video":
            media_group.append(types.InputMediaVideo(media=file["file_id"], caption=result_text if index == 0 else None))

    # Если есть медиа, отправляем их как группу
    if media_group:
        await bot.send_media_group(chat_id=GROUP_ID, media=media_group)

    # Отправляем финальное сообщение пользователю
    await message.answer(
        "Ваше сообщение отправлено!\nМы с вами свяжемся❤",
        reply_markup=back_keyboard
    )

    # Очищаем данные пользователя
    user_data.delete(user_id)


# Функция запуска бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
