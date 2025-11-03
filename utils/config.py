import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    def load_dotenv(*args, **kwargs):  # no-op fallback if python-dotenv is missing
        return False

# Load .env if present (no-op if dotenv not installed)
load_dotenv()

ROOT = Path(__file__).resolve().parents[1]

# Backends: "local" (default) or "hdfs"
DATA_BACKEND = os.getenv("DATA_BACKEND", "local").lower()
HDFS_URL = os.getenv("HDFS_URL", "")  # e.g., hdfs://namenode:9000

# Allow overriding directories
DATA_DIR = Path(os.getenv("DATA_DIR", ROOT / "data"))
ARTIFACTS_DIR = Path(os.getenv("ARTIFACTS_DIR", ROOT / "artifacts"))

PRODUCTS_FILE = os.getenv("PRODUCTS_FILE", "products.csv")
RATINGS_FILE = os.getenv("RATINGS_FILE", "ratings.csv")


def make_spark(app_name: str):
    """Create a SparkSession configured for local dev or cluster.
    If you run on a cluster, rely on spark-submit settings instead.
    """
    from pyspark.sql import SparkSession
    import sys
    # Ensure Python paths are consistent for driver & workers (Windows fix)
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

    builder = (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        # Ensure Spark uses the same Python interpreter for driver & executors (Windows fix)
        .config("spark.pyspark.driver.python", sys.executable)
        .config("spark.pyspark.python", sys.executable)
        .config("spark.executorEnv.PYSPARK_PYTHON", sys.executable)
    )
    # You can add extra configs here (e.g., warehouse dir, memory, etc.)
    return builder.getOrCreate()


def resolve_path(rel: str) -> str:
    """Return a fully qualified path for Spark read/write.
    - If DATA_BACKEND=hdfs, prefix with HDFS_URL.
    - Else, point to local file path.
    """
    rel = rel.lstrip("/")
    if DATA_BACKEND == "hdfs":
        base = HDFS_URL.rstrip("/")
        return f"{base}/{rel}"
    else:
        return str((ROOT / rel).resolve())


def input_path(filename: str) -> str:
    if DATA_BACKEND == "hdfs":
        return resolve_path(f"data/{filename}")
    else:
        return str((DATA_DIR / filename).resolve())


def output_path(rel_path: str) -> str:
    if DATA_BACKEND == "hdfs":
        return resolve_path(f"artifacts/{rel_path}")
    else:
        out = (ARTIFACTS_DIR / rel_path).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        return str(out)
