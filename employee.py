"""
FastAPI application for employees.json
Run with: uvicorn employees_api:app --reload
Swagger UI: http://127.0.0.1:8000/docs
"""

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Employees API")

DATA_FILE = Path("employees.json")


# ---------- Pydantic model for validating a new employee ----------
class Employee(BaseModel):
    name: str
    department: str
    salary: float = Field(gt=0, description="Salary must be a positive number")
    experience_years: int = Field(ge=0, description="Experience years cannot be negative")


# ---------- Helper functions to read/write the JSON file ----------
def read_employees():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def write_employees(employees):
    with open(DATA_FILE, "w") as f:
        json.dump(employees, f, indent=4)


# ---------- (A) GET all employees ----------
@app.get("/employees")
def get_employees():
    return read_employees()


# ---------- (A) DELETE an employee by id ----------
@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    employees = read_employees()
    updated_employees = [e for e in employees if e["id"] != employee_id]

    if len(updated_employees) == len(employees):
        raise HTTPException(status_code=404, detail=f"Employee with id {employee_id} not found")

    write_employees(updated_employees)
    return {"message": f"Employee with id {employee_id} deleted successfully"}


# ---------- (B) GET employees sorted by salary (descending) ----------
@app.get("/employees/sorted")
def get_employees_sorted_by_salary():
    employees = read_employees()

    for emp in employees:
        emp["bonus"] = round(emp["salary"] * 0.10, 2)

    sorted_employees = sorted(employees, key=lambda e: e["salary"], reverse=True)
    return sorted_employees


# ---------- (C) POST a new employee ----------
@app.post("/employees")
def add_employee(employee: Employee):
    employees = read_employees()

    # Raise 402 if the employee already exists (same name)
    if any(e["name"].lower() == employee.name.lower() for e in employees):
        raise HTTPException(status_code=402, detail="This employee already exists")

    new_id = max((e["id"] for e in employees), default=0) + 1
    new_employee = {"id": new_id, **employee.dict()}
    employees.append(new_employee)
    write_employees(employees)

    print(f"Employee '{employee.name}' added successfully")
    return {"message": f"Employee '{employee.name}' added successfully", "employee": new_employee}
