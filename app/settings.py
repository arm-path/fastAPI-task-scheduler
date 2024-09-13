from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class SiteSettings(BaseModel):
    PROTOCOL: str
    DOMAIN: str
    ADDRESS: str
    PORT: int
    NAME: str

    @property
    def URL_ADDRESS(self):
        return f'{self.PROTOCOL}://{self.DOMAIN}:{self.PORT}/'


class DatabasePGSettings(BaseModel):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    ENGINE_ECHO: bool = False

    CONVENTION: dict[str, str] = {
        'ix': 'ix_%(column_0_label)s',
        'uq': 'uq_%(table_name)s_%(column_0_N_name)s',
        'ck': 'ck_%(table_name)s_%(constraint_name)s',
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
        'pk': 'pk_%(table_name)s',
    }

    @property
    def POSTGRES_URL(self):
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}/{self.POSTGRES_DB}'


class SecuritySettings(BaseModel):
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int
    VERIFY_URL_SECRET_KEY: str


class EmailSettings(BaseModel):
    HOST: str
    PORT: int
    LOGIN: str
    PASSWORD: str


class Settings(BaseSettings):
    site: SiteSettings
    database: DatabasePGSettings
    security: SecuritySettings
    email: EmailSettings
    model_config = SettingsConfigDict(env_file=('.env.template', '.env'),
                                      env_nested_delimiter="__",
                                      case_sensitive=False
                                      )


settings = Settings()
