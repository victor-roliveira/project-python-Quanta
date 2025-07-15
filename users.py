from sqlalchemy import Table, Column, Integer, String, MetaData
from db import engine, SessionLocal
from auth import hash_password, verify_password

metadata = MetaData()

users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, nullable=False),
    Column("password", String, nullable=False),
    Column("role", String, default="comum")
)

metadata.create_all(engine)

def create_user(username, password, role="comum"):
    session = SessionLocal()
    hashed = hash_password(password)
    session.execute(users.insert().values(username=username, password=hashed, role=role))
    session.commit()
    session.close()

def authenticate_user(username, password):
    session = SessionLocal()
    user = session.execute(users.select().where(users.c.username == username)).fetchone()
    session.close()

    if user and verify_password(password, user.password):
        return {"username": user.username, "role": user.role}
    return None