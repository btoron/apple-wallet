from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_prefix="APPLE_WALLET_", frozen=True)
    template_path: Optional[str] = "templates"
    certificate_path: Optional[str] = "certificates"

    def get_template_path(self, template: str) -> Path:
        return Path(self.template_path) / f"{template}.pass"


def get_settings() -> Settings:
    return Settings()
