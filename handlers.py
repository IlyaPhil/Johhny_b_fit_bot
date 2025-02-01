"""
Импортируем зависимости
"""
from datetime import datetime
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from functions import (calculate_daily_needs,
                       get_calories_from_food,
                       rus_eng_translate,
                       check_time_elapsed
                      )


# Словарь для хранения данных пользователей
user_dict = {}

# Время запуска бота
start_time = datetime.now()

# Cоздаем класс, для группы состояний нашего FSM
class Form(StatesGroup):
    user_id = State()           # user_id
    gender = State()            # пол
    weight = State()            # вес
    height = State()            # рост
    age = State()               # возраст
    activity_level = State()    # уровень активности
    city = State()              # город проживания
    calories_goal = State()     # цель по калориям
    confirmation = State()      # подтверждение профиля
    log_water = State()         # логирование воды
    log_food = State            # логирование еды
    log_food_name = State()     # логирование названия продуктов
    log_food_amount = State()   # логирование количества продуктов
    log_workout = State()       # логирование физ. активности
    workout_type = State()      # тип физ. активности
    food_name = State()         # логирование физ. активности


# Виртуальная клавиатура для выбора пола
kb_gender = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Мужской", callback_data='мужской')],
        [InlineKeyboardButton(text="Женский", callback_data='женский')]
    ]
)

# Виртуальная клавиатура для выбора уровня физической активности
kb_act_level = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Сидячий образ жизни (минимальная активность)",\
                               callback_data='1.2')],
        [InlineKeyboardButton(text="Легкая активность (легкие упражнения 1-3 раза в неделю)",\
                               callback_data='1.375')],
        [InlineKeyboardButton(text="Умеренная активность (умеренные упражнения 3-5 раз в неделю)",\
                               callback_data='1.55')],
        [InlineKeyboardButton(text="Высокая активность (интенсивные упражнения 6-7 раз в неделю)",\
                               callback_data='1.735')],
        [InlineKeyboardButton(text="Экстремальная активность (очень тяжелые физические нагрузки,\
                               работа или тренировки дважды в день)", callback_data='1.9')]
    ]
)

# Виртуальная клавиатура для выбора вида физической активности
kb_workout = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Бег", callback_data="9")],
        [InlineKeyboardButton(text="Ходьба", callback_data="3.5")],
        [InlineKeyboardButton(text="Плавание", callback_data="7")],
        [InlineKeyboardButton(text="Велосипед", callback_data="5")],
        [InlineKeyboardButton(text="Фитнес", callback_data="7")],
        [InlineKeyboardButton(text="Йога", callback_data="4.5")],
        [InlineKeyboardButton(text="Игровые виды спорта", callback_data="5")],
        [InlineKeyboardButton(text="Единоборства", callback_data="10")],
    ]
)


async def process_start_cmd(message: types.Message):
    """
    Обработчик команды /start
    """
    await message.answer("Привет! Я готов следить за твоими калориями "
                         "и количеством выпитой воды.\n"
                         "Чтобы перейти к заполнению профиля введите команду /set_profile\n"
                         "Чтобы сбросить заполнение профиля введите команду /cancel"
    )


