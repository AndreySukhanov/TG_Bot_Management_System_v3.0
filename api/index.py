from http.server import BaseHTTPRequestHandler
import json
import asyncio
import logging
import os
import sys
from urllib.parse import parse_qs

# Добавляем корневую директорию в path для импорта модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'utils'))
sys.path.insert(0, os.path.join(root_dir, 'handlers'))
sys.path.insert(0, os.path.join(root_dir, 'db'))
sys.path.insert(0, os.path.join(root_dir, 'nlp'))

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальные переменные для кеширования
bot = None
dp = None

async def init_bot():
    """Инициализация бота и диспетчера"""
    global bot, dp
    
    if bot is not None and dp is not None:
        logger.info("Бот уже инициализирован, возвращаем существующий")
        return bot, dp
    
    try:
        from aiogram import Bot, Dispatcher
        from aiogram.fsm.storage.memory import MemoryStorage
        
        # Получаем токен из переменных окружения
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            raise Exception("BOT_TOKEN не найден в переменных окружения")
        
        # Создание бота и диспетчера
        bot = Bot(token=bot_token)
        dp = Dispatcher(storage=MemoryStorage())
        
        logger.info("✓ Бот и диспетчер созданы")
        
        # Пытаемся импортировать модули по одному
        logger.info("📦 Начинаем пошаговую инициализацию...")
        
        # Шаг 1: База данных
        try:
            logger.info("1️⃣ Импортируем db.database...")
            from db.database import init_database
            logger.info("✓ db.database импортирован")
            
            logger.info("1️⃣ Инициализируем базу данных...")
            await init_database()
            logger.info("✓ База данных инициализирована")
            
        except Exception as e:
            logger.error(f"❌ Ошибка базы данных: {e}")
            raise e
        
        # Шаг 2: Импорт обработчиков
        handlers_imported = {}
        
        try:
            logger.info("2️⃣ Импортируем handlers.common...")
            from handlers.common import setup_common_handlers
            handlers_imported['common'] = setup_common_handlers
            logger.info("✓ handlers.common импортирован")
        except Exception as e:
            logger.error(f"❌ Ошибка импорта handlers.common: {e}")
            handlers_imported['common'] = None
        
        try:
            logger.info("2️⃣ Импортируем handlers.command_handlers...")
            from handlers.command_handlers import setup_command_handlers
            handlers_imported['command'] = setup_command_handlers
            logger.info("✓ handlers.command_handlers импортирован")
        except Exception as e:
            logger.error(f"❌ Ошибка импорта handlers.command_handlers: {e}")
            handlers_imported['command'] = None
        
        try:
            logger.info("2️⃣ Импортируем handlers.menu_handler...")
            from handlers.menu_handler import setup_menu_handlers
            handlers_imported['menu'] = setup_menu_handlers
            logger.info("✓ handlers.menu_handler импортирован")
        except Exception as e:
            logger.error(f"❌ Ошибка импорта handlers.menu_handler: {e}")
            handlers_imported['menu'] = None
        
        try:
            logger.info("2️⃣ Импортируем handlers.voice_handler...")
            from handlers.voice_handler import setup_voice_handlers
            handlers_imported['voice'] = setup_voice_handlers
            logger.info("✓ handlers.voice_handler импортирован")
        except Exception as e:
            logger.error(f"❌ Ошибка импорта handlers.voice_handler: {e}")
            handlers_imported['voice'] = None
        
        try:
            logger.info("2️⃣ Импортируем handlers.marketer...")
            from handlers.marketer import setup_marketer_handlers
            handlers_imported['marketer'] = setup_marketer_handlers
            logger.info("✓ handlers.marketer импортирован")
        except Exception as e:
            logger.error(f"❌ Ошибка импорта handlers.marketer: {e}")
            handlers_imported['marketer'] = None
        
        try:
            logger.info("2️⃣ Импортируем handlers.financier...")
            from handlers.financier import setup_financier_handlers
            handlers_imported['financier'] = setup_financier_handlers
            logger.info("✓ handlers.financier импортирован")
        except Exception as e:
            logger.error(f"❌ Ошибка импорта handlers.financier: {e}")
            handlers_imported['financier'] = None
        
        try:
            logger.info("2️⃣ Импортируем handlers.manager...")
            from handlers.manager import setup_manager_handlers
            handlers_imported['manager'] = setup_manager_handlers
            logger.info("✓ handlers.manager импортирован")
        except Exception as e:
            logger.error(f"❌ Ошибка импорта handlers.manager: {e}")
            handlers_imported['manager'] = None
        
        # Шаг 3: Регистрация обработчиков
        logger.info("3️⃣ Начинаем регистрацию обработчиков...")
        
        # Регистрируем только те, которые успешно импортированы
        if handlers_imported['command']:
            try:
                handlers_imported['command'](dp)
                logger.info(f"✓ Command handlers зарегистрированы ({len(dp.message.handlers)} total)")
            except Exception as e:
                logger.error(f"❌ Ошибка регистрации command handlers: {e}")
        
        if handlers_imported['voice']:
            try:
                handlers_imported['voice'](dp)
                logger.info(f"✓ Voice handlers зарегистрированы ({len(dp.message.handlers)} total)")
            except Exception as e:
                logger.error(f"❌ Ошибка регистрации voice handlers: {e}")
        
        if handlers_imported['marketer']:
            try:
                handlers_imported['marketer'](dp)
                logger.info(f"✓ Marketer handlers зарегистрированы ({len(dp.message.handlers)} total)")
            except Exception as e:
                logger.error(f"❌ Ошибка регистрации marketer handlers: {e}")
        
        if handlers_imported['financier']:
            try:
                handlers_imported['financier'](dp)
                logger.info(f"✓ Financier handlers зарегистрированы ({len(dp.message.handlers)} total)")
            except Exception as e:
                logger.error(f"❌ Ошибка регистрации financier handlers: {e}")
        
        if handlers_imported['manager']:
            try:
                handlers_imported['manager'](dp)
                logger.info(f"✓ Manager handlers зарегистрированы ({len(dp.message.handlers)} total)")
            except Exception as e:
                logger.error(f"❌ Ошибка регистрации manager handlers: {e}")
        
        if handlers_imported['menu']:
            try:
                handlers_imported['menu'](dp)
                logger.info(f"✓ Menu handlers зарегистрированы ({len(dp.message.handlers)} total)")
            except Exception as e:
                logger.error(f"❌ Ошибка регистрации menu handlers: {e}")
        
        # Common handlers - ВСЕГДА последними
        if handlers_imported['common']:
            try:
                handlers_imported['common'](dp)
                logger.info(f"✓ Common handlers зарегистрированы ({len(dp.message.handlers)} total)")
            except Exception as e:
                logger.error(f"❌ Ошибка регистрации common handlers: {e}")
        
        # Финальная проверка
        final_handlers = len(dp.message.handlers)
        logger.info(f"🎯 ИТОГО ЗАРЕГИСТРИРОВАНО MESSAGE HANDLERS: {final_handlers}")
        
        if final_handlers == 0:
            logger.error("❌ НЕ ЗАРЕГИСТРИРОВАНО НИ ОДНОГО MESSAGE HANDLER!")
            logger.info("🆘 Добавляем минимальный набор обработчиков...")
            await add_minimal_handlers(dp)
        else:
            # Выводим список всех обработчиков
            for i, handler in enumerate(dp.message.handlers):
                handler_name = handler.callback.__name__
                logger.info(f"  📝 Handler {i}: {handler_name}")
        
        # Шаг 4: Команды бота (опционально)
        try:
            logger.info("4️⃣ Импортируем utils.bot_commands...")
            from utils.bot_commands import BotCommandManager
            logger.info("✓ utils.bot_commands импортирован")
            
            logger.info("4️⃣ Настраиваем команды бота...")
            command_manager = BotCommandManager(bot)
            await command_manager.setup_commands()
            logger.info("✓ Команды бота настроены")
        except Exception as e:
            logger.error(f"❌ Ошибка настройки команд (не критично): {e}")
        
        logger.info("🎉 ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        return bot, dp
        
    except Exception as e:
        logger.error(f"💥 КРИТИЧЕСКАЯ ОШИБКА ИНИЦИАЛИЗАЦИИ: {e}")
        logger.error(f"Тип ошибки: {e.__class__.__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Создаем базовый бот с аварийным обработчиком
        if bot is None:
            bot = Bot(token=os.getenv("BOT_TOKEN"))
            dp = Dispatcher(storage=MemoryStorage())
            await add_emergency_handler(dp)
        
        return bot, dp

async def add_minimal_handlers(dp):
    """Добавляет минимальный набор обработчиков"""
    from aiogram import types
    from aiogram.filters import Command
    
    async def minimal_start(message: types.Message):
        await message.reply("🤖 Бот запущен в минимальном режиме. Некоторые функции недоступны.")
    
    async def minimal_help(message: types.Message):
        await message.reply("ℹ️ Справка временно недоступна. Бот работает в ограниченном режиме.")
    
    async def minimal_default(message: types.Message):
        await message.reply("🤖 Бот в ограниченном режиме. Используйте /start")
    
    dp.message.register(minimal_start, Command("start"))
    dp.message.register(minimal_help, Command("help"))
    dp.message.register(minimal_default)
    
    logger.info("✓ Минимальные обработчики добавлены")

async def add_emergency_handler(dp):
    """Добавляет базовый обработчик в случае ошибки инициализации"""
    from aiogram import types
    
    async def emergency_handler(message: types.Message):
        """Аварийный обработчик"""
        await message.reply("🤖 Бот временно работает в ограниченном режиме. Используйте /start")
    
    dp.message.register(emergency_handler)
    logger.info("✓ Аварийный обработчик зарегистрирован")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Обработка GET запросов"""
        try:
            logger.info(f"GET запрос: {self.path}")
            
            # Health check
            if self.path in ['/', '/health']:
                response = {
                    "status": "ok", 
                    "bot": "running",
                    "webhook": "active"
                }
                self._send_response(200, response)
                return
            
            # Установка webhook
            if self.path == '/set_webhook':
                result = asyncio.run(self._set_webhook())
                self._send_response(200, result)
                return
            
            # Информация о webhook
            if self.path == '/webhook_info':
                result = asyncio.run(self._get_webhook_info())
                self._send_response(200, result)
                return
            
            # 404 для остальных путей
            self._send_response(404, {"error": "Not found", "path": self.path})
            
        except Exception as e:
            logger.error(f"Ошибка GET запроса: {e}")
            self._send_response(500, {"error": str(e)})
    
    def do_POST(self):
        """Обработка POST запросов"""
        try:
            logger.info(f"POST запрос: {self.path}")
            
            # Webhook endpoint
            if self.path == '/webhook':
                result = asyncio.run(self._handle_webhook())
                self._send_response(200, result)
                return
            
            # Установка webhook через POST
            if self.path == '/set_webhook':
                result = asyncio.run(self._set_webhook())
                self._send_response(200, result)
                return
            
            # 404 для остальных путей
            self._send_response(404, {"error": "Not found", "path": self.path})
            
        except Exception as e:
            logger.error(f"Ошибка POST запроса: {e}")
            self._send_response(500, {"error": str(e)})
    
    async def _handle_webhook(self):
        """Обработка webhook от Telegram"""
        try:
            # Получение данных запроса
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            logger.info(f"Получено обновление: {json.dumps(data, ensure_ascii=False)[:200]}...")
            
            # Инициализация бота
            bot_instance, dp_instance = await init_bot()
            
            # Создание Update объекта и обработка
            from aiogram.types import Update
            update = Update(**data)
            
            # Обработка обновления
            await dp_instance.feed_update(bot_instance, update)
            
            return {"ok": True}
            
        except Exception as e:
            logger.error(f"Ошибка обработки webhook: {e}")
            raise
    
    async def _set_webhook(self):
        """Установка webhook"""
        try:
            from aiogram import Bot
            
            # Получаем токен
            bot_token = os.getenv("BOT_TOKEN")
            if not bot_token:
                raise Exception("BOT_TOKEN не найден")
            
            # Создаем новый экземпляр бота для этой операции
            temp_bot = Bot(token=bot_token)
            
            # Получение хоста
            host = self.headers.get('host', self.headers.get('Host', 'unknown'))
            webhook_url = f"https://{host}/webhook"
            
            result = await temp_bot.set_webhook(webhook_url)
            logger.info(f"Webhook установлен: {webhook_url}")
            
            # Закрываем сессию
            await temp_bot.session.close()
            
            return {
                "ok": True, 
                "webhook_url": webhook_url,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Ошибка установки webhook: {e}")
            raise
    
    async def _get_webhook_info(self):
        """Получение информации о webhook"""
        try:
            from aiogram import Bot
            
            bot_token = os.getenv("BOT_TOKEN")
            if not bot_token:
                raise Exception("BOT_TOKEN не найден")
            
            temp_bot = Bot(token=bot_token)
            info = await temp_bot.get_webhook_info()
            
            await temp_bot.session.close()
            
            return {
                "url": info.url,
                "has_custom_certificate": info.has_custom_certificate,
                "pending_update_count": info.pending_update_count,
                "last_error_date": info.last_error_date,
                "last_error_message": info.last_error_message,
                "max_connections": info.max_connections,
                "allowed_updates": info.allowed_updates
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о webhook: {e}")
            raise
    
    def _send_response(self, status_code, data):
        """Отправка JSON ответа"""
        try:
            response_body = json.dumps(data, ensure_ascii=False).encode('utf-8')
            
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(response_body)))
            self.end_headers()
            self.wfile.write(response_body)
            
        except Exception as e:
            logger.error(f"Ошибка отправки ответа: {e}")
