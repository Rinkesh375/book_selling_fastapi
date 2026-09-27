from fastapi import Depends, HTTPException, APIRouter,status, Query
from sqlmodel import Session, select
from database import get_session
from sqlalchemy.exc import IntegrityError

from models.user import User, UserRead, CreateUser
from auth import verify_api_key

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: CreateUser,
    session: Session = Depends(get_session),
    api_key: str = Depends(verify_api_key),
) -> UserRead:

    email = user_data.email.strip().lower()

    existing_user = session.exec(
        select(User).where(User.email == email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        name=user_data.name.strip(),
        email=email,
        colleage=user_data.colleage.strip(),
    )

    try:
        session.add(user)
        session.commit()
        session.refresh(user)

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    except Exception:
        session.rollback()
        raise

    return user



@router.get(
    "/",
    response_model=list[UserRead],
    status_code=status.HTTP_200_OK,
)
def list_users(
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of users to skip",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of users to return",
    ),
    session: Session = Depends(get_session),
) -> list[UserRead]:

    statement = (
        select(User)
        .order_by(User.id)
        .offset(skip)
        .limit(limit)
    )

    return session.exec(statement).all()