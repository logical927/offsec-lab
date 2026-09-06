import logging
import os
from dataclasses import dataclass

import psycopg
from sqlalchemy import URL

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DatabaseSettings:
    database: str
    user: str
    password: str
    host: str
    port: int

    @classmethod
    def from_environment(cls) -> "DatabaseSettings":
        required = ("POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST")
        values = {name: os.getenv(name) for name in required}
        if any(not value for value in values.values()):
            raise ValueError("Required database configuration is missing.")

        return cls(
            database=values["POSTGRES_DB"],
            user=values["POSTGRES_USER"],
            password=values["POSTGRES_PASSWORD"],
            host=values["POSTGRES_HOST"],
            port=int(os.getenv("POSTGRES_PORT", "5432")),
        )

    def sqlalchemy_url(self) -> URL:
        """Build a safely escaped URL without serializing credentials to logs."""
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )


async def check_database_connection() -> bool:
    """Return whether PostgreSQL accepts a query without exposing connection details."""
    try:
        settings = DatabaseSettings.from_environment()
        connection = await psycopg.AsyncConnection.connect(
            dbname=settings.database,
            user=settings.user,
            password=settings.password,
            host=settings.host,
            port=settings.port,
            connect_timeout=3,
        )
        async with connection:
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT 1")
                row = await cursor.fetchone()
        return row == (1,)
    except (OSError, psycopg.Error, TypeError, ValueError):
        logger.warning("event=DATABASE_HEALTH_CHECK result=failed")
        return False