async def process_cancel_cmd(message: types.Message, state: FSMContext):
    """
    Обработчик команды /cancel
    """
    await message.answer(
        text='Вы вышли из диалога\n'
             'Чтобы снова перейти к заполнению профиля - '
             'введите комманду /set_profile'
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


async def process_set_profile_cmd(message: types.Message):
    """
    Обработчик на команду /set_profile
    """
    # Получаем уникальный ID пользователя
    user_id = message.from_user.id
    # создаем словарь для нового пользователя
    user_dict[user_id] = {'gender': None,
                          'weight': 0,
                          'height': 0,
                          'age': 0,
                          'activity_level': None,
                          'city': None,
                          'water_norm': 0,
                          'calories_norm': 0,
                          'calories_goal': None,
                          'logged_water': 0,
                          'calories_consumed': 0,
                          'calories_burned': 0,
                          'logged_calories': 0
                          }

    await message.answer('Укажите ваш пол', reply_markup=kb_gender)


async def process_gender_sent(callback_query, state: FSMContext):
    """
    Обработчик ввода пола через inline-keyboard
    """
    # Получаем уникальный ID пользователяe
    user_id = callback_query.from_user.id
    # Сохраняем введенный пол в словаре пользователей по ключу "gender"
    user_dict[user_id]['gender'] = callback_query.data

    await callback_query.message.answer(text='Теперь введите ваш вес в кг')
    # Устанавливаем состояние ожидания ввода веса
    await state.set_state(Form.weight)


async def process_weight_sent(message: types.Message, state: FSMContext):
    """
    Обработчик ввода веса
    """
    # Получаем уникальный ID пользователя
    user_id = message.from_user.id
    # Cохраняем введеный вес в хранилище по ключу "weight"
    user_dict[user_id]['weight'] = message.text

    await message.answer(text='Теперь введите ваш рост в см')
    # Устанавливаем состояние ожидания ввода роста
    await state.set_state(Form.height)


async def process_height_sent(message: types.Message, state: FSMContext):
    """
    Обработчик ввода роста
    """
    # Получаем уникальный ID пользователя
    user_id = message.from_user.id
    # Cохраняем введенный вес в хранилище по ключу "height"
    user_dict[user_id]['height'] = message.text
    await message.answer(text='Теперь введите ваш возраст')
    # Устанавливаем состояние ожидания ввода возраста
    await state.set_state(Form.age)


async def process_age_sent(message: types.Message):
    """
    Обработчик ввода возраста
    """
    # Получаем уникальный ID пользователя
    user_id = message.from_user.id
    # Cохраняем введенный вес в хранилище по ключу "age"
    user_dict[user_id]['age'] = message.text
    await message.answer(text='Теперь определите ваш уровень '
                          'физической активности', reply_markup=kb_act_level)


async def process_activity_sent(callback_query, state: FSMContext):
    """
    Обработчик ввода уровня физической активности
    """
    # Получаем уникальный ID пользователя
    user_id = callback_query.from_user.id
    # Cохраняем введенный вес в хранилище по ключу "activity_level"
    activity_level = float(callback_query.data)
    user_dict[user_id]['activity_level'] = activity_level

    await callback_query.message.answer(text='Теперь введите название города, '
                         'в котором вы проживаете')
    # Устанавливаем состояние ожидания ввода города
    await state.set_state(Form.city)


async def process_city_sent(message: types.Message, state: FSMContext):
    """
    Обработчик ввода города
    """
    # Получаем уникальный ID пользователя
    user_id = message.from_user.id
    # Cохраняем введенный вес в хранилище по ключу "city"
    user_dict[user_id]['city'] = message.text

    # Рассчитываем дневную норму калорий и воды
    calories_norm, water_norm = await calculate_daily_needs(user_dict[user_id])
    # Записываем рассчитанные значения в словарь
    user_dict[user_id]['calories_norm'] = calories_norm
    user_dict[user_id]['water_norm'] = water_norm

    # Формируем сообщение с подтверждением введенных данных
    confirmation_message = (
        f"Ваш профиль:\n"
        f"Пол: {user_dict[user_id].get('gender')}\n"
        f"Вес: {user_dict[user_id].get('weight')} кг\n"
        f"Рост: {user_dict[user_id].get('height')} см\n"
        f"Возраст: {user_dict[user_id].get('age')} лет\n"
        f"Коэффициент активности: {user_dict[user_id].get('activity_level')}\n"
        f"Город: {user_dict[user_id].get('city')}\n"

        f"Рекомендуемая суточная норма калорий для ваших параметров: {calories_norm}\n"
        f"Рекомендуемая суточная норма воды для ваших параметров: {water_norm}"
    )

    await message.answer(confirmation_message)
    await message.answer(text='Если хотите, можете указать свою цель по '
                         'количеству потребляемых калорий в день, отличную от '
                         'суточной нормы, либо напишите "нет"')
    # Устанавливаем состояние ожидания ввода целевого уровня калорий
    await state.set_state(Form.calories_goal)


async def process_calorie_goal_sent(message: types.Message, state: FSMContext):
    """
    Обработчик ввода цели по калориям
    """
    # Получаем уникальный ID пользователя
    user_id = message.from_user.id
    # Проверяем, выбрал ли пользователь собственную цель по калориям
    if message.text != 'нет':
        # Сохраняем введенное количество калорий в храниище по ключу "calories_goal"
        user_dict[user_id]['calories_goal'] = message.text
        await message.answer('Данные приняты')
    # В противном случае оставляем значение None
    else:
        await message.answer('Ну и живи, как знаешь!')
    await message.answer("Если данные в профиле верны, напишите 'да', "
                         "если хотите изменить данные - напишите 'нет'")
    # Устанавливаем состояние подтверждения профиля
    await state.set_state(Form.confirmation)


async def process_confirm_profile(message: types.Message, state: FSMContext):
    """
    Обработчик подтверждения данных пользователем
    """
    await message.answer("Ваш профиль успешно сохранен!")
    # Завершаем состояние после обработки
    await state.clear()


async def process_change_profile(message: types.Message, state: FSMContext):
    """
    Обработчик изменения профиля данных пользователя
    """
    await message.answer("Хорошо! Давайте начнем заново. "
                         "Введите команду /set_profile для повторного заполнения профиля.")
    # Завершаем состояние после завершения диалога
    await state.clear()


async def process_start_logging_cmd(message: types.Message):
    """
    Обработчик команды /start_logging
    Нужен для того, чтобы фиксировать время начала логирования
    """
    # Получаем уникальный ID пользователя
    user_id = message.from_user.id
    user_dict[user_id]['last_logging_start_time'] = datetime.now()
    await message.answer(f"Время начала логирования: {datetime.now()} "
                         "Логирование будет сброшено через 24 часа")


async def process_log_water(message: types.Message, state: FSMContext):
    """
    Обработчик логирования количества выпитой воды
    """
    # Получаем уникальный ID пользователя
    user_id = message.from_user.id
    # Проверяем, не прошло ли 24 часа с момента логирования
    # Если прошло, то обнуляем логи
    user_dict[user_id] = check_time_elapsed(user_dict[user_id])
    await message.answer("Сколько миллилитров воды вы выпили?")
    # Устанавливаем состояние ожидания ввода
    await state.set_state(Form.log_water)


async def process_log_water_amount(message: types.Message, state: FSMContext):
    """
    Обработчик ввода количества воды
    """
    # Получаем уникальный ID пользователя
    user_id = message.from_user.id
    # Сохраняем введенное количество воды в храниище по ключу "logged_water"
    water_amount = int(message.text)
    user_dict[user_id]['logged_water'] = user_dict[user_id].get('logged_water') + water_amount
    await message.answer(f"До выполнения суточной нормы осталось выпить\
                          {user_dict[user_id].get('water_norm') -\
                            user_dict[user_id].get('logged_water')} мл")
    # Завершаем состояние после обработки
    await state.clear()


async def process_log_food(message: types.Message, state: FSMContext):
    """
    Обработчик логирования количества потребленных калорий
    """
     # Получаем уникальный ID пользователя
    user_id = message.from_user.id
    # Проверяем, не прошло ли 24 часа с момента логирования
    # Если прошло, то обнуляем логи
    user_dict[user_id] = check_time_elapsed(user_dict[user_id])
    await message.answer("Что вы сегодня съели?")
    # Устанавливаем состояние ожидания ввода названия съеденных продуктов
    await state.set_state(Form.log_food_name)


async def process_log_food_name(message: types.Message, state: FSMContext):
    """
    Обработчик логирования названия потребленных продуктов
    """
    food_name = message.text
    # Сохраняем наименование продукта в состоянии
    await state.update_data(log_food_name=food_name)
    await message.answer("Укажите вес съеденного в граммах")
    # Устанавливаем состояние ввода количества съеденных продуктов
    await state.set_state(Form.log_food_amount)


async def process_log_food_amount(message: types.Message, state: FSMContext):
    """
    Обработчик логирования количества съеденных продуктов
    """
    # Получаем уникальный ID пользователя
    user_id = message.from_user.id
    food_weight = int(message.text)
    # Получаем название продуктов из состояния
    user_data = await state.get_data()
    food_name = user_data.get('food_name')
    # Переводим название продуктов с русского на английский
    food_name = await rus_eng_translate(food_name)
    # Получаем калорийность введенных продуктов через API
    food_data = await get_calories_from_food(food_name)
    # Извлекаем значение калорийности из полученного ответа
    if food_data and 'foods' in food_data:
        food_info = food_data['foods'][0]
        calories = next((nutrient['value'] for nutrient in food_info['foodNutrients']\
                          if nutrient['nutrientName'] == 'Energy'))
        # Рассчитываем количество потребленных калорий с учетом массы продукта
        calories = int(calories * food_weight / 100)
        # Сохраняем количество потребленных калорий в хранилище по ключу "calories_consumed"
        user_dict[user_id]['calories_consumed'] = \
            user_dict[user_id].get('calories_consumed') + calories
        # Сохраняем баланс калорий в хранилище по ключу "logged_calories"
        user_dict[user_id]['logged_calories'] = \
             user_dict[user_id].get('logged_calories') + calories
        # Если пользователь утсановил сою цель по количеству калорий
        # вычитаем из нее количество потребленных калорий
        if user_dict[user_id]['calories_goal'] is not None:
            calories_diff = int(user_dict[user_id]['calories_goal'])\
                 - user_dict[user_id]['logged_calories']

        # В противном случае вычитаем количество потребленных калорий из
        # рекомендуемой суточной нормы
        else:
            calories_diff = user_dict[user_id]['calories_norm'] \
                - user_dict[user_id]['logged_calories']
        # Если цель по количеству калорий не достигнута,
        # сообщаем пользователю о том, сколько калорий осталось получить
        if calories_diff > 0:
            await message.answer(f"Вы получили {calories} ккал. "
                                 f"До достижения цели осталось получить {calories_diff} ккал")
        else:
            await message.answer(f"Поздравляю, вы выполнили цель по количеству калорий! "
                                 f"{calories_diff} ккал")

    # Завершаем состояние после обработки
    await state.clear()


async def process_log_workout(message: types.Message, state: FSMContext):
    """
    Обработчик логирования тренировок
    """
    # Получаем уникальный ID пользователя
    user_id = message.from_user.id
    # Проверяем, не прошло ли 24 часа с момента логирования
    # Если прошло, то обнуляем логи
    user_dict[user_id] = check_time_elapsed(user_dict[user_id])
    await message.answer("Выберите тип физической активности:", reply_markup=kb_workout)
    # Сохраняем user_id в состоянии
    await state.update_data(user_id = user_id)


async def choose_workout(callback_query, state: FSMContext):
    """
    Обработчик выбора типа физической активности
    """
    workout_type = callback_query.data

    # Сохраняем workout_type в состоянии
    await state.update_data(workout_type=workout_type)
    await callback_query.message.answer('Теперь введите продолжительность занятия в минутах')
    # Устанавливаем состояние ожидания ввода
    await state.set_state(Form.log_workout)


async def specify_duration(message: types.Message, state: FSMContext):
    """
    Обработчик выбора типа физической активности
    """
    workout_duration = int(message.text)
    # Извлекаем данные из состояния
    user_data = await state.get_data()
    workout_calories = float(user_data.get('workout_type'))
    user_id = user_data.get('user_id')
    # Извлекаем значение веса пользователя из словаря
    weight = float(user_dict[user_id]['weight'])
    # Рассчитываем количество сожженных калорий
    calories_burned = int(workout_calories * weight * workout_duration / 60)
    # Сохраняем сожженные калории в хранилище по ключу "calories_burned"
    user_dict[user_id]['calories_burned'] \
        = user_dict[user_id].get('calories_burned') + calories_burned
    # Обновляем баланс калорий
    user_dict[user_id]['logged_calories'] \
        = user_dict[user_id].get('logged_calories') - calories_burned

    await message.answer(f'Поздравляю, вы сожгли {calories_burned} ккал')
    # Если продолжительность тренировки более 30 мин,
    # то предлагаем увеличить норму воды
    if workout_duration > 30:
        user_dict[user_id]['water_norm'] += 500
        await message.answer('Дополнительно Выпейте 500 мл воды')
    # Завершаем состояние после обработки
    await state.clear()


async def process_check_progress_cmd(message: types.Message):
    """
    Обработчик команды /check_progress
    """
    # Получаем уникальный ID пользователя
    user_id = message.from_user.id
    progress_message = (
       f"Вода:\n"
       f"Выпито: {user_dict[user_id].get('logged_water')} "
       f"мл из {user_dict[user_id].get('water_norm')} мл\n"
       f"Осталось: {user_dict[user_id].get('water_norm') \
                    - user_dict[user_id].get('logged_water')} мл\n\n"
       f"Калории:\n"
       f"Потреблено: {user_dict[user_id].get('calories_consumed')} ккал "
       f"из {user_dict[user_id].get('calories_goal') or \
             user_dict[user_id].get('calories_norm')} ккал\n"
       f"Сожжено: {user_dict[user_id].get('calories_burned')} ккал\n"
       f"Баланс: {user_dict[user_id].get('logged_calories')} ккал\n"
    )

    await message.answer(progress_message)
