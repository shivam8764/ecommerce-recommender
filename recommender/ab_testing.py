# recommender/ab_testing.py
import hashlib
from config import AB_TEST_DEFAULT


class ABTester:
    def __init__(self, config=None):
        self.config = config or AB_TEST_DEFAULT

    def assign(self, user_id: str):
        h = hashlib.md5(user_id.encode("utf-8")).hexdigest()
        num = int(h[:8], 16) / 0xFFFFFFFF
        if num < self.config["split"]:
            return self.config["variant_a"]
        return self.config["variant_b"]
