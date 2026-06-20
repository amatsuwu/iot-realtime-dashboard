from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "即時資料分析與監控系統"
    API_V1_STR: str = "/api/v1"
    
    JWT_SECRET_KEY: str = "your_super_secret_jwt_key_here"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    MARIADB_USER: str = "root"
    MARIADB_PASSWORD: str = "my_secure_password"
    MARIADB_HOST: str = "db"
    MARIADB_PORT: int = 3306
    MARIADB_DATABASE: str = "monitor_db"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+asyncmy://{self.MARIADB_USER}:{self.MARIADB_PASSWORD}@{self.MARIADB_HOST}:{self.MARIADB_PORT}/{self.MARIADB_DATABASE}"
        
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
