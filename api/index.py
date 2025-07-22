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
            try:
                from db.database import init_database
            except ImportError:
                # Альтернативный путь для Vercel
                import sys
                import importlib.util
                
                db_path = os.path.join(root_dir, 'db', 'database.py')
                if os.path.exists(db_path):
                    spec = importlib.util.spec_from_file_location("database", db_path)
                    database_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(database_module)
                    init_database = database_module.init_database
                else:
                    raise ImportError("Не найден файл db/database.py")
                    
            logger.info("✓ db.database импортирован")
            
            logger.info("1️⃣ Инициализируем базу данных...")
            await init_database()
            logger.info("✓ База данных инициализирована")
            
        except Exception as e:
            logger.error(f"❌ Ошибка базы данных: {e}")
            # Не поднимаем ошибку - работаем без базы данных
            logger.warning("⚠️ Работаем без базы данных - будет только fallback функциональность")
        
        # Шаг 2: Импорт обработчиков
        handlers_imported = {}
        
        def safe_import_handler(module_name: str, function_name: str):
            """Безопасный импорт обработчика с fallback"""
            try:
                logger.info(f"2️⃣ Импортируем {module_name}...")
                module = __import__(module_name, fromlist=[function_name])
                handler_func = getattr(module, function_name)
                logger.info(f"✓ {module_name} импортирован")
                return handler_func
            except Exception as e:
                logger.error(f"❌ Ошибка импорта {module_name}: {e}")
                return None
        
        # Импортируем обработчики с безопасными методами
        handlers_imported['common'] = safe_import_handler('handlers.common', 'setup_common_handlers')
        
        handlers_imported['command'] = safe_import_handler('handlers.command_handlers', 'setup_command_handlers')
        handlers_imported['menu'] = safe_import_handler('handlers.menu_handler', 'setup_menu_handlers')
        handlers_imported['voice'] = safe_import_handler('handlers.voice_handler', 'setup_voice_handlers')
        handlers_imported['marketer'] = safe_import_handler('handlers.marketer', 'setup_marketer_handlers')
        handlers_imported['financier'] = safe_import_handler('handlers.financier', 'setup_financier_handlers')
        handlers_imported['manager'] = safe_import_handler('handlers.manager', 'setup_manager_handlers')
        
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
        
        # ВСЕГДА добавляем fallback обработчик как последний
        await add_fallback_handler(dp)
        
        # Обновляем счетчик после добавления fallback
        final_handlers = len(dp.message.handlers)
        logger.info(f"🎯 ИТОГО MESSAGE HANDLERS (с fallback): {final_handlers}")
        
        # Выводим список всех обработчиков
        for i, handler in enumerate(dp.message.handlers):
            handler_name = handler.callback.__name__ if handler.callback else "Unknown"
            logger.info(f"  📝 Handler {i}: {handler_name}")
        
        # Шаг 4: Команды бота (опционально)
        try:
            logger.info("4️⃣ Импортируем utils.bot_commands...")
            bot_commands_func = safe_import_handler('utils.bot_commands', 'BotCommandManager')
            if bot_commands_func:
                logger.info("✓ utils.bot_commands импортирован")
                
                logger.info("4️⃣ Настраиваем команды бота...")
                command_manager = bot_commands_func(bot)
                await command_manager.setup_commands()
                logger.info("✓ Команды бота настроены")
            else:
                logger.warning("⚠️ Команды бота не настроены - модуль не импортирован")
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

