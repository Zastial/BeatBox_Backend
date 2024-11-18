# Beatbox

## Getting started

### Python 3.12

Install python3.12

```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev libpq-dev
```

### Postgres

If you don't have postgres installed, you can install it with the following command :
```
sudo apt install postgresql
```

Locally, you will need to have a postgres user to handle the database

```
sudo systemctl start postgresql
sudo su - postgres
createuser -d dipou -P
createdb musicDB
```

### Poetry

Install Poetry (https://python-poetry.org/docs/#installation) :
```
curl -sSL https://install.python-poetry.org | python3 -
```

Install the dependencies for this project :
```
cd /path/to/your/project
poetry env use 3.12
poetry install
poetry shell
```

### Uvicorn

You can launch the uvicorn server
```
cd /path/to/your/project
uvicorn beatbox_backend.main:app --port 8000 --reload
```
### Alembic

Each time the postgresSQL schema is modified (new table, new field, etc.), we need to generate a migration with Alembic :

```
alembic revision --autogenerate -m "Revision Message"
```

This will generate a new file in the `migrations` folder ; the result file may not be perfect and should be checked adjusted if needed.
See : https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect

The database will be automatically upgraded during the next restart of the application.

The whole `migrations` folder has been generated with the command :

```
alembic init -t async migrations
```

The env.py and script.py.mako files were then modified with the help of this tutorial : https://medium.com/@kasperjuunge/how-to-get-started-with-alembic-and-sqlmodel-288700002543
Each new model added to the application must be imported in the env.py file for the `alembic revision --autogenerate` to detect it.


Alternatively, the migration can be tested locally with the CLI :

```
alembic upgrade head
```

The `alembic-postgresql-enum` library (https://pypi.org/project/alembic-postgresql-enum/) was used to handle the enum changes in the Alembic migrations.
If we ever need the same for functions, views or triggers, we will need to install `alembic_utils` (https://olirice.github.io/alembic_utils/)