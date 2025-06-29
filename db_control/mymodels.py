from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime


class Base(DeclarativeBase):
    pass


class PrdMaster(Base):
    __tablename__ = 'prd_master'
    PRD_ID: Mapped[int] = mapped_column(primary_key=True)
    CODE: Mapped[str] = mapped_column(unique=True)
    NAME: Mapped[str] = mapped_column()
    PRICE: Mapped[int] = mapped_column()
