from flask import Flask, request, jsonify
from io import BytesIO
import jwt
import datetime
from functools import wraps
import requests
from pymongo import MongoClient
from counter import config
import psycopg2

JWT_SECRET = "381836fe163039ab7bcd0a84bf54dded9fbd4269"
JWT_ALGORITHM = "HS256"

# Sample local database of users
USER_DB = [
    {"username": "admin", "password": "password"},
    {"username": "user1", "password": "user1password"},
    {"username": "user2", "password": "user2password"},
]


def create_app():
    app = Flask(__name__)

    count_action = config.get_count_action()
    predict_action = config.get_predict_action()

    # Utility function to validate JWT tokens
    def protected_route(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return "Token is missing", 401
            try:
                jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            except jwt.ExpiredSignatureError:
                return "Token has expired", 401
            except jwt.InvalidTokenError:
                return "Invalid token", 401
            return f(*args, **kwargs)

        return decorated

    @app.route("/auth", methods=["POST"])
    def authenticate():
        data = request.json
        username = data.get("username")
        password = data.get("password")

        # Check if the username and password match any entry in the local database
        user = next(
            (
                u
                for u in USER_DB
                if u["username"] == username and u["password"] == password
            ),
            None,
        )

        if user:
            token = jwt.encode(
                {
                    "username": username,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
                },
                JWT_SECRET,
                algorithm=JWT_ALGORITHM,
            )
            return jsonify({"token": str(token)})
        else:
            return "Invalid credentials", 401

    @app.route("/object-count", methods=["POST"])
    @protected_route
    def object_detection():

        threshold = float(request.form.get("threshold", 0.5))
        uploaded_file = request.files["file"]
        model_name = request.form.get("model_name", "rfcn")
        image = BytesIO()
        uploaded_file.save(image)
        count_response = count_action.execute(image, threshold)
        return jsonify(count_response)

    @app.route("/predict", methods=["POST"])
    def prediction_list():

        threshold = float(request.form.get("threshold", 0.5))
        uploaded_file = request.files["file"]
        model_name = request.form.get("model_name", "rfcn")
        image = BytesIO()
        uploaded_file.save(image)
        predict_response = predict_action.execute(image, threshold)
        return jsonify(predict_response)

    @app.route("/health", methods=["GET"])
    def health_check():
        """
        Health check endpoint to verify the application's health, including dependencies.
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "dependencies": {},
        }

        try:
            # Check TensorFlow Serving health
            tfserving_url = "http://tfserving:8501/v1/models/rfcn"
            tfserving_response = requests.get(tfserving_url)
            if tfserving_response.status_code == 200:
                health_status["dependencies"]["tfserving"] = "healthy"
            else:
                health_status["dependencies"][
                    "tfserving"
                ] = f"unhealthy (status code: {tfserving_response.status_code})"
                health_status["status"] = "unhealthy"

        except Exception as e:
            health_status["dependencies"]["tfserving"] = f"unhealthy (error: {str(e)})"
            health_status["status"] = "unhealthy"

        try:
            # Check MongoDB health
            mongo_client = MongoClient("mongodb://mongo:27017")
            mongo_client.admin.command("ping")
            health_status["dependencies"]["mongodb"] = "healthy"
        except Exception as e:
            health_status["dependencies"]["mongodb"] = f"unhealthy (error: {str(e)})"
            health_status["status"] = "unhealthy"

        try:
            # Check PostgreSQL health
            postgres_conn = psycopg2.connect(
                dbname="OBJ_COUNT",
                user="postgres",
                password="postgres",
                host="postgres",
                port="5432",
            )
            cursor = postgres_conn.cursor()
            cursor.execute("SELECT 1;")
            postgres_conn.close()
            health_status["dependencies"]["postgresql"] = "healthy"
        except Exception as e:
            health_status["dependencies"]["postgresql"] = f"unhealthy (error: {str(e)})"
            health_status["status"] = "unhealthy"

        # Return the consolidated health status
        return jsonify(health_status), (
            200 if health_status["status"] == "healthy" else 500
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.run("0.0.0.0", debug=True)
