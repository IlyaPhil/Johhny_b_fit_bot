"""
Импорт зависимостей
"""
from datetime import datetime, timedelta
import aiohttp
from googletrans import Translator
from config_reader import config


# получаем ключ для OpenWeatherMap API
weather_api_key=config.weather_api_key.get_secret_value()
# получаем ключ для USADA API
usada_api_key = config.usada_api_key.get_secret_value()

# Брем функцию из ДЗ1, только теперь делаем запрос
# асинхронным при помощи библиотеки aiohttp
async def get_temperature_by_api(city, key):
    """
    Асинхронная функция для получения температуры по API OpenWeatherMap.

    Args:
    city (str): Название города.
    key (str): Ключ API OpenWeatherMap.

    Returns:
    float: текущая температура
    """

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric"

    try:
        # Создание асинхронного клиента
        async with aiohttp.ClientSession() as session:
            # Отправка асинхронного GET-запроса
            async with session.get(url) as response:
                # Проверка статуса ответа
                if response.status == 200:
                    # Если запрос успешный, получаем JSON-данные
                    weather_data = await response.json()
                    temperature = weather_data['main']['temp']
                    return temperature
                else:
                    # Если произошла ошибка, получаем JSON ошибки
                    error_data = await response.json()
                    return f"Ошибка: {error_data}"

    except aiohttp.ClientError as e:
        # Обработка ошибок соединения
        return (f"Ошибка соединения: {e}", None)


# Расчет суточной нормы калорий и воды
# Используем формулу Миффлина-Сан Жеора для расчета базального метаболизма (BMR)
# и затем умножим его на коэффициент физической активности
async def calculate_daily_needs(user_data):
    """
    Расчет норм потребления воды и калорий для введенных параметров пользователя
    """
    # Получаем значения параметров из переданных данных пользователя
    weight = float(user_data['weight'])
    height = float(user_data['height'])
    age = int(user_data['age'])
    gender = user_data['gender']
    city = user_data['city']
    activity_level = float(user_data['activity_level'])

    # Расчет BMR
    if gender.lower() == 'мужской':
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

    # Расчет суточной нормы калорий
    calories_norm = int(bmr * activity_level)
    # Добавляем флаг того, что текущая температура превышает 25 градусов
    hotness_flag = await get_temperature_by_api(city=city, key=weather_api_key) > 25

    # Расчет суточной нормы воды сделаем как было предложено в условии ДЗ
    water_norm = int(weight * 30 + 500 * activity_level / 30 + 750 * hotness_flag)

    return (calories_norm, water_norm)


async def get_calories_from_food(food_name):
    """
    Получение калорийности продуктов по API
    """
    api_key = usada_api_key
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"

    params = {
        'api_key': api_key,
        'query': food_name,
        'dataType': 'Survey (FNDDS)'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                food_data = await response.json()
                return food_data
            else:
                print(f"Ошибка запроса: {response.status} - {await response.text()}")
                return None


async def rus_eng_translate(text):
    """
    Перевод названия продуктов с русского языка на английский
    """
    async with Translator() as translator:
        result = await translator.translate(text)
        return result.text


def check_time_elapsed(user_data):
    """
    Проверка того, прошло ли 24 часа с момента начала логирования,
    и если да, то - обнуление логов
    """
    # Проверяем, прошло ли 24 часа с момента начала периода логирования
    current_time = datetime.now()
    if current_time - user_data['last_logging_start_time'] >= timedelta(days=1):
        # Если да, то обнуляем все логи
        user_data['logged_water'] = 0
        user_data['calories_consumed'] = 0
        user_data['calories_burned'] = 0
        user_data['logged_calories'] = 0
    return user_data
