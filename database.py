


#SQLAlchemy is an ORM.Object Relational Mapper
#Helps execute queries using methods.
#Define the table structure using classes and objects.

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey

class Base(DeclarativeBase):
    pass


#Map users table to User class
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(100))
    age: Mapped[int] = mapped_column()

class Authentication(Base):
    __tablename__ = "user_authentication"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[DateTime] = mapped_column(DateTime)