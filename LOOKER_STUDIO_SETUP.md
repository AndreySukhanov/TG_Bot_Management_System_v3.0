# 📊 Настройка Google Looker Studio для Telegram бота

## 🎯 О интеграции

Google Looker Studio (ранее Data Studio) - это бесплатная платформа для создания интерактивных дашбордов и отчетов. Интеграция с нашим ботом позволяет создавать профессиональные аналитические отчеты без необходимости поддерживать собственный веб-дашборд.

### ✅ Преимущества Looker Studio:
- **Бесплатно** - экономия на хостинге
- **Профессиональные графики** - готовые шаблоны
- **Автообновление данных** - настраиваемые интервалы
- **Легкий доступ** - поделиться ссылкой с командой
- **Мобильная версия** - просмотр с телефона
- **Google интеграция** - работает с другими сервисами Google

---

## 🛠️ Техническая архитектура

### Схема работы:
```
Telegram Bot → SQLite DB → Looker API → Google Looker Studio → Дашборды
```

### Компоненты:
1. **Looker API** (`dashboard/looker_api.py`) - FastAPI сервер на порту 8001
2. **Эндпоинты данных** - структурированные API для Looker Studio
3. **Авторизация** - Bearer token для безопасности
4. **CORS настройки** - доступ только для Looker Studio

---

## 🚀 Установка и запуск

### Шаг 1: Запуск API сервера

```bash
# Запуск Looker API (порт 8001)
python start_looker_api.py

# Проверка работы API
curl http://localhost:8001/
```

**Результат:**
```
🚀 Запуск Looker Studio API сервера...
📊 API будет доступен по адресу: http://localhost:8001
🔑 API Token: looker_studio_token_2025
📋 Документация: http://localhost:8001/docs
```

### Шаг 2: Проверка эндпоинтов

Доступные эндпоинты:
- `GET /` - информация об API
- `GET /payments` - данные о платежах
- `GET /balance-history` - история баланса
- `GET /projects` - статистика по проектам  
- `GET /daily-stats` - ежедневная статистика
- `GET /users` - информация о пользователях

**Пример запроса:**
```bash
curl -H "Authorization: Bearer looker_studio_token_2025" http://localhost:8001/payments?days=30
```

---

## 📊 Настройка Google Looker Studio

### Шаг 1: Создание источника данных

