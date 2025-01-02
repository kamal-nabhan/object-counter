from flask import Flask, request, jsonify
from io import BytesIO
from werkzeug.exceptions import Unauthorized
import jwt
import datetime
from functools import wraps
from counter import config

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
    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get("Authorization")
            print("token :", token)
            if not token:
                raise Unauthorized("Token is missing")
            try:
                jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            except jwt.ExpiredSignatureError:
                raise Unauthorized("Token has expired")
            except jwt.InvalidTokenError:
                raise Unauthorized("Invalid token")
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

        # Replace with actual authentication logic
        if user:
            token = jwt.encode(
                {
                    "username": username,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
                },
                JWT_SECRET,
                algorithm=JWT_ALGORITHM,
            )
            # return str({'token': token})
            return jsonify({"token": str(token)})
        else:
            return "Invalid credentials\n", 401

    @app.route("/object-count", methods=["POST"])
    @token_required
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

    return app


if __name__ == "__main__":
    app = create_app()
    app.run("0.0.0.0", debug=True)
