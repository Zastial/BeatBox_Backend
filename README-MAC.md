# Beatbox

## Getting started

### Python 3.12

Install Python 3.12 using Homebrew:

```
brew install python@3.12
```

Ensure the correct version is used:
```
echo 'export PATH="/opt/homebrew/opt/python@3.12/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### PostgreSQL

If you don't have PostgreSQL installed, you can install it with Homebrew:
```
brew install postgresql@17
```

Start the PostgreSQL service:
```
brew services start postgresql@17
```

Create a user and database:
```
psql postgres
CREATE USER dipou WITH CREATEDB PASSWORD 'your_password';
CREATE DATABASE musicDB OWNER dipou;
```

### Poetry

Install Poetry (https://python-poetry.org/docs/#installation):
```
curl -sSL https://install.python-poetry.org | python3 -
```

Ensure Poetry is in the PATH:
```
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Install the dependencies for this project:
```
cd /path/to/your/project
poetry env use 3.12
poetry install
poetry shell
```

### Uvicorn

You can launch the Uvicorn server:
```
cd /path/to/your/project
uvicorn beatbox_backend.main:app --port 8000 --reload
```

### Alembic

Each time the PostgreSQL schema is modified (new table, new field, etc.), we need to generate a migration with Alembic:

```
alembic revision --autogenerate -m "Revision Message"
```

This will generate a new file in the `migrations` folder; the result file may not be perfect and should be checked and adjusted if needed.
See: https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect

The database will be automatically upgraded during the next restart of the application.

The whole `migrations` folder has been generated with the command:

```
alembic init -t async migrations
```

The `env.py` and `script.py.mako` files were then modified with the help of this tutorial: https://medium.com/@kasperjuunge/how-to-get-started-with-alembic-and-sqlmodel-288700002543
Each new model added to the application must be imported in the `env.py` file for the `alembic revision --autogenerate` to detect it.

Alternatively, the migration can be tested locally with the CLI:

```
alembic upgrade head
```

The `alembic-postgresql-enum` library (https://pypi.org/project/alembic-postgresql-enum/) was used to handle the enum changes in the Alembic migrations.
If we ever need the same for functions, views, or triggers, we will need to install `alembic_utils` (https://olirice.github.io/alembic_utils/).

