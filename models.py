# THIS FILE RESPONSIBLE FOR ALL THE TABLE, COLUMN AND ROWS INTO THE DATABASE

from database import Base
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, DateTime, Table
from sqlalchemy.orm import relationship

from datetime import datetime, timezone

connected_users = Table(
    "connected_users",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("room_id", Integer, ForeignKey("rooms.id"), primary_key=True)
)

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone_number = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    hashed_password = Column(String)
    rooms = relationship("Rooms", secondary=connected_users, back_populates="users")


class Messages(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    context = Column(Text)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))

    room_id = Column(Integer, ForeignKey("rooms.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))

class Rooms(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    users = relationship("Users", secondary=connected_users, back_populates="rooms")

