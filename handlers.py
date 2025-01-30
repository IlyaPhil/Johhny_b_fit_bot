from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from functions import calculate_daily_needs, get_calories_from_food
from googletrans import Translator


# Словарь для хранения данных пользователей
user_dict = {}

# Cоздаем класс, для группы состояний нашего FSM
class Form(StatesGroup):
    gender = State()
    weight = State()
    height = State()
    age = State()
    activity_level = State()
    city = State()
    calorie_goal = State()
    confirmation = State()  # состояние для подтверждения
    log_water = State() # логирование воды
    log_food = State() # логирование воды

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
async def process_set_profile_cmd(message: types.Message, state: Form):
    user_id = message.from_user.id  # Получаем уникальный ID пользователя
    user_dict[user_id] = {}  # создаем словарь для нового пользователя
    await message.answer('Введите ваш пол: м или ж')
    await state.set_state(Form.gender)  # Устанавливаем состояние ожидания ввода пола


# Обработчик ввода пола
# @dp.message(StateFilter(Form.gender), F.text.lower() in ('м', 'ж'))
async def process_gender_sent(message: types.Message, state: FSMContext):
    user_id = message.from_user.id  # Получаем уникальный ID пользователя
    # Сохраняем введенный пол в словаре пользователей по ключу "gender"
    user_dict[user_id]['gender'] = message.text

    await message.answer(text='Спасибо!\n\nА теперь введите ваш вес в кг')
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
async def process_age_sent(message: types.Message, state: FSMContext):
    # Cохраняем введенный вес в хранилище по ключу "age"
    user_id = message.from_user.id  # Получаем уникальный ID пользователя
    user_dict[user_id]['age'] = message.text
    await message.answer(text='Спасибо!\n\nА теперь введите ваш уровень '
                          'физической активности (минут в день)')
    # Устанавливаем состояние ожидания ввода уровня физической активности
    await state.set_state(Form.activity_level)


# Обработчик ввода уровня физической активности
# @dp.message(StateFilter(Form.activity_level), F.text.isdigit())
async def process_activity_sent(message: types.Message, state: FSMContext):
    # Cохраняем введенный вес в хранилище по ключу "activity_level"
    user_id = message.from_user.id  # Получаем уникальный ID пользователя
    user_dict[user_id]['activity_level'] = message.text

    await message.answer(text='Спасибо!\n\nА теперь введите название города, '
                         'в котором вы проживаете')
    # Устанавливаем состояние ожидания ввода города
    await state.set_state(Form.city)


# Обработчик ввода города
# @dp.message(StateFilter(Form.city), F.text.isalpha())
async def process_city_sent(message: types.Message, state: FSMContext):
    # Cохраняем введенный вес в хранилище по ключу "city"
    user_id = message.from_user.id  # Получаем уникальный ID пользователя
    user_dict[user_id]['city'] = message.text

    await message.answer(text='Спасибо!\n\nА теперь введите желаемое '
                         'количество потребляемых калорий в день')
    # Устанавливаем состояние ожидания ввода целевого уровня калорий
    await state.set_state(Form.calorie_goal)
    state.update_data(calorie_goal_level=message.text)


# Обработчик ввода цели по калориям
# @dp.message(StateFilter(Form.calorie_goal), F.text.isdigit())
async def process_calorie_goal_sent(message: types.Message, state: FSMContext):
    user_id = message.from_user.id  # Получаем уникальный ID пользователя
    # Сохраняем введенное количество калорий в словаре пользователей по ключу "calorie_goal"
    user_dict[user_id]['calorie_goal'] = message.text

    # Рассчитываем дневную норму калорий и воды
    calories_norm, water_norm = await calculate_daily_needs(user_dict[user_id])
    # Записываем рассчитанные значения в словарь
    user_dict[user_id]['calories norm'] = calories_norm
    user_dict[user_id]['water norm'] = water_norm

    # Формируем сообщение с подтверждением введенных данных
    confirmation_message = (
        f"Ваш профиль:\n"
        f"Пол: {user_dict[user_id].get('gender')}\n"
        f"Вес: {user_dict[user_id].get('weight')} кг\n"
        f"Рост: {user_dict[user_id].get('height')} см\n"
        f"Возраст: {user_dict[user_id].get('age')} лет\n"
        f"Уровень активности: {user_dict[user_id].get('activity_level')} минут в день\n"
        f"Город: {user_dict[user_id].get('city')}\n"
        f"Цель по калориям: {user_dict[user_id].get('calorie_goal')} калорий в день\n"
        f"Рекомендуемая суточная норма калорий для ваших параметров: {calories_norm}\n"
        f"Рекомендуемая суточная норма воды для ваших параметров: {water_norm}\n"
        f"\nЕсли все верно, напишите 'да', если хотите изменить данные - напишите 'нет'."
    )

    await message.answer(confirmation_message)
    await state.set_state(Form.confirmation)  # Переходим к состоянию подтверждения


# Обработчик подтверждения данных пользователем
# @dp.message(StateFilter(Form.confirmation), F.text.lower() == 'да')
async def process_confirm_profile(message: types.Message, state: FSMContext):
    await message.answer("Ваш профиль успешно сохранен!")
    await state.clear()  # Завершаем состояние и очищаем данные после завершения диалога


# Обработчик изменения данных пользователем
# @dp.message(StateFilter(Form.confirmation), F.text.lower() == 'нет')
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
                          {user_dict[user_id].get('water norm') - user_dict[user_id].get('logged_water')} мл")
    # Завершаем состояние после обработки
    await state.clear()


# Обработчик логирования количества потребленных калорий
async def process_log_food(message: types.Message, state: FSMContext):
    # Запрашиваем количество съеденного
    await message.answer("Что вы сегодня съели?\n"
                         "Введите в формате <еда> <вес в граммах>")
    # Устанавливаем состояние ожидания ввода
    await state.set_state(Form.log_food)


# Обработчик ввода количества воды
async def process_log_food_amount(message: types.Message, state: FSMContext):
    user_id = message.from_user.id  # Получаем уникальный ID пользователя
    # Сохраняем введенное значение в словарь с данными по конкретному пользователю
    *food_name, food_weight = message.text.split()
    food_data = await get_calories_from_food(food_name, food_weight)
    if food_data and 'foods' in food_data:
        food_info = food_data['foods'][0]
        # description = food_info.get('description', 'Нет описания')
        calories = next((nutrient['value'] for nutrient in food_info['foodNutrients'] if nutrient['nutrientName'] == 'Energy'))
        calories = calories * food_weight / 100
        user_dict[user_id]['logged_calories'] = user_dict[user_id].get('logged_calories', 0) + calories
        if user_dict[user_id]['logged_calories'] >= user_dict[user_id]['calories_goal']:

        # response_message = f"Продукт: {description}\nКалории: {calories} ккал"
        await message.answer(response_message)
    else:
        await message.answer("Продукт не найден.")

    # Завершаем состояние после обработки
    await state.clear()
