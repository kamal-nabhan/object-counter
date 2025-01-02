import os

from counter.adapters.count_repo import (
    CountMongoDBRepo,
    CountInMemoryRepo,
    CountPostgreSQLRepo,
)
from counter.adapters.object_detector import TFSObjectDetector, FakeObjectDetector
from counter.domain.actions import CountDetectedObjects, PredictedObjects


def dev_count_action() -> CountDetectedObjects:
    return CountDetectedObjects(FakeObjectDetector(), CountInMemoryRepo())


def prod_count_action() -> CountDetectedObjects:
    tfs_host = os.environ.get("TFS_HOST", "localhost")
    tfs_port = int(os.environ.get("TFS_PORT", 8501))
    db_type = os.environ.get("DATABASE", "mongodb")

    if db_type == "mongodb":
        mongo_host = os.environ.get("MONGO_HOST", "localhost")
        mongo_port = int(os.environ.get("MONGO_PORT", 27017))
        mongo_db = os.environ.get("MONGO_DB", "prod_counter")
        return CountDetectedObjects(
            TFSObjectDetector(tfs_host, tfs_port, "rfcn"),
            CountMongoDBRepo(host=mongo_host, port=mongo_port, database=mongo_db),
        )
    elif db_type == "postgres":
        postgres_url = os.environ.get("db_url")
        if not postgres_url:
            raise Exception(
                "Please provide the PostgreSQL URL in the 'db_url' environment variable."
            )
        else:
            db = CountPostgreSQLRepo(postgres_url)
        return CountDetectedObjects(TFSObjectDetector(tfs_host, tfs_port, "rfcn"), db)

    else:
        # Handle incorrect db_type values
        supported_databases = ["mongodb", "postgres"]
        raise ValueError(
            f"Unsupported DATABASE type '{db_type}'. Supported types are: {', '.join(supported_databases)}."
        )


def predict_action() -> PredictedObjects:
    tfs_host = os.environ.get("TFS_HOST", "localhost")
    tfs_port = int(os.environ.get("TFS_PORT", 8501))
    return PredictedObjects(TFSObjectDetector(tfs_host, tfs_port, "rfcn"))


def get_count_action() -> CountDetectedObjects:
    env = os.environ.get("ENV", "dev")
    count_action_fn = f"{env}_count_action"
    return globals()[count_action_fn]()


def get_predict_action() -> PredictedObjects:
    predict_fn = f"predict_action"
    return globals()[predict_fn]()