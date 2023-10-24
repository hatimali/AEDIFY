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


from routes.create_machine import create_machine_blueprint
from routes.delete_machine import delete_machine_blueprint
from routes.get_machine import list_machine_blueprint, available_machine_blueprint, mark_machine_blueprint
from routes.update_machine import update_machine_blueprint

app.register_blueprint(create_machine_blueprint)
app.register_blueprint(update_machine_blueprint)
app.register_blueprint(list_machine_blueprint)
app.register_blueprint(mark_machine_blueprint)
app.register_blueprint(available_machine_blueprint)
app.register_blueprint(delete_machine_blueprint)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True)
