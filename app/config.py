from urllib.parse import ParseResult, quote, urlparse

from pydantic import BaseSettings


class AppSettings(BaseSettings):
    debug_query: bool = False
    query_timeout_seconds: float = 60

    class Config:
        env_prefix = "app_"


class DatabaseSettings(BaseSettings):
    user: str = "app_user"

    db: str = "app_db"
    host: str = "localhost"
    password: str = "password"
    port: int = 5432

    class Config:
        env_prefix = "database_"

        # for settings, `env` is used, not `alias`
        # see https://pydantic-docs.helpmanual.io/usage/settings/#environment-variable-names for more
        fields = {
            "password": {
                "env": f"{env_prefix}pass",
            },
        }

    @property
    def async_uri(self) -> ParseResult:
        # special characters need to be encoded, i.e "@" -> "%40"
        url_safe_password = quote(self.password)
        return urlparse(
            f"postgresql+asyncpg://{self.user}:{url_safe_password}@{self.host}:{self.port}/{self.db}"
        )

    @property
    def sync_uri(self) -> ParseResult:
        return self.async_uri._replace(scheme="postgresql")


class Settings(BaseSettings):
    release_version: str = "0.0.0"
    app_settings = AppSettings()
    core_postgres_settings = DatabaseSettings()


settings = Settings()
