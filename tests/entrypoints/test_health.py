import pytest
from counter.entrypoints.webapp import create_app
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_health_endpoint_healthy(client):
    with patch("requests.get") as mock_get, patch(
        "counter.entrypoints.webapp.MongoClient"
    ) as mock_mongo_client, patch(
        "counter.entrypoints.webapp.psycopg2.connect"
    ) as mock_pg_connect:

        # Mock TensorFlow Serving health
        mock_get.return_value.status_code = 200

        # Mock MongoDB health
        mock_mongo = MagicMock()
        mock_mongo.admin.command.return_value = {"ok": 1.0}
        mock_mongo_client.return_value = mock_mongo

        # Mock PostgreSQL health
        mock_pg_conn = MagicMock()
        mock_pg_cursor = MagicMock()
        mock_pg_conn.cursor.return_value = mock_pg_cursor
        mock_pg_cursor.execute.return_value = None
        mock_pg_connect.return_value = mock_pg_conn

        # Call the endpoint
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert data["dependencies"]["tfserving"] == "healthy"
        assert data["dependencies"]["mongodb"] == "healthy"
        assert data["dependencies"]["postgresql"] == "healthy"


def test_health_endpoint_unhealthy_tfserving(client):
    with patch("requests.get") as mock_get, patch(
        "counter.entrypoints.webapp.MongoClient"
    ) as mock_mongo_client, patch(
        "counter.entrypoints.webapp.psycopg2.connect"
    ) as mock_pg_connect:

        # Mock TensorFlow Serving health to be unhealthy
        mock_get.return_value.status_code = 500

        # Mock MongoDB and PostgreSQL health to be healthy
        mock_mongo = MagicMock()
        mock_mongo.admin.command.return_value = {"ok": 1.0}
        mock_mongo_client.return_value = mock_mongo

        mock_pg_conn = MagicMock()
        mock_pg_cursor = MagicMock()
        mock_pg_conn.cursor.return_value = mock_pg_cursor
        mock_pg_cursor.execute.return_value = None
        mock_pg_connect.return_value = mock_pg_conn

        # Call the endpoint
        response = client.get("/health")
        assert response.status_code == 500
        data = response.get_json()
        assert data["status"] == "unhealthy"
        assert data["dependencies"]["tfserving"].startswith("unhealthy")


def test_health_endpoint_unhealthy_mongodb(client):
    with patch("requests.get") as mock_get, patch(
        "counter.entrypoints.webapp.MongoClient"
    ) as mock_mongo_client, patch(
        "counter.entrypoints.webapp.psycopg2.connect"
    ) as mock_pg_connect:

        # Mock TensorFlow Serving health to be healthy
        mock_get.return_value.status_code = 200

        # Mock MongoDB health to be unhealthy
        mock_mongo_client.side_effect = Exception("MongoDB connection error")

        # Mock PostgreSQL health to be healthy
        mock_pg_conn = MagicMock()
        mock_pg_cursor = MagicMock()
        mock_pg_conn.cursor.return_value = mock_pg_cursor
        mock_pg_cursor.execute.return_value = None
        mock_pg_connect.return_value = mock_pg_conn

        # Call the endpoint
        response = client.get("/health")
        assert response.status_code == 500
        data = response.get_json()
        assert data["status"] == "unhealthy"
        assert data["dependencies"]["mongodb"].startswith("unhealthy")


def test_health_endpoint_unhealthy_postgresql(client):
    with patch("requests.get") as mock_get, patch(
        "counter.entrypoints.webapp.MongoClient"
    ) as mock_mongo_client, patch(
        "counter.entrypoints.webapp.psycopg2.connect"
    ) as mock_pg_connect:

        # Mock TensorFlow Serving and MongoDB health to be healthy
        mock_get.return_value.status_code = 200

        mock_mongo = MagicMock()
        mock_mongo.admin.command.return_value = {"ok": 1.0}
        mock_mongo_client.return_value = mock_mongo

        # Mock PostgreSQL health to be unhealthy
        mock_pg_connect.side_effect = Exception("PostgreSQL connection error")

        # Call the endpoint
        response = client.get("/health")
        assert response.status_code == 500
        data = response.get_json()
        assert data["status"] == "unhealthy"
        assert data["dependencies"]["postgresql"].startswith("unhealthy")


def test_health_endpoint_unhealthy_all(client):
    with patch("requests.get") as mock_get, patch(
        "counter.entrypoints.webapp.MongoClient"
    ) as mock_mongo_client, patch(
        "counter.entrypoints.webapp.psycopg2.connect"
    ) as mock_pg_connect:

        # Mock all dependencies to be unhealthy
        mock_get.return_value.status_code = 500
        mock_mongo_client.side_effect = Exception("MongoDB connection error")
        mock_pg_connect.side_effect = Exception("PostgreSQL connection error")

        # Call the endpoint
        response = client.get("/health")
        assert response.status_code == 500
        data = response.get_json()
        assert data["status"] == "unhealthy"
        assert data["dependencies"]["tfserving"].startswith("unhealthy")
        assert data["dependencies"]["mongodb"].startswith("unhealthy")
        assert data["dependencies"]["postgresql"].startswith("unhealthy")
