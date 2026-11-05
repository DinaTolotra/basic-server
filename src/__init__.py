from typing import Annotated, Any, Optional
from datetime import datetime, timezone
from enum import Enum

from fastapi import FastAPI, HTTPException, Path, Query
from sqlmodel import SQLModel, Field as sqlField, Session
from sqlmodel import create_engine
from pydantic import BaseModel, Field as pdField

from .model import Item

app = FastAPI()
DB_URL = "postgresql://taskflow:taskflow@localhost:5432/TaskFlow"
engine = create_engine(DB_URL, echo=True)


class ItemPutSchema(BaseModel):
    title: Annotated[str, pdField(max_length=200)]
    description: Annotated[str, pdField()]
    status: Annotated[str, pdField(default="TODO")]
    priority: Annotated[int, pdField(default=1, ge=0, le=2)]
    due_date: Annotated[datetime, pdField()]


@app.put("/item")
async def get_item(item: ItemPutSchema):
    data = Item(**item.model_dump())
    with Session(engine) as session:
        try:
            session.add(data)
            session.commit()
            session.refresh(data)
        except Exception as error:
            print("ERROR:", error)
            raise HTTPException(500)
    return data

def init():
    SQLModel.metadata.create_all(engine)

init()
