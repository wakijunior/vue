import sentry_sdk
from sqlalchemy import select
from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Employee, Authentication
from flask_cors import CORS
from datetime import datetime
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt


sentry_sdk.init(
    dsn="https://a887740c8a91b928a5e45329b0cff1e9@o4511094700900352.ingest.us.sentry.io/4511094748217344",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "gfgtrsersrtfyghuioh8d45s765634diou09gferay"

CORS(app)

jwt = JWTManager(app)

bcrypt = Bcrypt(app)

allowed_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]

try:
    DATABASE_URL = "postgresql+psycopg2://postgres:0911@localhost:5432/vue"
except Exception as e:
    print("Error connecting to the database", str(e))
# Connect to the database using sqlalchemy
engine = create_engine(DATABASE_URL, echo=True)

# Create a session to call query methods
session = sessionmaker(bind=engine)
my_session = session()

# Create the tables in the database
Base.metadata.create_all(engine)

@app.route("/", methods=allowed_methods)
def home():
    # 1/0
    method = request.method.lower()
    if method == "GET":
        msg = { "Flask API Version" : "1.0" }
        return jsonify(msg), 200
    else:
        return jsonify({"error": "Method not allowed"}), 405


@app.route("/employees", methods=allowed_methods)
@jwt_required()
def employees():
    try:
        method = request.method.lower()
        if method == "get":
            employee_list = []
            query = select(Employee)
            my_employees = list(my_session.scalars(query).all())

            for employee in my_employees:
                employee_list.append({"id": employee.id,
                                "name": employee.name,
                                "location": employee.location,
                                "age": employee.age
                                })

            return jsonify({"data": employee_list}), 200
        elif method == "post":
            # convert json to dictionary
            data = request.get_json()
            # check if all fields are received
            if data["name"] == "" or data["location"] == "" or data["age"] == "":
                return jsonify({"msg": "All fields required"}), 401
            else:
                # employee_list.append(data)/store employee in employees tables using SQLAlchemypip
                new_employee = Employee(name=data["name"], 
                                        location=data["location"], 
                                        age=data["age"]
                                        )

                my_session.add(new_employee)
                my_session.commit()
                my_session.close()

                return jsonify({"msg": "Successfully added employee"}), 201
        else:
            return jsonify({"msg": "Method not allowed"}), 405
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/register", methods=allowed_methods)
def register():
    
    if not request.method == "POST":
        return jsonify({"message": "Send a POST request to register a user"}), 405

    else:
        data = request.get_json() or {}

        full_name = data.get("full_name")
        email = data.get("email")
        password = data.get("password")

        if not full_name or not email or not password:
            return jsonify({"error": "Full name, email and password cannot be empty"}), 400

        existing_employee = my_session.query(Authentication).filter_by(email=email).first()
        if existing_employee:
            return jsonify({"error": "Email already registered"}), 409

        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        new_auth = Authentication(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            created_at=datetime.utcnow()
        )

        my_session.add(new_auth)
        my_session.commit()

        token = create_access_token(identity=email)

        return jsonify({
            "message": "User created",
            "token": token
        }), 201

@app.route("/login", methods=allowed_methods)
def login():

    if not request.method == "POST":
        return jsonify({ 'Only post requests allowed'}), 405
        
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    query = select(Authentication).where(Authentication.email == email)
    auth = my_session.scalars(query).first()

    if not auth:
        return jsonify({"error": "Invalid email or password"}), 401

    if not bcrypt.check_password_hash(auth.hashed_password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=data["email"])
    return jsonify({
        "message": "Login successful",
        "user": {
            "id": auth.id,
            "full_name": auth.full_name,
            "email": auth.email,
        },
        "token": f"{token}"
    }), 200


app.run(debug=True)