from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime


class Base(DeclarativeBase):
    pass


class PrdMaster(Base):
    __tablename__ = 'prd_master'
    prd_id: Mapped[int] = mapped_column('prd_id', primary_key=True)
    code: Mapped[str] = mapped_column('code', unique=True)
    name: Mapped[str] = mapped_column('name')
    price: Mapped[int] = mapped_column('price')
    
    # 大文字でアクセスできるようにプロパティを追加
    @property
    def PRD_ID(self):
        return self.prd_id
    
    @property
    def CODE(self):
        return self.code
    
    @property
    def NAME(self):
        return self.name
    
    @property
    def PRICE(self):
        return self.price
