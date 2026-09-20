import os
import logging
from fastapi import FastAPI, HTTPException, Depends, status, Request
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, or_, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("profind_backend")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://profind_db_user:tWWichGQvmQJmouzxfMCmeCbxYNr2lu4@dpg-dansmln40ujc73d1ksi0-a/profind_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

class MessageDB(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ProFind Backend")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Server is alive"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class MessageCreate(BaseModel):
    sender_id: int
    receiver_id: int
    text: str

@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    if not username or not username.strip() or not password:
        raise HTTPException(status_code=400, detail="Заполните все поля")
    existing = db.query(UserDB).filter(UserDB.username == username.strip()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
    new_user = UserDB(username=username.strip(), password=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username}

@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == username.strip(), UserDB.password == password).first()
    if not user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    return {"id": user.id, "username": user.username}

@app.get("/users/{username}")
def get_user(username: str, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == username.strip()).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {"id": user.id, "username": user.username}

@app.post("/messages")
def send_message(msg: MessageCreate, db: Session = Depends(get_db)):
    new_msg = MessageDB(sender_id=msg.sender_id, receiver_id=msg.receiver_id, text=msg.text)
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return {"status": "ok", "message_id": new_msg.id}

# Личные сообщения между двумя пользователями
@app.get("/messages/{user_id}/{other_user_id}")
def get_direct_messages(user_id: int, other_user_id: int, db: Session = Depends(get_db)):
    messages = db.query(MessageDB).filter(
        or_(
            and_(MessageDB.sender_id == user_id, MessageDB.receiver_id == other_user_id),
            and_(MessageDB.sender_id == other_user_id, MessageDB.receiver_id == user_id)
        )
    ).order_by(MessageDB.timestamp.asc()).all()
    
    return [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "receiver_id": m.receiver_id,
            "text": m.text,
            "timestamp": m.timestamp.isoformat()
        }
        for m in messages
    ]