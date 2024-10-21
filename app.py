from quart import Quart, jsonify, request, abort
from sqlalchemy.future import select
import uuid
from database import get_db, engine, Base
from models import WorkOrder, WorkOrderActionLog, StateTransition
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
    try:
        async with get_db() as db:
            new_work_order = WorkOrder(
                state="pending",
                id = str(uuid.uuid4()),
                viewers=json.dumps(data.get("viewers", [])),
                changers=json.dumps(data.get("changers", [])),
                details=json.dumps(data.get("details", {})),
                last_updated=datetime.utcnow().isoformat(),
                step_count=0
            )
            db.add(new_work_order)
            print(new_work_order)
            return jsonify({"id": new_work_order.id}), 200
    except Exception as e:
        abort(500, description=str(e))

@app.route("/workorders/<id>/state", methods=["POST"])
async def shift_work_order_state(id):
    data = await request.json
    try:
        async with get_db() as db:
            result = await db.execute(select(WorkOrder).filter_by(id=id))
            work_order = result.scalars().first()

            if not work_order:
                abort(404, description="Work order not found")

            requested_action = data.get("action")
            current_state = work_order.state

            transition_result = await db.execute(select(StateTransition).filter_by(current_state=current_state, action=requested_action))
            transition = transition_result.scalars().first()

            if not transition:
                abort(400, description="Invalid state transition")

            previous_last_updated = work_order.last_updated
            work_order.state = transition.next_state
            work_order.last_updated = datetime.utcnow().isoformat()
            work_order.step_count += 1

            previous_last_updated_dt = datetime.fromisoformat(previous_last_updated)
            time_taken = (datetime.fromisoformat(work_order.last_updated) - previous_last_updated_dt).total_seconds()

            action_log = WorkOrderActionLog(
                work_order_id=work_order.id,
                previous_state=current_state,
                next_state=transition.next_state,
                action=requested_action,
                performed_by=data["performed_by"],
                time_taken=float(time_taken),
                timestamp=datetime.utcnow().isoformat(),
                step_count=work_order.step_count
            )
            db.add(action_log)
            return jsonify({"status": "success", "time_taken": time_taken}), 200
    except Exception as e:
        abort(500, description=str(e))

@app.route("/workorders/visible/<user_id>", methods=["GET"])
async def get_visible_work_orders(user_id):
    try:
        async with get_db() as db:
            result = await db.execute(select(WorkOrder).filter(WorkOrder.viewers.contains(user_id)))
            work_orders = result.scalars().all()
            return jsonify([wo.as_dict() for wo in work_orders]), 200
    except Exception as e:
        abort(500, description=str(e))

@app.route("/workorders/changeable/<user_id>", methods=["GET"])
async def get_changeable_work_orders(user_id):
    try:
        async with get_db() as db:
            result = await db.execute(select(WorkOrder).filter(WorkOrder.changers.contains(user_id)))
            work_orders = result.scalars().all()
            return jsonify([wo.as_dict() for wo in work_orders]), 200
    except Exception as e:
        abort(500, description=str(e))

if __name__ == "__main__":
    app.run()
