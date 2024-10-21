import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, Integer, Float

# Database URL (using SQLite, compatible with LibSQL)
DATABASE_URL = "sqlite+aiosqlite:///./my_database.db"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create session factory for async sessions
AsyncSessionLocal = sessionmaker(bind=engine, class_=sessionmaker, expire_on_commit=False)

# Base model
Base = declarative_base()

# Define the WorkOrder model
class WorkOrder(Base):
    __tablename__ = "work_orders"
    id = Column(String, primary_key=True)
    state = Column(String, index=True)
    last_updated = Column(Text)
    viewers = Column(Text)
    changers = Column(Text)
    details = Column(Text)
    step_count = Column(Integer)

# Define the WorkOrderActionLog model
class WorkOrderActionLog(Base):
    __tablename__ = "work_order_action_log"
    id = Column(String, primary_key=True)
    work_order_id = Column(String)
    previous_state = Column(String)
    next_state = Column(String)
    action = Column(String)
    performed_by = Column(String)
    time_taken = Column(String)
    timestamp = Column(Float)
    step_count = Column(Integer)

# Define the StateTransition model
class StateTransition(Base):
    __tablename__ = "state_transitions"
    current_state = Column(String, primary_key=True)
    action = Column(String, primary_key=True)
    next_state = Column(String)

# Function to create the tables
async def create_tables():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

# Function to populate the state_transitions table
async def populate_state_transitions():
    async with AsyncSessionLocal() as session:
        # Insert initial state transitions
        initial_transitions = [
            {"current_state": "pending", "action": "approve", "next_state": "approved"},
            {"current_state": "pending", "action": "reject", "next_state": "rejected"},
            {"current_state": "approved", "action": "complete", "next_state": "completed"},
            {"current_state": "approved", "action": "reopen", "next_state": "pending"},
            {"current_state": "rejected", "action": "reopen", "next_state": "pending"},
            {"current_state": "completed", "action": "reopen", "next_state": "approved"}
        ]

        # Create StateTransition objects
        transitions = [StateTransition(**transition) for transition in initial_transitions]

        # Add to the session
        session.add_all(transitions)
        
        # Commit the transaction
        await session.commit()
        print("State transitions populated.")

# Main function to create and deploy the database
async def main():
    # Step 1: Create the tables
    print("Creating tables...")
    await create_tables()

    # Step 2: Populate the state transitions table
    print("Populating state transitions...")
    await populate_state_transitions()

    print("Database setup complete.")

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
