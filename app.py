from quart import Quart, jsonify, request, abort
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from database import get_db, engine, Base
from models import WorkOrder, WorkOrderActionLog
from datetime import datetime
import json

app = Quart(__name__)

@app.before_serving
async def create_db():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.route("/workorders/", methods=["POST"])
async def create_work_order():
    data = await request.json
    db = None
    try:
        db = await anext(get_db())  # Get the database session using anext
        new_work_order = WorkOrder(
            state="pending",
            viewers=json.dumps(data.get("viewers", [])),  # Convert list to JSON string
            changers=json.dumps(data.get("changers", [])),  # Convert list to JSON string
            details=json.dumps(data.get("details", {})),  # Convert dict to JSON string
            last_updated=datetime.utcnow().isoformat()  # Store datetime as string
        )
        db.add(new_work_order)
        await db.commit()
        return jsonify({"id": new_work_order.id}), 200
    except Exception as e:
        if db:
            await db.rollback()  # Rollback on error
        return jsonify({"error": str(e)}), 500
    finally:
        if db:
            await db.close()  # Close the session

@app.route("/workorders/<id>/state", methods=["POST"])
async def shift_work_order_state(id):
    data = await request.json
    db = None
    try:
        db = await anext(get_db())  # Get the database session using anext
        result = await db.execute(select(WorkOrder).filter_by(id=id))
        work_order = result.scalars().first()

        if not work_order:
            return jsonify({"error": "Work order not found"}), 404

        previous_last_updated = work_order.last_updated
        previous_state = work_order.state
        work_order.state = "approved"
        work_order.last_updated = datetime.utcnow().isoformat()

        previous_last_updated_dt = datetime.fromisoformat(previous_last_updated)
        time_taken = (datetime.fromisoformat(work_order.last_updated) - previous_last_updated_dt).total_seconds()

        action_log = WorkOrderActionLog(
            work_order_id=work_order.id,
            previous_state=previous_state,
            next_state=work_order.state,
            action=data["action"],
            performed_by=data["performed_by"],
            time_taken=str(time_taken),
            timestamp=datetime.utcnow().isoformat()
        )
        db.add(action_log)
        await db.commit()

        return jsonify({"status": "success", "time_taken": time_taken}), 200
    except Exception as e:
        if db:
            await db.rollback()  # Rollback on error
        return jsonify({"error": str(e)}), 500
    finally:
        if db:
            await db.close()  # Close the session


@app.route("/workorders/visible/<user_id>", methods=["GET"])
async def get_visible_work_orders(user_id):
    db = None
    try:
        db = await anext(get_db())  # Retrieve the DB session
        result = await db.execute(select(WorkOrder).filter(WorkOrder.viewers.contains(user_id)))
        work_orders = result.scalars().all()

        return jsonify([{
            "id": wo.id,
            "state": wo.state,
            "viewers": json.loads(wo.viewers),
            "changers": json.loads(wo.changers),
            "details": json.loads(wo.details),
            "last_updated": wo.last_updated
        } for wo in work_orders]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if db:
            await db.close()  # Close the session properly

@app.route("/workorders/changeable/<user_id>", methods=["GET"])
async def get_changeable_work_orders(user_id):
    db = None
    try:
        db = await anext(get_db())  # Retrieve the DB session
        result = await db.execute(select(WorkOrder).filter(WorkOrder.changers.contains(user_id)))
        work_orders = result.scalars().all()

        return jsonify([{
            "id": wo.id,
            "state": wo.state,
            "viewers": json.loads(wo.viewers),
            "changers": json.loads(wo.changers),
            "details": json.loads(wo.details),
            "last_updated": wo.last_updated
        } for wo in work_orders]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if db:
            await db.close()  # Close the session properly

