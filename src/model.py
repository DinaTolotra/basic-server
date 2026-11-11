from datetime import datetime, timezone
from typing import Annotated, Optional

from sqlmodel import SQLModel, Field as sqlField


class User(SQLModel, table=True):
    id: Annotated[Optional[int], sqlField(default=None, primary_key=True)]
    username: Annotated[str, sqlField(max_length=150)]
    email: Annotated[str, sqlField(max_length=150, unique=True)]
    created_at: Annotated[Optional[datetime], sqlField(default_factory=lambda: datetime.now(timezone.utc))]
    updated_at: Annotated[Optional[datetime], sqlField(default=None)]


class Project(SQLModel, table=True):
    id: Annotated[Optional[int], sqlField(default=None, primary_key=True)]
    owner_id: Annotated[int, sqlField(foreign_key="user.id", ondelete="CASCADE")]
    name: Annotated[str, sqlField(max_length=150)]
    description: Annotated[Optional[str], sqlField(default=None)]
    created_at: Annotated[Optional[datetime], sqlField(default_factory=lambda: datetime.now(timezone.utc))]
    updated_at: Annotated[Optional[datetime], sqlField(default=None)]


class Item(SQLModel, table=True):
    id: Annotated[Optional[int], sqlField(default=None, primary_key=True, unique=True)]
    project_id: Annotated[int, sqlField(foreign_key="project.id", ondelete="CASCADE")]
    title: Annotated[str, sqlField(max_length=200)]
    description: Annotated[str, sqlField()]
    status: Annotated[str, sqlField(default="TODO")]
    priority: Annotated[int, sqlField(default=1, ge=0, le=2)]
    due_date: Annotated[datetime, sqlField()]
    created_at: Annotated[Optional[datetime], sqlField(default_factory=lambda: datetime.now(timezone.utc))]
    updated_at: Annotated[Optional[datetime], sqlField(default=None)]
