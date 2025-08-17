# Используем официальный образ Python
FROM python:3.12

# Устанавливаем рабочую директорию
WORKDIR /usr/src/app

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем необходимые зависимости (например, библиотеку для работы с Telegram API)
RUN pip install -r requirements.txt

# Копируем все файлы проекта в контейнер
COPY . /usr/src/app/

# Команда для запуска бота (укажите имя вашего файла с ботом)
CMD ["python", "bot.py"]
