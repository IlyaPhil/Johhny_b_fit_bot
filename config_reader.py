from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    # Вместо str используем SecretStr
    bot_token: SecretStr
    weather_api_key: SecretStr

    # В данном случае будет использоваться файла .env, который будет прочитан
    # с кодировкой UTF-8
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


# При импорте файла сразу создастся
# и провалидируется объект конфига,
# который можно далее импортировать из разных мест
config = Settings()
