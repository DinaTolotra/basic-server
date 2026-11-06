from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from sqlmodel import Session, SQLModel, select

from .database import create_db_and_tables, get_session
from .model import Item, Project, User


class UserCreate(BaseModel):
    username: str = Field(max_length=150)
    email: str = Field(max_length=150)


class ProjectCreate(BaseModel):
    owner_id: int
    name: str = Field(max_length=150)
    description: str | None = None


class ItemCreate(BaseModel):
    project_id: int
    title: str = Field(max_length=200)
    description: str
    status: str = "TODO"
    priority: int = Field(default=1, ge=0, le=2)
    due_date: datetime


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Caching Demo API", lifespan=lifespan)
SessionDependency = Annotated[Session, Depends(get_session)]


def require_parent(session: Session, model: type[SQLModel], identifier: int, name: str) -> None:
    if session.get(model, identifier) is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            f"{name} with id {identifier} not found",
        )


def get_record(session: Session, model: type[SQLModel], identifier: int, name: str):
    record = session.get(model, identifier)
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"{name} with id {identifier} not found")
    return record


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, session: SessionDependency):
    user = User(**payload.model_dump())
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.get("/users", response_model=list[User])
def list_users(
    session: SessionDependency,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
):
    return session.exec(select(User).offset(offset).limit(limit)).all()


@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: int, session: SessionDependency):
    return get_record(session, User, user_id, "user")


@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, payload: UserCreate, session: SessionDependency):
    user = get_record(session, User, user_id, "user")
    for field, value in payload.model_dump().items():
        setattr(user, field, value)
    user.updated_at = datetime.now(timezone.utc)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: SessionDependency):
    user = get_record(session, User, user_id, "user")
    session.delete(user)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, session: SessionDependency):
    require_parent(session, User, payload.owner_id, "user")
    project = Project(**payload.model_dump())
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@app.get("/projects", response_model=list[Project])
def list_projects(
    session: SessionDependency,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
):
    return session.exec(select(Project).offset(offset).limit(limit)).all()


@app.get("/projects/{project_id}", response_model=Project)
def read_project(project_id: int, session: SessionDependency):
    return get_record(session, Project, project_id, "project")


@app.put("/projects/{project_id}", response_model=Project)
def update_project(project_id: int, payload: ProjectCreate, session: SessionDependency):
    require_parent(session, User, payload.owner_id, "user")
    project = get_record(session, Project, project_id, "project")
    for field, value in payload.model_dump().items():
        setattr(project, field, value)
    project.updated_at = datetime.now(timezone.utc)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, session: SessionDependency):
    project = get_record(session, Project, project_id, "project")
    session.delete(project)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, session: SessionDependency):
    require_parent(session, Project, payload.project_id, "project")
    item = Item(**payload.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@app.get("/items", response_model=list[Item])
def list_items(
    session: SessionDependency,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
):
    return session.exec(select(Item).offset(offset).limit(limit)).all()


@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int, session: SessionDependency):
    return get_record(session, Item, item_id, "item")


@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, payload: ItemCreate, session: SessionDependency):
    require_parent(session, Project, payload.project_id, "project")
    item = get_record(session, Item, item_id, "item")
    for field, value in payload.model_dump().items():
        setattr(item, field, value)
    item.updated_at = datetime.now(timezone.utc)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, session: SessionDependency):
    item = get_record(session, Item, item_id, "item")
    session.delete(item)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)