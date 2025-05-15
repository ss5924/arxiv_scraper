from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, DateTime, Integer, Enum
import enum

Base = declarative_base()


class TaskStatus(str, enum.Enum):
    pending = "pending"
    done = "done"
    fail = "fail"


class TaskQueue(AsyncAttrs, Base):
    __tablename__ = "task_queue"
    __table_args__ = {"schema": "arxiv_raw"}

    id = Column(Integer, primary_key=True)
    start = Column(DateTime)
    status = Column(
        Enum(TaskStatus, name="status", native_enum=False),
        default=TaskStatus.pending
    )
    retries = Column(Integer, default=0)


class Paper(AsyncAttrs, Base):
    __tablename__ = "papers"
    __table_args__ = {"schema": "arxiv_raw"}

    arxiv_id = Column(String, primary_key=True)
    authors = Column(String)
    category = Column(String)
    abstract = Column(String)
    published_date = Column(DateTime)
    pdf_url = Column(String)
