# 🚀 Деплой на Vercel

## Подготовка к деплою

Проект подготовлен для деплоя на платформу Vercel с поддержкой serverless функций.

### Структура для Vercel

```
├── api/
│   └── index.py              # Serverless функция
├── vercel.json               # Конфигурация Vercel
├── runtime.txt               # Версия Python
├── requirements.txt          # Зависимости Python
└── [остальные файлы проекта]
```

### Файлы конфигурации

#### `vercel.json`
```json
{
  "functions": {
    "api/index.py": {
      "runtime": "python3.11"
    }
  },
  "routes": [
    {
      "src": "/webhook",
      "dest": "/api/index.py"
    },
    {
      "src": "/set_webhook",
      "dest": "/api/index.py"
    },
    {
      "src": "/webhook_info",
      "dest": "/api/index.py"
    },
    {
      "src": "/health",
      "dest": "/api/index.py"
    },
    {
      "src": "/",
      "dest": "/api/index.py"
    }
  ],
  "env": {
    "PYTHONPATH": ".",
    "TZ": "UTC"
  },
  "regions": ["fra1"]
}
```

#### `runtime.txt`
```
python-3.11
```

## Настройка переменных окружения

В панели Vercel добавьте следующие переменные:

### Обязательные переменные:
- `BOT_TOKEN` - токен Telegram бота
- `OPENAI_API_KEY` - ключ OpenAI API
- `MARKETERS` - ID маркетологов (через запятую)
- `FINANCIERS` - ID финансистов (через запятую)
- `MANAGERS` - ID руководителей (через запятую)

### Дополнительные переменные:
- `LOW_BALANCE_THRESHOLD` - порог низкого баланса (по умолчанию: 100)
- `DATABASE_PATH` - путь к базе данных (по умолчанию: /tmp/bot.db)
- `DASHBOARD_TOKEN` - токен для доступа к дашборду

## Процесс деплоя

### 1. Подключение репозитория

1. Войдите в [Vercel Dashboard](https://vercel.com/dashboard)
2. Нажмите "New Project"
3. Выберите репозиторий из GitHub
4. Vercel автоматически определит настройки

### 2. Настройка переменных

1. Перейдите в Settings → Environment Variables
2. Добавьте все необходимые переменные
3. Убедитесь, что они доступны для всех сред (Production, Preview, Development)

### 3. Деплой

1. Vercel автоматически начнет деплой при коммите в main/master ветку
2. Следите за логами в разделе Deployments

### 4. Настройка webhook

После успешного деплоя:

1. Получите URL вашего приложения (например: `https://your-app.vercel.app`)
2. Перейдите по адресу: `https://your-app.vercel.app/set_webhook`
3. Проверьте статус webhook: `https://your-app.vercel.app/webhook_info`

## Endpoints

### Основные маршруты:

- `GET /` - статус приложения
- `GET /health` - проверка здоровья
- `POST /webhook` - webhook для Telegram
- `POST /set_webhook` - установка webhook
- `GET /webhook_info` - информация о webhook

### Ответы API:

#### GET / или /health
```json
{
  "status": "ok",
  "bot": "running",
  "webhook": "active"
}
```

#### POST /set_webhook
```json
{
  "ok": true,
  "webhook_url": "https://your-app.vercel.app/webhook",
  "result": true
}
```

## Мониторинг

### Логи

1. В Vercel Dashboard перейдите в раздел Functions
2. Выберите функцию `api/index.py`
3. Просмотрите логи выполнения

### Проверка работоспособности

1. **Health check**: `curl https://your-app.vercel.app/health`
2. **Webhook info**: `curl https://your-app.vercel.app/webhook_info`
3. **Тест бота**: отправьте команду `/start` в Telegram

## Ограничения Vercel

### Serverless функции:
- **Время выполнения**: 10 секунд (Hobby), 60 секунд (Pro)
- **Размер функции**: 50MB
- **Память**: 1024MB (по умолчанию)

### База данных:
- SQLite база данных создается в `/tmp/` (временная файловая система)
- Данные могут быть потеряны при перезапуске функции
- **Рекомендация**: подключить внешнюю БД (PostgreSQL, MySQL)

### Голосовые сообщения:
- Обработка голосовых файлов через OpenAI API
- Временные файлы сохраняются в `/tmp/`
- Автоматически удаляются после обработки

## Возможные проблемы

### 1. Timeout ошибки
**Причина**: Долгая обработка голосовых сообщений или AI запросов
**Решение**: Оптимизация кода, увеличение лимитов (Pro план)

### 2. База данных
**Причина**: Потеря данных в SQLite
**Решение**: Использование внешней базы данных

### 3. Холодный старт
**Причина**: Первый запрос после периода неактивности
**Решение**: Warming up endpoints, Pro план

## Альтернативы

Если Vercel не подходит:

1. **Railway** - хорошая поддержка Python
2. **Render** - бесплатный tier с persistent storage
3. **Heroku** - классическая платформа
4. **DigitalOcean App Platform** - доступные цены

## Поддержка

При возникновении проблем:

1. Проверьте логи в Vercel Dashboard
2. Убедитесь в правильности переменных окружения
3. Проверьте статус webhook в Telegram
4. Тестируйте API endpoints напрямую