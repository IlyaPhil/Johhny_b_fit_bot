from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from functions import calculate_daily_needs, get_calories_from_food, rus_eng_translate
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



# Словарь для хранения данных пользователей
user_dict = {}

# Cоздаем класс, для группы состояний нашего FSM
class Form(StatesGroup):
    user_id = State()
    gender = State()
    weight = State()
    height = State()
    age = State()
    activity_level = State()
    city = State()
    calories_goal = State()
    confirmation = State()  # состояние для подтверждения
    log_water = State() # логирование воды
    log_food = State
    log_food_name = State() # логирование воды
    log_food_amount = State() # логирование воды
    log_workout = State()
    workout_type = State()
    food_name = State()

kb_gender = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Мужской", callback_data='мужской')],
        [InlineKeyboardButton(text="Женский", callback_data='женский')]
    ]
)


kb_act_level = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Сидячий образ жизни (минимальная активность)", callback_data='1.2')],
        [InlineKeyboardButton(text="Легкая активность (легкие упражнения 1-3 раза в неделю)", callback_data='1.375')],
        [InlineKeyboardButton(text="Умеренная активность (умеренные упражнения 3-5 раз в неделю)", callback_data='1.55')],
        [InlineKeyboardButton(text="Высокая активность (интенсивные упражнения 6-7 раз в неделю)", callback_data='1.735')],
        [InlineKeyboardButton(text="Экстремальная активность (очень тяжелые физические нагрузки,\
                               работа или тренировки дважды в день)", callback_data='1.9')]
    ]
)


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

# Обработчик на команду /start
# @dp.message(Command("start"))
async def process_start_cmd(message: types.Message):
    await message.answer("Привет! Я готов следить за твоими калориями "
                         "и количеством выпитой воды.\n"
                         "Чтобы перейти к заполнению профиля введите команду /set_profile\n"
                         "Чтобы перейти к списку команд введите команду /help")

# Обработчик на команду "/help"
# @dp.message(Command('help'))
async def process_help_cmd(message: types.Message):
    await message.answer(
        'Напиши мне что-нибудь и в ответ '
        'я пришлю тебе твое сообщение'
    )


