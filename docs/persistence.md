# Persistence (SQLAlchemy + Alembic)

Location: `persistence/`

## Install
```bash
cd persistence
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configure
Set `DATABASE_URL`, or edit `persistence/alembic.ini`.

## Run migrations
```bash
cd /Users/apple/agent-kernel-local
alembic -c persistence/alembic.ini upgrade head
```

## Generate migration
```bash
alembic -c persistence/alembic.ini revision --autogenerate -m "message"
```
