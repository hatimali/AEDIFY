from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

update_machine_blueprint = Blueprint("update_machine", __name__)


@update_machine_blueprint.route('/machines/<int:machine_id>', methods=['PUT'])
def update_machine(machine_id):
    data = request.json
    try:
        from app import db, Machine
        machine = db.session.query(Machine).get(machine_id)
        if machine:
            if "label" in data:
                machine.label = data["label"]
            if "inventory_id" in data:
                machine.inventory_id = data["inventory_id"]
            if "machine_type" in data:
                machine.machine_type = data["machine_type"]
            if "machine_price" in data:
                machine.machine_price = data["machine_price"]
            if "in_maintenance" in data:
                machine.in_maintenance = data["in_maintenance"]

            if machine.in_maintenance:
                maintenance_start = datetime.strptime(
                    data.get('maintenance_start', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d')
                maintenance_end = datetime.strptime(
                    data.get('maintenance_end', (maintenance_start + timedelta(days=7)).strftime('%Y-%m-%d')),
                    '%Y-%m-%d')

                if maintenance_start and maintenance_end and maintenance_start > maintenance_end:
                    return jsonify({'error': 'Invalid maintenance date range'}), 400

                machine.maintenance_start = maintenance_start
                machine.maintenance_end = maintenance_end
            else:
                machine.maintenance_start = None
                machine.maintenance_end = None

            db.session.commit()
            return jsonify({'message': 'Machine updated successfully'})
        else:
            return jsonify({'error': 'Machine not found'}, 404)
    except KeyError:
        return jsonify({'error': 'Invalid request format'}), 400
