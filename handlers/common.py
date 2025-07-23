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
            "👋 Привет! Вы зарегистрированы как <b>Маркетолог</b>.\n\n"
            "📝 <b>Как создать заявку на оплату:</b>\n"
            "🆕 <b>Теперь поддерживается естественный язык!</b>\n\n"
            "<b>Примеры естественного языка:</b>\n"
            "• <code>Привет, мне нужно оплатить фейсбук на сотку для проекта Альфа через крипту</code>\n"
            "• <code>Нужна оплата гугл адс 50 долларов проект Бета телефон +1234567890</code>\n"
            "• <code>Оплати инстаграм 200$ проект Гамма счет 1234-5678</code>\n\n"
            "<b>Или классический формат:</b>\n"
            "• <code>Нужна оплата сервиса Facebook Ads на сумму 100$ для проекта Alpha, криптовалюта: 0x1234...abcd</code>\n\n"
            "ℹ️ Используйте /help для подробной справки"
        ),
        "financier": (
            "👋 Привет! Вы зарегистрированы как <b>Финансист</b>.\n\n"
            "💼 <b>Ваши возможности:</b>\n"
            "• Получение уведомлений о новых заявках на оплату\n"
            "• Подтверждение оплат командой <code>Оплачено [ID]</code>\n"
            "• Просмотр текущего баланса: /balance\n\n"
            "ℹ️ Используйте /help для подробной справки"
        ),
        "manager": (
            "👋 Привет! Вы зарегистрированы как <b>Руководитель</b>.\n\n"
            "👨‍💼 <b>Ваши возможности:</b>\n"
            "• Пополнение баланса (поддерживает естественный язык):\n"
            "  - <code>Added 1000$</code> (классический формат)\n"
            "  - <code>Пополнение 500</code>\n"
            "  - <code>Добавить 200 на баланс</code>\n"
            "• Обнуление баланса:\n"
            "  - <code>/resetbalance</code> (команда)\n"
            "  - <code>Обнули баланс</code> (естественный язык)\n"
            "• Просмотр статистики: /balance или /stats\n"
            "• AI-помощник: /ai или обычные вопросы\n"
            "• Получение уведомлений о низком балансе\n\n"
            "ℹ️ Используйте /help для подробной справки"
        )
    }
    
    await message.answer(
        role_messages[user_role], 
        parse_mode="HTML",
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
            "📖 <b>Справка для маркетолога</b>\n\n"
            "🆕 <b>Естественный язык (новая функция):</b>\n"
            "Теперь можно писать обычными словами!\n\n"
            "<b>Примеры естественного языка:</b>\n"
            "• <code>Привет, мне нужно оплатить фейсбук на сотку для проекта Альфа через крипту</code>\n"
            "• <code>Нужна оплата гугл адс 50 долларов проект Бета телефон +1234567890</code>\n"
            "• <code>Оплати инстаграм 200$ проект Гамма счет 1234-5678</code>\n"
            "• <code>Требуется оплата тикток 75$ для проекта Дельта, прикрепляю файл</code>\n\n"
            "<b>Классические форматы:</b>\n"
            "1. <b>Криптовалюта:</b>\n"
            "   <code>Нужна оплата сервиса [НАЗВАНИЕ] на сумму [СУММА]$ для проекта [ПРОЕКТ], криптовалюта: [АДРЕС_КОШЕЛЬКА]</code>\n\n"
            "2. <b>Номер телефона:</b>\n"
            "   <code>Оплата сервиса [НАЗВАНИЕ] на [СУММА]$ для проекта [ПРОЕКТ], номер телефона: [ТЕЛЕФОН]</code>\n\n"
            "3. <b>Счет/QR-код:</b>\n"
            "   <code>Оплата сервиса [НАЗВАНИЕ] на [СУММА]$ для проекта [ПРОЕКТ], счет:</code> + прикрепите файл\n\n"
            "<b>Статусы заявок:</b>\n"
            "• ⏳ <b>pending</b> - ожидает оплаты\n"
            "• ✅ <b>paid</b> - оплачено\n"
            "• ❌ <b>rejected</b> - отклонено\n\n"
            "<b>Команды:</b>\n"
            "• /start - главное меню\n"
            "• /help - эта справка"
        ),
        "financier": (
            "📖 <b>Справка для финансиста</b>\n\n"
            "<b>Подтверждение оплаты:</b>\n"
            "После выполнения платежа отправьте:\n"
            "<code>Оплачено [ID_ЗАЯВКИ]</code> + прикрепите подтверждение (хэш транзакции, скриншот, чек)\n\n"
            "<b>Примеры:</b>\n"
            "• <code>Оплачено 123</code> + скриншот\n"
            "• <code>Оплачено 124, хэш: 0xabc123...</code>\n\n"
            "<b>Команды:</b>\n"
            "• /start - главное меню\n"
            "• /help - эта справка\n"
            "• /balance - текущий баланс"
        ),
        "manager": (
            "📖 <b>Справка для руководителя</b>\n\n"
            "🆕 <b>Пополнение баланса (поддержка естественного языка):</b>\n\n"
            "<b>Классический формат:</b>\n"
            "• <code>Added 1000$</code>\n"
            "• <code>Added 500$ пополнение от клиента X</code>\n\n"
            "<b>Естественный язык:</b>\n"
            "• <code>Пополнение 1000</code>\n"
            "• <code>Добавить 500 на баланс</code>\n"
            "• <code>Закинь 200 долларов</code>\n"
            "• <code>1000$ от клиента Альфа</code>\n\n"
            "⚠️ <b>Обнуление баланса:</b>\n"
            "• <code>/resetbalance</code> - команда обнуления\n"
            "• <code>Обнули баланс</code> - естественный язык\n"
            "• <code>Очисти баланс</code> - естественный язык\n"
            "• <code>Баланс 0</code> - естественный язык\n\n"
            "<b>Уведомления:</b>\n"
            "Бот автоматически уведомляет о балансе ниже 100$\n\n"
            "<b>Команды:</b>\n"
            "• /start - главное меню\n"
            "• /help - эта справка\n"
            "• /balance или /stats - статистика и баланс\n"
            "• /ai - AI-помощник для аналитики\n"
            "• /resetbalance - обнуление баланса"
        )
    }
    
    await message.answer(help_messages[user_role], parse_mode="HTML", reply_markup=ReplyKeyboardRemove())


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
    role_emojis = {
        "marketer": "📱",
        "financier": "💰", 
        "manager": "👨‍💼"
    }
    
    # Формируем список команд для каждой роли
    commands_text = ""
    if role == "manager":
        commands_text = (
            "• /start - 🏠 Главное меню\n"
            "• /help - 📋 Справка и помощь\n"
            "• /balance - 💰 Показать баланс\n"
            "• /stats - 📊 Статистика системы\n"
            "• /ai - 🤖 AI-помощник для аналитики\n"
            "• /dashboard - 📊 Веб-дашборд аналитики\n"
            "• /resetbalance - ⚠️ Обнулить баланс"
        )
    elif role == "financier":
        commands_text = (
            "• /start - 🏠 Главное меню\n"
            "• /help - 📋 Справка и помощь\n"
            "• /balance - 💰 Показать баланс"
        )
    elif role == "marketer":
        commands_text = (
            "• /start - 🏠 Главное меню\n"
            "• /help - 📋 Справка и помощь\n"
            "• /examples - 📝 Примеры создания заявок\n"
            "• /formats - 📋 Поддерживаемые форматы\n"
            "• /natural - 🗣️ Примеры естественного языка"
        )
    else:
        commands_text = (
            "• /start - 🏠 Главное меню\n"
            "• /help - 📋 Справка и помощь"
        )
    
    await message.answer(
        f"{role_emojis.get(role, '❓')} <b>Команда не распознана:</b> <code>{message.text}</code>\n\n"
        f"<b>Доступные команды:</b>\n"
        f"{commands_text}\n\n"
        f"Или используйте команды из меню.",
        parse_mode="HTML"
    )


def setup_common_handlers(dp: Dispatcher):
    """Регистрация общих обработчиков"""
    dp.message.register(start_handler, Command("start"))
    dp.message.register(help_handler, Command("help"))
    
    # Проверка авторизации для всех остальных сообщений
    def is_authorized(message: Message) -> bool:
        return Config.is_authorized(message.from_user.id)
    
    # Обработчик по умолчанию для текстовых сообщений (ПОСЛЕДНИЙ!)
    # Исключаем голосовые, фото, видео и другие медиа
    dp.message.register(default_handler, F.content_type.in_({"text"}))
    
    logger.info("✓ Обработчики common зарегистрированы")
