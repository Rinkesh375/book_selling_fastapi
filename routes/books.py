from fastapi import Depends, HTTPException, APIRouter, Query,status
from sqlmodel import Session, select
from database import get_session
from typing import Optional
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models.book import Book, BookCreate, BookRead, BookUpdate

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



@router.patch(
    "/{book_id}",
    response_model=BookRead,
    status_code=status.HTTP_200_OK,
)
def update_book(
    book_id: int,
    updates: BookUpdate,
    session: Session = Depends(get_session),
    api_key: str = Depends(verify_api_key),
) -> BookRead:
    book = session.get(Book, book_id)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found",
        )

    update_data = updates.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    for field, value in update_data.items():
        if isinstance(value, str):
            value = value.strip()

        setattr(book, field, value)

    try:
        session.add(book)
        session.commit()
        session.refresh(book)

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to update book due to a data conflict",
        )

    except Exception:
        session.rollback()
        raise

    return book



@router.patch(
    "/{book_id}/sold",
    response_model=BookRead,
    status_code=status.HTTP_200_OK,
)
def mark_book_sold(
    book_id: int,
    session: Session = Depends(get_session),
    api_key: str = Depends(verify_api_key),
) -> BookRead:
    book = session.get(Book, book_id)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found",
        )

    if book.is_sold:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book is already sold",
        )

    book.is_sold = True

    try:
        session.add(book)
        session.commit()
        session.refresh(book)

    except SQLAlchemyError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark book as sold",
        )

    return book