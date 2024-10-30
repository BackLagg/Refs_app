from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy.orm import relationship

from src.database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey


class User(SQLAlchemyBaseUserTable[int] ,Base):
    __tablename__ = 'user'
    id = Column("id", Integer, primary_key=True)
    hashed_password: str = Column(String(length=1024), nullable=False)
    reg_at = Column("reg_at", TIMESTAMP, default=datetime.utcnow())

class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    referred_user_id = Column(Integer, ForeignKey("user.id"))

    user = relationship("User", foreign_keys=[user_id])
    referred_user = relationship("User", foreign_keys=[referred_user_id])