# Обработчик команды "/cancel"
# @dp.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_cmd(message: types.Message, state: FSMContext):
    await message.answer(
        text='Вы вышли из диалога\n'
             'Чтобы снова перейти к заполнению профиля - '
             'введите комманду /set_profile'
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()

# Обработчик на команду "/set_profile"
# @dp.message(Command('set_profile'))
async def process_set_profile_cmd(message: types.Message):
    user_id = message.from_user.id  # Получаем уникальный ID пользователя
    user_dict[user_id] = {}  # создаем словарь для нового пользователя
    await message.answer('Укажите ваш пол', reply_markup=kb_gender)
    # await state.set_state(Form.gender)  # Устанавливаем состояние ожидания ввода пола


# Обработчик ввода пола
# @dp.message(StateFilter(Form.gender), F.text.lower() in ('м', 'ж'))
async def process_gender_sent(callback_query, state: FSMContext):
    # user_id = message.from_user.id  # Получаем уникальный ID пользователяe
    user_id = callback_query.from_user.id  # Получаем уникальный ID пользователя
    # activity_level = float(callback_query.data)
    # Сохраняем введенный пол в словаре пользователей по ключу "gender"
    user_dict[user_id]['gender'] = callback_query.data

    await callback_query.message.answer(text='Спасибо!\n\nА теперь введите ваш вес в кг')
    await state.set_state(Form.weight) # Устанавливаем состояние ожидания ввода веса


# Обработчик ввода веса
# @dp.message(StateFilter(Form.weight), F.text.isdigit())
async def process_weight_sent(message: types.Message, state: FSMContext):
    # Cохраняем введеный вес в хранилище по ключу "weight"
    user_id = message.from_user.id  # Получаем уникальный ID пользователя
    user_dict[user_id]['weight'] = message.text

    await message.answer(text='Спасибо!\n\nА теперь введите ваш рост в см')
    # Устанавливаем состояние ожидания ввода роста
    await state.set_state(Form.height)


# Обработчик ввода роста
# @dp.message(StateFilter(Form.height), F.text.isdigit())
async def process_height_sent(message: types.Message, state: FSMContext):
    # Cохраняем введенный вес в хранилище по ключу "height"
    user_id = message.from_user.id  # Получаем уникальный ID пользователя
    user_dict[user_id]['height'] = message.text
    await message.answer(text='Спасибо!\n\nА теперь введите ваш возраст')
    # Устанавливаем состояние ожидания ввода возраста
    await state.set_state(Form.age)


# Обработчик ввода возраста
# @dp.message(StateFilter(Form.age), F.text.isdigit())
async def process_age_sent(message: types.Message):
    # Cохраняем введенный вес в хранилище по ключу "age"
    user_id = message.from_user.id  # Получаем уникальный ID пользователя
    user_dict[user_id]['age'] = message.text
    await message.answer(text='Спасибо!\n\nА теперь определите ваш уровень '
                          'физической активности', reply_markup=kb_act_level)


# Обработчик ввода уровня физической активности
async def process_activity_sent(callback_query, state: FSMContext):
    # Cохраняем введенный вес в хранилище по ключу "activity_level"
    user_id = callback_query.from_user.id  # Получаем уникальный ID пользователя
    activity_level = float(callback_query.data)
    user_dict[user_id]['activity_level'] = activity_level

    await callback_query.message.answer(text='Теперь введите название города, '
                         'в котором вы проживаете')
    # Устанавливаем состояние ожидания ввода города
    await state.set_state(Form.city)


# Обработчик ввода города
# @dp.message(StateFilter(Form.city), F.text.isalpha())
async def process_city_sent(message: types.Message, state: FSMContext):
    # Cохраняем введенный вес в хранилище по ключу "city"
    user_id = message.from_user.id  # Получаем уникальный ID пользователя
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
        f"Уровень активности: {user_dict[user_id].get('activity_level')} минут в день\n"
        f"Город: {user_dict[user_id].get('city')}\n"

        f"Рекомендуемая суточная норма калорий для ваших параметров: {calories_norm}\n"
        f"Рекомендуемая суточная норма воды для ваших параметров: {water_norm}"
    )

    await message.answer(confirmation_message)
    await message.answer(text='Спасибо!\nЕсли хотите, можете указать свою цель по '
                         'количеству потребляемых калорий в день, отличную от '
                         'суточной нормы, либо напишите "нет"')
    await state.set_state(Form.calories_goal)  # Переходим к состоянию подтверждения

    # Обработчик ввода цели по калориям
async def process_calorie_goal_sent(message: types.Message, state: FSMContext):
    user_id = message.from_user.id  # Получаем уникальный ID пользователя
    # Устанавливаем состояние ожидания ввода целевого уровня калорий
    if message.text != 'нет':
        # Сохраняем введенное количество калорий в словаре пользователей по ключу "calories_goal"
        user_dict[user_id]['calories_goal'] = message.text
        await message.answer('Данные приняты')
    else:
        user_dict[user_id]['calories_goal'] = None
        await message.answer('Ну и живи, как знаешь!')
    await message.answer("Если все верно, напишите 'да', если хотите изменить данные - напишите 'нет'")
    await state.set_state(Form.confirmation)  # Переходим к состоянию подтверждения


# Обработчик подтверждения данных пользователем
async def process_confirm_profile(message: types.Message, state: FSMContext):
    await message.answer("Ваш профиль успешно сохранен!")
    # Завершаем состояние после обработки
    await state.clear()


# Обработчик изменения данных пользователем
async def process_change_profile(message: types.Message, state: FSMContext):
    await message.answer("Хорошо! Давайте начнем заново. "
                         "Введите команду /set_profile для повторного заполнения профиля.")
    await state.clear()  # Завершаем состояние и очищаем данные после завершения диалога


# Обработчик логирования количества выпитой воды
async def process_log_water(message: types.Message, state: FSMContext):
    # Запрашиваем количество воды
    await message.answer("Сколько миллилитров воды вы выпили?")
    # Устанавливаем состояние ожидания ввода
    await state.set_state(Form.log_water)

