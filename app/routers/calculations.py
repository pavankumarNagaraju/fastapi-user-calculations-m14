# app/routers/calculations.py

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/calculations",
    tags=["calculations"],
)


def perform_operation(operation: str, operand1: float, operand2: float) -> float:
    """
    Simple arithmetic engine for the calculator.
    Supports: add, subtract, multiply, divide.
    """
    op = operation.lower()
    if op == "add":
        return operand1 + operand2
    elif op == "subtract":
        return operand1 - operand2
    elif op == "multiply":
        return operand1 * operand2
    elif op == "divide":
        if operand2 == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot divide by zero",
            )
        return operand1 / operand2
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported operation '{operation}'",
        )


@router.get("/", response_model=List[schemas.CalculationRead])
def browse_calculations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Browse: return all calculations for the current user.
    """
    calculations = (
        db.query(models.Calculation)
        .filter(models.Calculation.user_id == current_user.id)
        .order_by(models.Calculation.id)
        .all()
    )
    return calculations


@router.post(
    "/", response_model=schemas.CalculationRead, status_code=status.HTTP_200_OK
)
def add_calculation(
    calc_in: schemas.CalculationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Add: create a new calculation for the current user.
    """
    result = perform_operation(
        calc_in.operation, calc_in.operand1, calc_in.operand2
    )

    calc = models.Calculation(
        user_id=current_user.id,
        operation=calc_in.operation,
        operand1=calc_in.operand1,
        operand2=calc_in.operand2,
        result=result,
        created_at=datetime.utcnow(),  # deprecation warning is fine for now
    )
    db.add(calc)
    db.commit()
    db.refresh(calc)
    return calc


@router.get("/{calc_id}", response_model=schemas.CalculationRead)
def read_calculation(
    calc_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Read: get a single calculation by ID for the current user.
    """
    calc = db.query(models.Calculation).get(calc_id)
    if not calc or calc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found",
        )
    return calc


@router.put("/{calc_id}", response_model=schemas.CalculationRead)
@router.patch("/{calc_id}", response_model=schemas.CalculationRead)
def edit_calculation(
    calc_id: int,
    calc_in: schemas.CalculationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Edit: update an existing calculation and persist new result.
    Accepts same fields as CalculationCreate.
    """
    calc = db.query(models.Calculation).get(calc_id)
    if not calc or calc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found",
        )

    calc.operation = calc_in.operation
    calc.operand1 = calc_in.operand1
    calc.operand2 = calc_in.operand2
    calc.result = perform_operation(
        calc_in.operation, calc_in.operand1, calc_in.operand2
    )

    db.commit()
    db.refresh(calc)
    return calc


@router.delete("/{calc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(
    calc_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Delete: remove a calculation by ID for the current user.
    Returns HTTP 204 No Content on success (what your test expects).
    """
    calc = db.query(models.Calculation).get(calc_id)
    if not calc or calc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found",
        )

    db.delete(calc)
    db.commit()
    # 204 No Content → return nothing
    return None
