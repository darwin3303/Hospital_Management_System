from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str = "development"
    DATABASE_URL: str
    JWT_SECRET: str
    REFRESH_SECRET: str
    ACCESS_TOKEN_TTL_MINUTES: int = 30
    REFRESH_TOKEN_TTL_DAYS: int = 7
    CLIENT_ORIGIN: str = "http://localhost:5173"
    BCRYPT_ROUNDS: int = 12

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
