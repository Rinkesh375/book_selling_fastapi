from fastapi import Depends, HTTPException, APIRouter, Query,status
from sqlmodel import Session, select
from database import get_session
from typing import Optional

from models.book import Book, BookCreate, BookRead

from auth import verify_api_key

router = APIRouter(prefix="/books", tags=["books"])

@router.get(
    "/",
    response_model=list[BookRead],
    status_code=status.HTTP_200_OK,
)
def list_books(
    title: Optional[str] = Query(
        default=None,
        min_length=1,
        max_length=100,
        description="Filter books by title",
    ),
    author: Optional[str] = Query(
        default=None,
        min_length=1,
        max_length=100,
        description="Filter books by author",
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of books to skip",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of books to return",
    ),
    session: Session = Depends(get_session),
) -> list[BookRead]:

    query = select(Book).where(
        Book.is_sold.is_(False)
    )

    if title:
        title = title.strip()
        query = query.where(
            Book.title.ilike(f"%{title}%")
        )

    if author:
        author = author.strip()
        query = query.where(
            Book.author.ilike(f"%{author}%")
        )

    query = (
        query
        .order_by(Book.id)
        .offset(skip)
        .limit(limit)
    )

    return session.exec(query).all()   




@router.post(
    "/",
    response_model=BookRead,
    status_code=status.HTTP_201_CREATED,
)
def create_book(
    book_data: BookCreate,
    session: Session = Depends(get_session),
    api_key: str = Depends(verify_api_key)
) -> BookRead: 
    book = Book.model_validate(book_data)
    session.add(book)
    session.commit()
    session.refresh(book)

    return book