# Обработчик ввода количества воды
async def process_log_water_amount(message: types.Message, state: FSMContext):
    user_id = message.from_user.id  # Получаем уникальный ID пользователя
    # Сохраняем введенное значение в словарь с данными по конкретному пользователю
    water_amount = float(message.text)
    user_dict[user_id]['logged_water'] = user_dict[user_id].get('logged_water', 0) + water_amount
    await message.answer(f"До выполнения суточной нормы осталось выпить\
                          {user_dict[user_id].get('water_norm') - user_dict[user_id].get('logged_water')} мл")
    # Завершаем состояние после обработки
    await state.clear()


# Обработчик логирования количества потребленных калорий
async def process_log_food(message: types.Message, state: FSMContext):
    # Запрашиваем количество съеденного
    await message.answer("Что вы сегодня съели?")
    # Устанавливаем состояние ожидания ввода
    await state.set_state(Form.log_food_name)


async def process_log_food_name(message: types.Message, state: FSMContext):
    food_name = message.text  # Получаем название продукта от пользователя
    # Сохраняем наименование продукта в состоянии
    await state.update_data(log_food_name=food_name)
    await message.answer("Укажите вес съеденного в граммах")
    await state.set_state(Form.log_food_amount)  # Переходим к следующему состоянию


# Обработчик ввода количества еды
async def process_log_food_amount(message: types.Message, state: FSMContext):
    user_id = message.from_user.id  # Получаем уникальный ID пользователя
    food_weight = float(message.text)  # Преобразуем введенное значение в число
    user_data = await state.get_data()
    food_name = user_data.get('food_name')

    food_name = await rus_eng_translate(food_name)
    food_data = await get_calories_from_food(food_name)
    if food_data and 'foods' in food_data:
        food_info = food_data['foods'][0]
        # description = food_info.get('description', 'Нет описания')
        calories = next((nutrient['value'] for nutrient in food_info['foodNutrients'] if nutrient['nutrientName'] == 'Energy'))
        calories = calories * float(food_weight) / 100
        user_dict[user_id]['logged_calories'] = user_dict[user_id].get('logged_calories', 0) + calories
        if user_dict[user_id]['calories_goal'] is not None:
            calories_diff = float(user_dict[user_id]['calories_goal']) - user_dict[user_id]['logged_calories']

        else:
            calories_diff = user_dict[user_id]['calories_norm'] - user_dict[user_id]['logged_calories']

        if calories_diff > 0:
            await message.answer(f"Вы получили {calories} ккал. До достижения цели осталось получить {calories_diff} ккал")
        else:
            await message.answer(f"Поздравляю, вы выполнили цель по количеству калорий! {calories_diff} ккал")

    # Завершаем состояние после обработки
    await state.clear()

# Обработчик ввода логирования тренировок
async def process_log_workout(message: types.Message, state: FSMContext):
    user_id = message.from_user.id  # Получаем уникальный ID пользователя
    await message.answer("Выберите тип физической активности:", reply_markup=kb_workout)
    # Сохраняем user_id в состоянии
    await state.update_data(user_id = user_id)


async def choose_workout(callback_query, state: FSMContext):
    workout_type = callback_query.data

    # Сохраняем workout_type в состоянии
    await state.update_data(workout_type=workout_type)

    await callback_query.message.answer('Теперь введите продолжительность занятия в минутах')
    # Устанавливаем состояние ожидания ввода
    await state.set_state(Form.log_workout)


async def specify_duration(message: types.Message, state: FSMContext):

    workout_duration = int(message.text)  # Преобразуем введенное значение в число
    # Извлекаем данные из состояния
    user_data = await state.get_data()
    # workout_type = user_data.get('workout_type')
    workout_calories = float(user_data.get('workout_type'))
    user_id = user_data.get('user_id')
    weight = float(user_dict[user_id]['weight'])
    # calories_burned = get_calories_burned(workout_calories, workout_duration, weight)
    calories_burned = float(workout_calories * weight * workout_duration / 60)
    user_dict[user_id]['logged_calories'] = user_dict[user_id].get('logged_calories', 0) - calories_burned
    await message.answer(f'Поздравляю, вы сожгли {calories_burned} ккал')
    await state.clear()  # Завершаем состояние
