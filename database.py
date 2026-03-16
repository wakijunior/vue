


#SQLAlchemy is an ORM.Object Relational Mapper
#Helps execute queries using methods.
#Define the table structure using classes and objects.

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String

class Base(DeclarativeBase):
    pass

#Map users table to User class
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(100))
    age: Mapped[int] = mapped_column()