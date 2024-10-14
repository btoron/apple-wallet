import pytest
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file="tests/.env", env_prefix="TEST_")
    passId: str


@pytest.fixture(scope="session", autouse=True)
def test_settings() -> TestSettings:
    return TestSettings()
