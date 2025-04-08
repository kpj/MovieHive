import pathlib
import functools

import bcrypt
from pydantic import model_validator
from pydantic_settings import BaseSettings


def get_password_hash(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password=password.encode(), salt=salt)


class Settings(BaseSettings):
    user_database_string: str
    user_database: dict[str, bytes] | None = None

    jwt_secret_key: str  # Created with `openssl rand -hex 32`.
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    datatbase_directory: pathlib.Path = pathlib.Path(".")

    @model_validator(mode="after")
    def check_passwords_match(self) -> "Settings":
        if self.user_database is not None:
            raise ValueError("`user_database` should not be set.")

        self.user_database = {
            user: {"username": user, "hashed_password": get_password_hash(pw)}
            for user, pw in (
                entry.split(":") for entry in self.user_database_string.split()
            )
        }

        return self


@functools.lru_cache
def get_settings() -> Settings:
    return Settings()
