from config_reader import config
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
# Импортируем хэндлеры из fsm_handlers.py
from handlers import (
    process_start_cmd,
    process_help_cmd,
    process_cancel_cmd,
    process_set_profile_cmd,
    process_gender_sent,
    process_weight_sent,
    process_height_sent,
    process_age_sent,
    process_activity_sent,
    process_city_sent,
    process_calorie_goal_sent,
    process_confirm_profile,
    process_change_profile,
    process_log_water,
    process_log_water_amount,
    process_log_food,
    process_log_food_amount,
    Form
)


# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=config.bot_token.get_secret_value())

# Хранилище
storage = MemoryStorage()

# Диспетчер
dp = Dispatcher(storage=storage)


# Регистрация хэндлеров
dp.message.register(process_start_cmd, Command("start"))
dp.message.register(process_help_cmd, Command("help"))
dp.message.register(process_cancel_cmd, Command(commands='cancel'))
dp.message.register(process_set_profile_cmd, Command('set_profile'))
dp.message.register(process_gender_sent, StateFilter(Form.gender), F.text.in_(['м', 'ж']))
dp.message.register(process_weight_sent, StateFilter(Form.weight), F.text.isdigit())
dp.message.register(process_height_sent, StateFilter(Form.height), F.text.isdigit())
dp.message.register(process_age_sent, StateFilter(Form.age), F.text.isdigit())
dp.message.register(process_activity_sent, StateFilter(Form.activity_level), F.text.isdigit())
dp.message.register(process_city_sent, StateFilter(Form.city), F.text.isalpha())
dp.message.register(process_calorie_goal_sent, StateFilter(Form.calorie_goal), F.text.isdigit())
dp.message.register(process_calorie_goal_sent, StateFilter(Form.calorie_goal), F.text.isdigit())
dp.message.register(process_confirm_profile, StateFilter(Form.confirmation), F.text.lower() == 'да')
dp.message.register(process_change_profile, StateFilter(Form.confirmation), F.text.lower() == 'нет')
dp.message.register(process_log_water, Command('log_water'))
dp.message.register(process_log_water_amount, StateFilter(Form.log_water), F.text.isdigit())
dp.message.register(process_log_food, Command('log_food'))
dp.message.register(process_log_food_amount, StateFilter(Form.log_food))


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
