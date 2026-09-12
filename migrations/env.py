import sys

from os.path import abspath, dirname

# Asegura que Python encuentre la carpeta raíz del proyecto
# Esto sube dos niveles desde migrations/env.py hasta la raíz
sys.path.insert(0, dirname(dirname(abspath(__file__))))


from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context


# Importación de los modelos
from app.database.base import Base
from app.models.users import Users
from app.models.business import Business
from app.models.user_business import UserBusiness
from app.models.recovery import Recovery

# Importamos la variable de entorno ya procesada
from app.config.settings import DATABASE_URL


# Configuración de Alembic
config = context.config


# Configuración del logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Configuración de la conexión a la BD
if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)


# Metadata de los modelos para autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Aquí es donde Alembic lee el "sqlalchemy.url" que inyectamos arriba
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
