# 🤖 Бот для обращений в ОСС

Телеграм-бот, позволяющий пользователям направлять обращения в Общественный студенческий совет (ОСС).  

---

## 🚀 Развертывание

### 1. Клонировать репозиторий

```bash
git clone https://github.com/your-username/oss-bot.git
cd oss-bot
```
2. Создать и активировать виртуальное окружение
```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
```
3. Установить зависимости
Уже готовый requirements.txt:

```bash
pip install -r requirements.txt
```
4. Указать токен бота
Создай файл .env (если ещё нет) и добавь:

```env
TOKEN = "ваш токен"
GROUP_ID = id группы
```

⚠️ .env нужно создать самостоятельно.

5. Запустить бота
```bash
python main.py
```
📁 Структура проекта
bash
Копировать
Редактировать
oss-bot/
├── main.py              # основной файл бота
├── json_storage.py      # файл хранилища данных
├── .env                 # файл с переменными окружения (BOT_TOKEN)
├── requirements.txt     # зависимости проекта
├── README.md            # эта инструкция
└── ...