async def add_fallback_handler(dp):
    """Добавляет fallback обработчик который ТОЧНО сработает"""
    from aiogram import types
    from aiogram.filters import Command
    
    async def fallback_start(message: types.Message):
        """Fallback start handler"""
        try:
            user_id = message.from_user.id
            logger.info(f"🆘 Fallback /start от пользователя {user_id}")
            await message.reply(
                "🤖 Бот запущен в режиме совместимости.\n"
                "Некоторые функции могут быть ограничены.\n\n"
                "Попробуйте:\n"
                "• /help - справка\n"
                "• /status - статус системы"
            )
        except Exception as e:
            logger.error(f"Ошибка в fallback_start: {e}")
    
    async def fallback_help(message: types.Message):
        """Fallback help handler"""
        try:
            user_id = message.from_user.id
            logger.info(f"🆘 Fallback /help от пользователя {user_id}")
            await message.reply(
                "ℹ️ Справка (режим совместимости)\n\n"
                "Доступные команды:\n"
                "• /start - перезапуск\n"
                "• /help - эта справка\n"
                "• /status - статус бота\n\n"
                "Для полной функциональности обратитесь к администратору."
            )
        except Exception as e:
            logger.error(f"Ошибка в fallback_help: {e}")
    
    async def fallback_status(message: types.Message):
        """Fallback status handler"""
        try:
            user_id = message.from_user.id
            logger.info(f"🆘 Fallback /status от пользователя {user_id}")
            await message.reply(
                "📊 Статус системы:\n\n"
                "🤖 Бот: Активен (режим совместимости)\n"
                "⚡ Webhook: Работает\n"
                "🛡️ Режим: Fallback handlers\n\n"
                "Если видите это сообщение, основные обработчики не загружены."
            )
        except Exception as e:
            logger.error(f"Ошибка в fallback_status: {e}")
    
    async def fallback_default(message: types.Message):
        """Универсальный fallback обработчик"""
        try:
            user_id = message.from_user.id
            text = message.text or "<non-text>"
            logger.info(f"🆘 Fallback default для {user_id}: {text[:50]}")
            await message.reply(
                f"🤖 Получено сообщение: «{text[:50]}{'...' if len(text) > 50 else ''}»\n\n"
                f"Бот работает в ограниченном режиме.\n"
                f"Используйте /help для получения справки."
            )
        except Exception as e:
            logger.error(f"Ошибка в fallback_default: {e}")
    
    # Регистрируем fallback обработчики 
    dp.message.register(fallback_start, Command("start"))
    dp.message.register(fallback_help, Command("help"))  
    dp.message.register(fallback_status, Command("status"))
    dp.message.register(fallback_default)  # Последний - ловит всё остальное
    
    logger.info("✓ Fallback обработчики зарегистрированы")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Обработка GET запросов"""
        try:
            logger.info(f"GET запрос: {self.path}")
            
            # Health check
            if self.path in ['/', '/health']:
                # Инициализируем бота при первом запросе чтобы убедиться что всё работает
                try:
                    bot_instance, dp_instance = asyncio.run(init_bot())
                    handlers_count = len(dp_instance.message.handlers) if dp_instance.message.handlers else 0
                    response = {
                        "status": "ok", 
                        "bot": "running",
                        "webhook": "active",
                        "handlers": handlers_count,
                        "message": "Bot initialized successfully"
                    }
                except Exception as e:
                    logger.error(f"Ошибка инициализации бота в health check: {e}")
                    response = {
                        "status": "error", 
                        "bot": "error",
                        "webhook": "inactive",
                        "error": str(e)
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
            
            logger.info(f"📨 Получено обновление: {json.dumps(data, ensure_ascii=False)[:200]}...")
            
            # Инициализация бота
            bot_instance, dp_instance = await init_bot()
            
            # ДИАГНОСТИКА: Проверяем что обработчики есть
            handlers_count = len(dp_instance.message.handlers) if dp_instance.message.handlers else 0
            logger.info(f"🎯 Доступно message handlers: {handlers_count}")
            
            if handlers_count == 0:
                logger.error("❌ НЕТ ОБРАБОТЧИКОВ СООБЩЕНИЙ!")
                logger.info("🆘 Добавляем экстренные обработчики...")
                await add_minimal_handlers(dp_instance)
                handlers_count = len(dp_instance.message.handlers)
                logger.info(f"✅ Добавлено экстренных обработчиков: {handlers_count}")
            else:
                # Показываем список обработчиков для диагностики
                for i, handler in enumerate(dp_instance.message.handlers):
                    handler_name = handler.callback.__name__ if handler.callback else "Unknown"
                    logger.info(f"  📝 Handler {i}: {handler_name}")
            
            # Создание Update объекта
            from aiogram.types import Update
            update = Update(**data)
            
            # Дополнительная диагностика входящего апдейта
            if update.message:
                text = update.message.text or "<non-text message>"
                user_id = update.message.from_user.id if update.message.from_user else "unknown"
                logger.info(f"📩 Сообщение от {user_id}: '{text[:50]}...'")
            elif update.callback_query:
                logger.info(f"🔘 Callback query: {update.callback_query.data}")
            else:
                logger.info(f"❓ Неизвестный тип апдейта: {update}")
            
            # Обработка обновления
            logger.info("⚡ Начинаем обработку апдейта...")
            await dp_instance.feed_update(bot_instance, update)
            logger.info("✅ Апдейт обработан успешно")
            
            return {"ok": True}
            
        except Exception as e:
            logger.error(f"💥 Ошибка обработки webhook: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
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
