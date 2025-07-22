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
        
        try:
            # Пытаемся импортировать и инициализировать полную функциональность
            logger.info("Начинаем загрузку модулей...")
            
            # Импортируем по одному с логированием
            logger.info("Импортируем базовые модули...")
            from db.database import init_database
            logger.info("✓ db.database импортирован")
            
            # Инициализация базы данных
            logger.info("Инициализируем базу данных...")
            await init_database()
            logger.info("✓ База данных инициализирована")
            
            logger.info("Импортируем обработчики...")
            from handlers.common import setup_common_handlers
            logger.info("✓ handlers.common импортирован")
            
            from handlers.menu_handler import setup_menu_handlers  
            logger.info("✓ handlers.menu_handler импортирован")
            
            from handlers.command_handlers import setup_command_handlers
            logger.info("✓ handlers.command_handlers импортирован")
            
            from handlers.voice_handler import setup_voice_handlers
            logger.info("✓ handlers.voice_handler импортирован")
            
            from handlers.marketer import setup_marketer_handlers
            logger.info("✓ handlers.marketer импортирован")
            
            from handlers.financier import setup_financier_handlers
            logger.info("✓ handlers.financier импортирован")
            
            from handlers.manager import setup_manager_handlers
            logger.info("✓ handlers.manager импортирован")
            
            from utils.bot_commands import BotCommandManager
            logger.info("✓ utils.bot_commands импортирован")
            
            # КРИТИЧНО: Регистрация обработчиков в правильном порядке
            logger.info("🔧 Начинаем регистрацию обработчиков...")
            
            # 1. Сначала специфичные обработчики
            try:
                setup_command_handlers(dp)
                cmd_count = len(dp.message.handlers)
                logger.info(f"✓ Command handlers зарегистрированы (handlers: {cmd_count})")
            except Exception as e:
                logger.error(f"❌ Ошибка в setup_command_handlers: {e}")
            
            try:
                setup_voice_handlers(dp)
                voice_count = len(dp.message.handlers)
                logger.info(f"✓ Voice handlers зарегистрированы (total handlers: {voice_count})")
            except Exception as e:
                logger.error(f"❌ Ошибка в setup_voice_handlers: {e}")
            
            try:
                setup_marketer_handlers(dp)
                marketer_count = len(dp.message.handlers)
                logger.info(f"✓ Marketer handlers зарегистрированы (total handlers: {marketer_count})")
            except Exception as e:
                logger.error(f"❌ Ошибка в setup_marketer_handlers: {e}")
            
            try:
                setup_financier_handlers(dp)
                financier_count = len(dp.message.handlers)
                logger.info(f"✓ Financier handlers зарегистрированы (total handlers: {financier_count})")
            except Exception as e:
                logger.error(f"❌ Ошибка в setup_financier_handlers: {e}")
            
            try:
                setup_manager_handlers(dp)
                manager_count = len(dp.message.handlers)
                logger.info(f"✓ Manager handlers зарегистрированы (total handlers: {manager_count})")
            except Exception as e:
                logger.error(f"❌ Ошибка в setup_manager_handlers: {e}")
            
            try:
                setup_menu_handlers(dp)
                menu_count = len(dp.message.handlers)
                logger.info(f"✓ Menu handlers зарегистрированы (total handlers: {menu_count})")
            except Exception as e:
                logger.error(f"❌ Ошибка в setup_menu_handlers: {e}")
            
            # 2. Общие обработчики идут ПОСЛЕДНИМИ (включая default)
            try:
                setup_common_handlers(dp)
                total_count = len(dp.message.handlers)
                logger.info(f"✓ Common handlers зарегистрированы (total handlers: {total_count})")
            except Exception as e:
                logger.error(f"❌ Ошибка в setup_common_handlers: {e}")
            
            # 3. Финальная проверка
            final_handlers = len(dp.message.handlers)
            logger.info(f"🎯 ИТОГО ЗАРЕГИСТРИРОВАНО MESSAGE HANDLERS: {final_handlers}")
            
            # Выводим список всех обработчиков
            for i, handler in enumerate(dp.message.handlers):
                handler_name = handler.callback.__name__
                filters_info = str(handler.filters) if handler.filters else "No filters"
                logger.info(f"  Handler {i}: {handler_name} | Filters: {filters_info}")
            
            if final_handlers == 0:
                logger.error("❌ НЕ ЗАРЕГИСТРИРОВАНО НИ ОДНОГО MESSAGE HANDLER!")
                raise Exception("Message handlers не зарегистрированы")
            
            # Настройка команд бота
            logger.info("Настраиваем команды бота...")
            try:
                command_manager = BotCommandManager(bot)
                await command_manager.setup_commands()
                logger.info("✓ Команды бота настроены")
            except Exception as e:
                logger.error(f"❌ Ошибка настройки команд: {e}")
            
            logger.info("🎉 ПОЛНАЯ ФУНКЦИОНАЛЬНОСТЬ ЗАГРУЖЕНА УСПЕШНО!")
            
        except ImportError as ie:
            logger.error(f"❌ Ошибка импорта: {ie}")
            # Добавляем базовый обработчик в случае ошибки
            await add_emergency_handler(dp)
            
        except Exception as e:
            logger.error(f"❌ Общая ошибка при инициализации: {e}")
            # Добавляем базовый обработчик в случае ошибки
            await add_emergency_handler(dp)
        
        return bot, dp
        
    except Exception as e:
        logger.error(f"Критическая ошибка инициализации бота: {e}")
        raise

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
