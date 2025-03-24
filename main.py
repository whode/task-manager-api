from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, Enum as SQLEnum
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, validator
from enum import Enum

# Database configuration (using SQLite for testing; update to PostgreSQL in production)
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- ENUMs ---
class TaskStatus(str, Enum):
    to_do = "to do"
    in_progress = "in progress"
    done = "done"

class SortBy(str, Enum):
    created_at = "created_at"
    due_date = "due_date"

# SQLAlchemy model for Task
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.to_do, nullable=False)  # Используем Enum
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime, nullable=True)

Base.metadata.create_all(bind=engine)

# Pydantic schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    status: Optional[TaskStatus] = TaskStatus.to_do # default

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None

class TaskOut(TaskBase):
    id: int
    status: TaskStatus
    created_at: datetime

    class Config:
        from_attributes = True

app = FastAPI(title="Task Manager API")

# Dependency for getting the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/tasks/", response_model=TaskOut)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task."""
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks/", response_model=List[TaskOut])
def read_tasks(
    status: Optional[TaskStatus] = Query(None),
    sort_by: SortBy = Query(SortBy.created_at),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Retrieve tasks with optional filtering and sorting."""
    query = db.query(Task)
    if status:
        query = query.filter(Task.status == status)

    query = query.order_by(getattr(Task, sort_by.value))
    return query.offset(offset).limit(limit).all()

@app.get("/tasks/{task_id}", response_model=TaskOut)
def read_task(task_id: int, db: Session = Depends(get_db)):
    """Get a task by its ID."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """Update an existing task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task_update.dict(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}