from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    This class represents application configuration.

    Pydantic will automatically read values from
    environment variables or our .env file.
    """

    # PostgreSQL connection URL.
    #
    # Because we declare this as a string without a default,
    # Pydantic requires DATABASE_URL to exist.
    database_url: str

    # Tell Pydantic to load variables from the .env file.
    #
    # env_file=".env"
    # means:
    #
    # Look for a file called ".env" in the project directory.
    #
    # extra="ignore"
    # means:
    #
    # If .env contains some settings that aren't defined in
    # this class yet, don't raise an error.
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


# Create one Settings object for the application.
#
# Other files will import:
#
# from app.config import settings
#
# instead of creating Settings() repeatedly.
settings = Settings()