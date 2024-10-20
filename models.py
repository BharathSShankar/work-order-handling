from sqlalchemy import Column, String, Text, Float
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class WorkOrder(Base):
    __tablename__ = "work_orders"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    state = Column(String, index=True)
    last_updated = Column(Text)  # Store ISO 8601 string for datetime
    viewers = Column(Text)  # Store JSON string
    changers = Column(Text)  # Store JSON string
    details = Column(Text)  # Store JSON string

class WorkOrderActionLog(Base):
    __tablename__ = "work_order_action_log"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    work_order_id = Column(String)
    previous_state = Column(String)
    next_state = Column(String)
    action = Column(String)
    performed_by = Column(String)
    time_taken = Column(String)  # Store time taken as string
    timestamp = Column(Text)  # Store ISO 8601 string for datetime
