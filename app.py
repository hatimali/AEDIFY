from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///machinery.db'  # Change to your database URI
db = SQLAlchemy(app)
engine = create_engine('sqlite:///machinery.db')
Session = sessionmaker(bind=engine)


# Define the Machine model
class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(50))
    inventory_id = db.Column(db.String(20))
    machine_type = db.Column(db.String(50))
    machine_price = db.Column(db.Float, default=0.0)
    in_maintenance = db.Column(db.Boolean, default=False)
    maintenance_start = db.Column(db.DateTime, nullable=True)
    maintenance_end = db.Column(db.DateTime, nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.now)


@app.route('/machines', methods=['POST'])
def create_machine():
    data = request.json
    try:
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


@app.route('/machines/<int:machine_id>', methods=['PUT'])
def update_machine(machine_id):
    data = request.json
    try:
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


@app.route('/machines', methods=['GET'])
def list_machines():
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


@app.route('/machines/<int:machine_id>/maintenance', methods=['POST'])
def mark_maintenance(machine_id):
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


@app.route('/machines/available', methods=['GET'])
def list_available_machines():
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


@app.route('/machines/<int:machine_id>', methods=['DELETE'])
def delete_machine(machine_id):
    machine = db.session.query(Machine).get(machine_id)

    if machine:
        db.session.delete(machine)
        db.session.commit()
        return jsonify({'message': 'Machine deleted successfully'})
    else:
        return jsonify({'error': 'Machine not found'}, 404)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
