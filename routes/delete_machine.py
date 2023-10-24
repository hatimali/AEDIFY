from flask import Blueprint, request, jsonify


delete_machine_blueprint = Blueprint("delete_machine", __name__)

@delete_machine_blueprint.route('/machines/<int:machine_id>', methods=['DELETE'])
def delete_machine(machine_id):
    from app import db, Machine
    machine = db.session.query(Machine).get(machine_id)

    if machine:
        db.session.delete(machine)
        db.session.commit()
        return jsonify({'message': 'Machine deleted successfully'})
    else:
        return jsonify({'error': 'Machine not found'}, 404)