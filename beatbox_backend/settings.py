from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    postgres_dsn: str = "postgresql://dipou:dipou@localhost:5431/musicDB"


settings = Settings()
