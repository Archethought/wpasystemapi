from pydantic import BaseSettings

class Settings(BaseSettings):
    wpa_supplicant_file_path: str = "./wpa_supplicant.conf"

    class Config:
        env_prefix = "APP_"
        env_file = ".env"

