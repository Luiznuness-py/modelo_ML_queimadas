import __main__
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from sqlalchemy.engine.url import URL


def get_project_root():
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / "pyproject.toml").exists():
            root = parent
            break
    else:
        root = Path.cwd()
            
    data_dir = root / "data"
    if not data_dir.exists():
        print(f"⚠️  Aviso: A pasta 'data/' não foi encontrada em {root}")
            
    return root

PROJECT_ROOT = get_project_root()

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / '.env'),
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

    PATH_ARQUIVOS_CSV: str = Field(default=str(PROJECT_ROOT / "data/"), description="Path to CSV files")
    
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