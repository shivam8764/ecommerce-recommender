import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
PRODUCTS_CSV = os.path.join(DATA_DIR, "products.csv")
INTERACTIONS_CSV = os.path.join(DATA_DIR, "interactions.csv")

# Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# A B test settings
# model_a can be content
# model_b can be hybrid
AB_TEST_DEFAULT = {
    "variant_a": "content",
    "variant_b": "hybrid",
    "split": 0.5
}
