from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas

router = APIRouter(prefix="/auth", tags=["Auth - Login / LoginScreen"])


@router.post("/login/", response_model=schemas.LoginResponse)
def login(payload: schemas.LoginInput, db: Session = Depends(get_db)):

    user = (
        db.query(models.User)
        .filter(models.User.email == payload.email.strip())
        .first()
    )
    if not user or user.password != payload.password:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if user.status != "Active":
        raise HTTPException(status_code=403, detail="Account is inactive.")

    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)

    return {"user": user}


@router.post("/logout/", status_code=204)
def logout(payload: dict, db: Session = Depends(get_db)):
    return None