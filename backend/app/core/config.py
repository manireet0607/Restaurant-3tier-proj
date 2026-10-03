"""Application settings. Everything sensitive comes from environment variables."""
from decimal import Decimal
from functools import lru_cache
from typing import List, Optional
from urllib.parse import quote_plus

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "development"  # development | production
    APP_NAME: str = "Dragon Wok API"
    LOG_LEVEL: str = "INFO"

    # Security
    SECRET_KEY: str = "change-me-in-development-only"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS (comma separated list)
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Database. Works for local MySQL and Amazon RDS MySQL.
    DATABASE_URL: Optional[str] = None  # optional full override (used by tests)
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "dragonwok"
    DB_PASSWORD: str = ""
    DB_NAME: str = "dragonwok"
    # TLS. For RDS set DB_SSL_CA to the path of the AWS RDS CA bundle.
    DB_SSL_CA: Optional[str] = None
    DB_SSL_VERIFY: bool = True

    # Business rules
    DELIVERY_FEE: Decimal = Decimal("40.00")
    TAX_PERCENT: Decimal = Decimal("5.00")

    # First admin (used by the seed script)
    ADMIN_EMAIL: str = "admin@dragonwok.local"
    ADMIN_PASSWORD: str = ""

    @field_validator("DB_SSL_VERIFY", mode="before")
    @classmethod
    def _bool(cls, v):
        if isinstance(v, str):
            return v.strip().lower() in {"1", "true", "yes", "on"}
        return v

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def sqlalchemy_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"mysql+pymysql://{quote_plus(self.DB_USER)}:{quote_plus(self.DB_PASSWORD)}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    @property
    def connect_args(self) -> dict:
        if self.DATABASE_URL or not self.DB_SSL_CA:
            return {}
        # Verify the server certificate and host name against the RDS CA bundle.
        return {
            "ssl": {"ca": self.DB_SSL_CA},
            "ssl_verify_cert": self.DB_SSL_VERIFY,
            "ssl_verify_identity": self.DB_SSL_VERIFY,
        }


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    if s.is_production and (s.SECRET_KEY.startswith("change-me") or len(s.SECRET_KEY) < 32):
        raise RuntimeError("Set a strong SECRET_KEY (32+ characters) in production.")
    return s
