from sqlalchemy import select
from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, User, Authentication
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime



app = Flask(__name__)
CORS(app)

allowed_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]

DATABASE_URL = "postgresql+psycopg2://postgres:0911@localhost:5432/vue"

# Connect to the database using sqlalchemy
engine = create_engine(DATABASE_URL, echo=True)

# Create a session to call query methods
session = sessionmaker(bind=engine)
my_session = session()

# Create the tables in the database
Base.metadata.create_all(engine)

@app.route("/", methods=allowed_methods)
def home():
    if request.method == "GET":
        msg = { "Flask API Version" : "1.0" }
        return jsonify(msg), 200
    else:
        return jsonify({"error": "Method not allowed"}), 405


@app.route("/users", methods=allowed_methods)
def user():
    if request.method.upper() == "GET":
        # return a list of all users in the database
        query = select(User)
        users = my_session.scalars(query).all()
        data = []

        for user in users:
            data.append({
                "id": user.id,
                "full_name": user.full_name,
                "age": user.age,
                "location": user.location
            })
        return jsonify({ "data": data })
    elif request.method.upper() == "POST":
        data = request.get_json()
        if data["full_name"] == "" or data["location"] == "" or data["age"] == "":
            return jsonify({ "error": "Full name and Location cannot be empty" }), 400
        else:
            new_user = User(name=data["name"], location=data["location"], age=data["age"])
            my_session.add(new_user)
            my_session.commit()
            return jsonify({ "message": f"User created successfully{data['full_name']}" }), 201

@app.route("/register", methods=allowed_methods)
def register():
    data = request.get_json()

    #ensure all fields are set and check if email already exists in the user authentication table.
    if data["full_name"] == "" or data["email"] == "" or data["password"] == "":
        return jsonify({"error": "Full name, email and password cannot be empty"}), 400
    
    existing_user = my_session.query(Authentication).filter_by(email=data["email"]).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 409

    # 🔑 Create authentication record
    new_auth = Authentication(
        email=data["email"],
        hashed_password=data["password"],
        full_name=data["full_name"],
        created_at=datetime.utcnow()
    )

    # 💾 Save both
    my_session.add(new_auth)
    my_session.commit()
    return jsonify({"message": "User created"}), 201

@app.route("/login", methods=allowed_methods)
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    query = select(Authentication).where(Authentication.email == email, Authentication.hashed_password == password)
    auth = my_session.scalars(query).first()

    if not auth:
        return jsonify({"error": "Invalid email or password"}), 401

    # Assuming you stored hashed password
    # if not check_password_hash(auth.password, password):
        # return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": auth.id,
            "full_name": auth.full_name,
            "email": auth.email
        }
    }), 200


app.run(debug=True)