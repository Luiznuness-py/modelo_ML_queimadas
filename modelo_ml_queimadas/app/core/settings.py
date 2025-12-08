from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from sqlalchemy.engine.url import URL

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )
    
    APP_NAME: str = Field(default="FireAI", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Debug mode")
    ENVIRONMENT: str = Field(default="development", description="Environment (development, production, test)")
    
    # Database Configuration - Using separate parameters (NOT DATABASE_URL)
    DB_USER: str = Field(default="postgres", description="Database user")
    DB_PASSWORD: str = Field(default="postgres", description="Database password")
    DB_HOST: str = Field(default="localhost", description="Database host")
    DB_PORT: int = Field(default=5432, description="Database port")
    DB_NAME: str = Field(default="DBFireAI", description="Database name")
    DB_NAME_TEST: str = Field(default="DBFireAITest", description="Test database name")
    DATABASE_ECHO: bool = Field(default=False, description="Echo SQL queries")

    PATH_ARQUIVOS_CSV: str
    
    def get_database_url(self, async_driver: bool = True, use_test_db: bool = False) -> URL:
        """
        Build database URL from separate parameters.
        
        Args:
            async_driver: If True, uses asyncpg driver. If False, uses psycopg2.
            use_test_db: If True, uses test database name instead of main database.
        
        Returns:
            str: Complete database URL
        """
                
        if use_test_db and async_driver:
            return "sqlite+aiosqlite:///:memory:"
        if use_test_db and not async_driver:
            return "sqlite:///:memory:"
        
        driver = "postgresql+asyncpg" if async_driver else "postgresql"
        db_name = self.DB_NAME_TEST if use_test_db else self.DB_NAME
        
        return URL.create(drivername=driver,
                          username=self.DB_USER,
                          password=self.DB_PASSWORD,
                          host=self.DB_HOST,
                          port=self.DB_PORT,
                          database=db_name)
        
        
settings = Settings()