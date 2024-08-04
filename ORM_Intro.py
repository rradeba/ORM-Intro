from flask import Flask, jsonify, request 
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow 
from password import my_password
from marshmallow import fields 
from marshmallow import ValidationError 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{my_password}@localhost/fitness_center_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class MemberSchema(ma.Schema): 
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ("name", "email", "phone")

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

class SessionSchema(ma.Schema): 
    time = fields.String(required=True)
    date = fields.String(required=True)
    activity = fields.String(required=True)

    class Meta:
        fields = ("time", "date", "activity")

session_schema = SessionSchema()
sessions_schema = SessionSchema(many=True)

class Member(db.Model):
    __tablename__ = 'members'
    member_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(255), nullable=False)

class WorkoutSession(db.Model):
    __tablename__ = 'workout_sessions'
    session_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(255), nullable=False)
    activity = db.Column(db.String(255), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.member_id'))

# POST method for members
@app.route('/members', methods=['POST'])
def add_member():
    try: 
        member_data = member_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 400 

    new_member = Member(
        name=member_data['name'], 
        email=member_data['email'], 
        phone=member_data['phone']
    )
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"message": "Member added successfully"}), 201

# GET method for members
@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    member = Member.query.get_or_404(id)
    return member_schema.jsonify(member)

# PUT method for members
@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id): 
    member = Member.query.get_or_404(id) 
    try: 
        member_data = member_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 400 
    member.name = member_data['name']
    member.email = member_data['email']
    member.phone = member_data['phone']
    db.session.commit()
    return jsonify({"message": "Member updated successfully"}), 200

# DELETE method for members
@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member deleted successfully"}), 200

# POST method for sessions 
@app.route('/workoutsessions', methods=['POST'])
def schedule_session():
    try: 
        session_data = session_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 400 

    new_session = WorkoutSession(
        time=session_data['time'], 
        date=session_data['date'], 
        activity=session_data['activity'],
        member_id=session_data.get('member_id')  # Make sure member_id is included in the request
    )
    db.session.add(new_session)
    db.session.commit()
    return jsonify({"message": "Session scheduled successfully"}), 201

# GET method for sessions
@app.route('/workoutsessions/<int:id>', methods=['GET'])
def get_session(id):
    session = WorkoutSession.query.get_or_404(id)
    return session_schema.jsonify(session)

# PUT method for sessions
@app.route('/workoutsessions/<int:id>', methods=['PUT'])
def update_session(id):   
    session = WorkoutSession.query.get_or_404(id)
    try: 
        session_data = session_schema.load(request.json)
    except ValidationError as e: 
        return jsonify(e.messages), 400 
    session.date = session_data['date']
    session.time = session_data['time']
    session.activity = session_data['activity']
    db.session.commit()
    return jsonify({"message": "Session updated successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)