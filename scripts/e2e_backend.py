"""Run the real API against a disposable PostgreSQL schema, never player progress."""
import os
from uuid import uuid4

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import uvicorn

from app.database import DatabaseSettings
from app.seed import seed_mission01


def main():
    engine = create_engine(DatabaseSettings.from_environment().sqlalchemy_url())
    schema = "phase9_e2e_" + uuid4().hex
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    isolated = None
    try:
        os.environ["PGOPTIONS"] = f"-csearch_path={schema}"
        config = Config()
        config.set_main_option("script_location", "alembic")
        command.upgrade(config, "head")
        isolated = create_engine(DatabaseSettings.from_environment().sqlalchemy_url())
        with Session(isolated) as session, session.begin():
            seed_mission01(session)
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
    finally:
        if isolated is not None:
            isolated.dispose()
        with engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        engine.dispose()
        print("E2E schema removed", flush=True)


if __name__ == "__main__":
    main()
