from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True)
    colleage: str

    # one to many relationship
    books: list["Book"] = Relationship(back_populates="owner")


class UserRead(SQLModel):
    id:int
    name:str
    email:str
    colleage:str


class CreateUser(SQLModel):
    name:str
    email:str
    colleage:str


from models.book import Book

User.model_rebuild()