from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta


create_machine_blueprint = Blueprint("create_machine", __name__)


@create_machine_blueprint.route('/machines', methods=['POST'])
def create_machine():
    data = request.json
    try:
        from app import Machine, db
        label = data['label']
        inventory_id = data['inventory_id']
        machine_type = data['machine_type']
        in_maintenance = data.get('in_maintenance', False)

        if in_maintenance:
            maintenance_start = datetime.strptime(data.get('maintenance_start', datetime.now().strftime('%Y-%m-%d')),
                                                  '%Y-%m-%d')
            maintenance_end = datetime.strptime(data.get('maintenance_end', (
                    maintenance_start + timedelta(days=7)).strftime('%Y-%m-%d')), '%Y-%m-%d')
        else:
            maintenance_start = None
            maintenance_end = None

        if maintenance_start and maintenance_end and maintenance_start > maintenance_end:
            return jsonify({'error': 'Invalid maintenance date range'}), 400

        # Check if the label, inventory_id, and machine_type are provided
        if not label or not inventory_id or not machine_type:
            return jsonify({'error': 'Label, inventory_id, and machine_type are required fields'}), 400

        # Check if a machine with the same inventory_id already exists
        existing_machine = Machine.query.filter_by(inventory_id=inventory_id).first()
        if existing_machine:
            return jsonify({'error': 'A machine with the same inventory_id already exists'}), 400

        # Create a new machine
        machine = Machine(
            label=label,
            inventory_id=inventory_id,
            machine_type=machine_type,
            in_maintenance=in_maintenance,
            maintenance_start=maintenance_start,
            maintenance_end=maintenance_end
        )

        # Add additional data to the machine if present in the request
        for key, value in data.items():
            if key not in ('label', 'inventory_id', 'machine_type', 'in_maintenance', 'maintenance_start', 'maintenance_end'):
                setattr(machine, key, value)

        # Add the machine to the database
        db.session.add(machine)
        db.session.commit()

        return jsonify({'message': 'Machine created successfully'})
    except KeyError:
        return jsonify({'error': 'Invalid request format'}), 400
