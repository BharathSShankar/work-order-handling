from sqlalchemy import Column, String, Text, Float, Integer
from sqlalchemy.dialects.sqlite import JSON
import json
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class WorkOrder(Base):
    __tablename__ = 'work_orders'

    id = Column(Integer, primary_key=True)
    state = Column(String)
    viewers = Column(String)  # Assuming JSON stored as String
    changers = Column(String)  # Assuming JSON stored as String
    details = Column(String)  # Assuming JSON stored as String
    last_updated = Column(String)
    step_count = Column(Integer)

    def as_dict(self):
        return {
            "id": self.id,
            "state": self.state,
            "viewers": json.loads(self.viewers),
            "changers": json.loads(self.changers),
            "details": json.loads(self.details),
            "last_updated": self.last_updated,
            "step_count": self.step_count
        }

class WorkOrderActionLog(Base):
    __tablename__ = "work_order_action_log"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    work_order_id = Column(String)
    previous_state = Column(String)
    next_state = Column(String)
    action = Column(String)
    performed_by = Column(String)
    time_taken = Column(Float)  # Store time taken as string
    timestamp = Column(Text)  # Store ISO 8601 string for datetime
    step_count = Column(Integer)  # Store step count as string

class StateTransition(Base):
    __tablename__ = "state_transitions"
    current_state = Column(String, primary_key=True)
    action = Column(String, primary_key=True)
    next_state = Column(String)