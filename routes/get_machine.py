from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

list_machine_blueprint = Blueprint("list_machine", __name__)
mark_machine_blueprint = Blueprint("mark_maintenance", __name__)
available_machine_blueprint = Blueprint("list_available_machines", __name__)



@mark_machine_blueprint.route('/machines/<int:machine_id>/maintenance', methods=['GET'])
def mark_maintenance(machine_id):
    from app import Machine, db
    data = request.json
    machine = db.session.query(Machine).get(machine_id)

    if machine:
        machine.in_maintenance = True
        machine.maintenance_start = datetime.now()
        duration = data.get('duration', 7)  # Default duration is 7 days
        end_date = datetime.now() + timedelta(days=duration)
        machine.maintenance_end = end_date
        db.session.commit()
        return jsonify({'message': 'Machine marked for maintenance'})
    else:
        return jsonify({'error': 'Machine not found'}, 404)


@list_machine_blueprint.route('/machines', methods=['GET'])
def list_machines():
    from app import Machine, db
    machines = Machine.query.all()
    machine_list = []

    for machine in machines:
        machine_info = {
            'id': machine.id,
            'label': machine.label,
            'inventory_id': machine.inventory_id,
            'machine_type': machine.machine_type,
            'machine_price': machine.machine_price,
            'in_maintenance': machine.in_maintenance,
            'creation_date': machine.creation_date
        }

        # Only include maintenance dates if in_maintenance is True
        if machine.in_maintenance:
            if machine.maintenance_start and machine.maintenance_end:
                machine_info['maintenance_start'] = machine.maintenance_start.strftime('%Y-%m-%d %H:%M:%S')
                machine_info['maintenance_end'] = machine.maintenance_end.strftime('%Y-%m-%d %H:%M:%S')

        machine_list.append(machine_info)

    return jsonify(machine_list)


@available_machine_blueprint.route('/machines/available', methods=['GET'])
def list_available_machines():
    from app import Machine, db
    input_date_str = request.args.get('date')
    try:
        input_date = datetime.strptime(input_date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    machines = Machine.query.all()
    available_machines = []

    for machine in machines:
        if not machine.in_maintenance and machine.creation_date.date() == input_date.date():
            available_machines.append({
                'id': machine.id,
                'label': machine.label,
                'inventory_id': machine.inventory_id,
                'machine_type': machine.machine_type,
                'machine_price': machine.machine_price,
                'creation_date': machine.creation_date.strftime('%Y-%m-%d %H:%M:%S')
            })

    return jsonify(available_machines)
