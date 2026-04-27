from sqlalchemy import Column, String, ForeignKey, DateTime, Numeric, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database.session import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    transaction_type = Column(
        Enum("income", "expense", name="transaction_type"),
        nullable=False,
    )
    description = Column(String, nullable=True)
    category = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account", back_populates="transactions")