1. Откройте [Looker Studio](https://lookerstudio.google.com)
2. Нажмите **"Создать"** → **"Источник данных"**
3. Выберите **"HTTP/REST API"** или **"Веб-коннектор"**

### Шаг 2: Настройка подключения

**Параметры подключения:**
- **URL:** `http://ваш-сервер.com:8001/payments`
- **Метод:** `GET`
- **Заголовки:**
  ```
  Authorization: Bearer looker_studio_token_2025
  Content-Type: application/json
  ```

### Шаг 3: Настройка полей данных

После подключения Looker Studio автоматически определит поля:

**Основные поля платежей:**
- `payment_id` (число) - ID платежа
- `service_name` (текст) - название сервиса
- `amount` (число) - сумма платежа
- `project_name` (текст) - название проекта
- `status` (текст) - статус платежа
- `payment_date` (дата) - дата платежа
- `user_type` (текст) - тип пользователя

**Вычисляемые поля:**
- `day_of_week` (число) - день недели (0-6)
- `is_weekend` (булево) - выходной день
- `amount_usd` (число) - сумма в долларах
- `status_numeric` (число) - статус в числовом виде

---

## 📈 Создание дашбордов

### Дашборд 1: Общая статистика

**Компоненты:**
1. **Scorecard** - текущий баланс
2. **Scorecard** - общее количество платежей
3. **Scorecard** - общая сумма платежей
4. **Time Series** - график платежей по дням
5. **Pie Chart** - распределение по проектам

### Дашборд 2: Аналитика по проектам

**Компоненты:**
1. **Table** - топ проектов по сумме
2. **Bar Chart** - сравнение проектов
3. **Geo Map** - если есть геоданные
4. **Heatmap** - активность по дням недели

### Дашборд 3: Финансовая аналитика

**Компоненты:**
1. **Line Chart** - динамика баланса
2. **Area Chart** - приход/расход
3. **Waterfall** - изменения баланса
4. **Gauge** - индикатор здоровья системы

---

## 🔧 Расширенные настройки

### Фильтры и параметры

Looker Studio поддерживает динамические параметры:

**Временные фильтры:**
- `?days=7` - последние 7 дней
- `?days=30` - последний месяц
- `?days=90` - последние 3 месяца

**Фильтры по статусу:**
- `?status=paid` - только оплаченные
- `?status=pending` - только ожидающие

**Пример URL с фильтрами:**
```
http://localhost:8001/payments?days=30&status=paid
```

### Автообновление данных

В Looker Studio настройте автообновление:
1. **Источник данных** → **Настройки**
2. **Кэширование** → **Включить автообновление**
3. **Интервал:** каждые 15 минут / 1 час / 4 часа

### Настройка уведомлений

Создайте автоматические отчеты:
1. **Дашборд** → **Поделиться** → **Запланировать доставку**
2. **Частота:** ежедневно / еженедельно
3. **Получатели:** email адреса команды
4. **Формат:** PDF / ссылка

---

## 🔐 Безопасность

### Авторизация API

**Токен доступа:** `looker_studio_token_2025`

Для изменения токена отредактируйте файл `dashboard/looker_api.py`:
```python
LOOKER_API_TOKEN = "ваш_новый_токен"
```

### CORS настройки

API настроен только для доменов Looker Studio:
```python
allow_origins=[
    "https://lookerstudio.google.com", 
    "https://datastudio.google.com"
]
```

### Рекомендации по безопасности

1. **Используйте HTTPS** в production
2. **Смените токен** от стандартного
3. **Ограничьте IP доступ** на сервере
4. **Настройте firewall** для порта 8001
5. **Регулярно обновляйте** токен доступа

---

## 🚀 Деплой в production

### На VPS сервере

1. **Установите зависимости:**
```bash
pip install fastapi uvicorn
```

2. **Создайте systemd сервис:**
```bash
sudo nano /etc/systemd/system/looker-api.service
```

```ini
[Unit]
Description=Looker Studio API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/bot
ExecStart=/path/to/venv/bin/python start_looker_api.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. **Запустите сервис:**
```bash
sudo systemctl enable looker-api
sudo systemctl start looker-api
```

### Настройка Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location /api/ {
        proxy_pass http://localhost:8001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📋 Примеры запросов

### Получение платежей за последние 7 дней

```bash
curl -H "Authorization: Bearer looker_studio_token_2025" \
     "http://localhost:8001/payments?days=7"
```

**Ответ:**
```json
{
  "data": [
    {
      "payment_id": 123,
      "service_name": "Facebook Ads",
      "amount": 100.0,
      "project_name": "Alpha",
      "status": "paid",
      "payment_date": "2025-01-15",
      "user_type": "marketer"
    }
  ],
  "meta": {
    "total_records": 1,
    "date_range_days": 7,
    "generated_at": "2025-01-20T10:30:00"
  }
}
```

### Получение статистики по проектам

```bash
curl -H "Authorization: Bearer looker_studio_token_2025" \
     "http://localhost:8001/projects?days=30"
```

### Получение истории баланса

```bash
curl -H "Authorization: Bearer looker_studio_token_2025" \
     "http://localhost:8001/balance-history?days=30"
```

---

## 🎨 Рекомендуемые визуализации

### График временных рядов
- **Ось X:** payment_date
- **Ось Y:** amount (сумма)
- **Группировка:** project_name
- **Фильтр:** status = "paid"

### Круговая диаграмма
- **Измерение:** project_name
- **Метрика:** SUM(amount)
- **Сортировка:** по убыванию суммы

### Таблица топ проектов
- **Столбцы:** project_name, total_amount, paid_payments
- **Сортировка:** total_amount DESC
- **Условное форматирование:** цвет по сумме

### Тепловая карта активности
- **Строки:** день недели
- **Столбцы:** час дня
- **Значения:** количество платежей

---

## 🔍 Отладка и мониторинг

### Проверка работы API

```bash
# Проверка статуса API
curl http://localhost:8001/

# Проверка с авторизацией
curl -H "Authorization: Bearer looker_studio_token_2025" \
     http://localhost:8001/payments?days=1

# Просмотр документации
open http://localhost:8001/docs
```

### Логи сервера

```bash
# Просмотр логов systemd
sudo journalctl -u looker-api -f

# Проверка портов
netstat -tlnp | grep 8001
```

### Частые проблемы

**1. CORS ошибки:**
- Проверьте настройки CORS в `looker_api.py`
- Убедитесь, что домен Looker Studio в списке разрешенных

**2. Ошибки авторизации:**
- Проверьте правильность токена
- Убедитесь, что заголовок Authorization настроен

**3. Таймауты:**
- Увеличьте таймауты в Looker Studio
- Оптимизируйте SQL запросы в API

---

## 📚 Дополнительные ресурсы

### Документация
- [Google Looker Studio Help](https://support.google.com/looker-studio)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Community Connectors](https://developers.google.com/looker-studio/connector)

### Шаблоны дашбордов
В репозитории в папке `looker_templates/` можно найти готовые шаблоны:
- `financial_dashboard.json` - финансовый дашборд
- `projects_analytics.json` - аналитика проектов
- `users_activity.json` - активность пользователей

---

*Looker Studio позволяет создавать профессиональные дашборды без затрат на разработку и хостинг!*