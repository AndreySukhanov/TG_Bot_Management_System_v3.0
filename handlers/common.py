"""
Общие обработчики для всех пользователей.
Содержит команды start, help и проверку авторизации.
"""

from aiogram import Dispatcher, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from utils.config import Config
from utils.logger import log_action
# from utils.keyboards import get_main_menu_keyboard
from utils.bot_commands import BotCommandManager
import logging

logger = logging.getLogger(__name__)


async def start_handler(message: Message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    log_action(user_id, "start", f"username: {username}")
    
    config = Config()
    user_role = config.get_user_role(user_id)
    
    if user_role == "unknown":
        await message.answer(
            "❌ У вас нет доступа к этому боту.\n"
            "Обратитесь к администратору для получения разрешений."
        )
        return
    
    role_messages = {
        "marketer": (
            "👋 Привет! Вы зарегистрированы как **Маркетолог**.\n\n"
            "📝 **Как создать заявку на оплату:**\n"
            "🆕 **Теперь поддерживается естественный язык!**\n\n"
            "**Примеры естественного языка:**\n"
            "• `Привет, мне нужно оплатить фейсбук на сотку для проекта Альфа через крипту`\n"
            "• `Нужна оплата гугл адс 50 долларов проект Бета телефон +1234567890`\n"
            "• `Оплати инстаграм 200$ проект Гамма счет 1234-5678`\n\n"
            "**Или классический формат:**\n"
            "• `Нужна оплата сервиса Facebook Ads на сумму 100$ для проекта Alpha, криптовалюта: 0x1234...abcd`\n\n"
            "ℹ️ Используйте /help для подробной справки"
        ),
        "financier": (
            "👋 Привет! Вы зарегистрированы как **Финансист**.\n\n"
            "💼 **Ваши возможности:**\n"
            "• Получение уведомлений о новых заявках на оплату\n"
            "• Подтверждение оплат командой `Оплачено [ID]`\n"
            "• Просмотр текущего баланса: /balance\n\n"
            "ℹ️ Используйте /help для подробной справки"
        ),
        "manager": (
            "👋 Привет! Вы зарегистрированы как **Руководитель**.\n\n"
            "👨‍💼 **Ваши возможности:**\n"
            "• Пополнение баланса (поддерживает естественный язык):\n"
            "  - `Added 1000$` (классический формат)\n"
            "  - `Пополнение 500`\n"
            "  - `Добавить 200 на баланс`\n"
            "• Обнуление баланса:\n"
            "  - `/resetbalance` (команда)\n"
            "  - `Обнули баланс` (естественный язык)\n"
            "• Просмотр статистики: /balance или /stats\n"
            "• AI-помощник: /ai или обычные вопросы\n"
            "• Получение уведомлений о низком балансе\n\n"
            "ℹ️ Используйте /help для подробной справки"
        )
    }
    
    await message.answer(
        role_messages[user_role], 
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Устанавливаем персональные команды для пользователя
    try:
        command_manager = BotCommandManager(message.bot)
        await command_manager.set_commands_for_user(user_id, user_role)
    except Exception as e:
        logger.error(f"Ошибка установки команд для пользователя {user_id}: {e}")


async def help_handler(message: Message):
    """Обработчик команды /help"""
    user_id = message.from_user.id
    config = Config()
    user_role = config.get_user_role(user_id)
    
    if user_role == "unknown":
        await message.answer("❌ У вас нет доступа к этому боту.")
        return
    
    help_messages = {
        "marketer": (
            "📖 **Справка для маркетолога**\n\n"
            "🆕 **Естественный язык (новая функция):**\n"
            "Теперь можно писать обычными словами!\n\n"
            "**Примеры естественного языка:**\n"
            "• `Привет, мне нужно оплатить фейсбук на сотку для проекта Альфа через крипту`\n"
            "• `Нужна оплата гугл адс 50 долларов проект Бета телефон +1234567890`\n"
            "• `Оплати инстаграм 200$ проект Гамма счет 1234-5678`\n"
            "• `Требуется оплата тикток 75$ для проекта Дельта, прикрепляю файл`\n\n"
            "**Классические форматы:**\n"
            "1. **Криптовалюта:**\n"
            "   `Нужна оплата сервиса [НАЗВАНИЕ] на сумму [СУММА]$ для проекта [ПРОЕКТ], криптовалюта: [АДРЕС_КОШЕЛЬКА]`\n\n"
            "2. **Номер телефона:**\n"
            "   `Оплата сервиса [НАЗВАНИЕ] на [СУММА]$ для проекта [ПРОЕКТ], номер телефона: [ТЕЛЕФОН]`\n\n"
            "3. **Счет/QR-код:**\n"
            "   `Оплата сервиса [НАЗВАНИЕ] на [СУММА]$ для проекта [ПРОЕКТ], счет:` + прикрепите файл\n\n"
            "**Статусы заявок:**\n"
            "• ⏳ **pending** - ожидает оплаты\n"
            "• ✅ **paid** - оплачено\n"
            "• ❌ **rejected** - отклонено\n\n"
            "**Команды:**\n"
            "• /start - главное меню\n"
            "• /help - эта справка"
        ),
        "financier": (
            "📖 **Справка для финансиста**\n\n"
            "**Подтверждение оплаты:**\n"
            "После выполнения платежа отправьте:\n"
            "`Оплачено [ID_ЗАЯВКИ]` + прикрепите подтверждение (хэш транзакции, скриншот, чек)\n\n"
            "**Примеры:**\n"
            "• `Оплачено 123` + скриншот\n"
            "• `Оплачено 124, хэш: 0xabc123...`\n\n"
            "**Команды:**\n"
            "• /start - главное меню\n"
            "• /help - эта справка\n"
            "• /balance - текущий баланс"
        ),
        "manager": (
            "📖 **Справка для руководителя**\n\n"
            "🆕 **Пополнение баланса (поддержка естественного языка):**\n\n"
            "**Классический формат:**\n"
            "• `Added 1000$`\n"
            "• `Added 500$ пополнение от клиента X`\n\n"
            "**Естественный язык:**\n"
            "• `Пополнение 1000`\n"
            "• `Добавить 500 на баланс`\n"
            "• `Закинь 200 долларов`\n"
            "• `1000$ от клиента Альфа`\n\n"
            "⚠️ **Обнуление баланса:**\n"
            "• `/resetbalance` - команда обнуления\n"
            "• `Обнули баланс` - естественный язык\n"
            "• `Очисти баланс` - естественный язык\n"
            "• `Баланс 0` - естественный язык\n\n"
            "**Уведомления:**\n"
            "Бот автоматически уведомляет о балансе ниже 100$\n\n"
            "**Команды:**\n"
            "• /start - главное меню\n"
            "• /help - эта справка\n"
            "• /balance или /stats - статистика и баланс\n"
            "• /ai - AI-помощник для аналитики\n"
            "• /resetbalance - обнуление баланса"
        )
    }
    
    await message.answer(help_messages[user_role], parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())


async def unauthorized_handler(message: Message):
    """Обработчик для неавторизованных пользователей"""
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    log_action(user_id, "unauthorized_access", f"username: {username}")
    
    await message.answer(
        "❌ У вас нет доступа к этому боту.\n"
        "Обратитесь к администратору для получения разрешений."
    )


async def default_handler(message: Message):
    """Обработчик по умолчанию для всех необработанных сообщений"""
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    logger.info(f"Необработанное сообщение от {user_id} ({username}): {message.text}")
    
    config = Config()
    role = config.get_user_role(user_id)
    
    if role == "unknown":
        await unauthorized_handler(message)
        return
    
    # Для авторизованных пользователей
    role_names = {
        "marketer": "маркетолог",
        "financier": "финансист", 
        "manager": "руководитель"
    }
    
    await message.answer(
        f"🤖 Привет, {role_names.get(role, 'пользователь')}!\n\n"
        f"Я не понимаю команду: «{message.text}»\n\n"
        f"**Доступные команды:**\n"
        f"• /help - справка\n"
        f"• /menu - главное меню\n"
        f"• /start - начало работы\n\n"
        f"Или используйте кнопки меню.",
        parse_mode="Markdown"
    )


def setup_common_handlers(dp: Dispatcher):
    """Регистрация общих обработчиков"""
    dp.message.register(start_handler, Command("start"))
    dp.message.register(help_handler, Command("help"))
    
    # Проверка авторизации для всех остальных сообщений
    def is_authorized(message: Message) -> bool:
        return Config.is_authorized(message.from_user.id)
    
    # Обработчик по умолчанию для ВСЕХ необработанных сообщений (ПОСЛЕДНИЙ!)
    dp.message.register(default_handler)
    
    logger.info("✓ Обработчики common зарегистрированы")    