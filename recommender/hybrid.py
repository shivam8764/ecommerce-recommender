# recommender/hybrid.py
from typing import List, Optional, Dict
import pandas as pd


class HybridRecommender:
    def __init__(self, products_df: pd.DataFrame, content_model, cf_model):
        self.products_df = products_df
        self.content_model = content_model
        self.cf_model = cf_model

    def _to_dict(self, product_id: str, score: float, title_map: Dict[str, str]):
        return {
            "product_id": product_id,
            "title": title_map.get(product_id, ""),
            "score": float(score)
        }

    def recommend(
        self,
        user_id: Optional[str] = None,
        product_id: Optional[str] = None,
        top_k: int = 10,
        w_content: float = 0.5,
        w_cf: float = 0.5
    ) -> List[dict]:

        title_map = dict(zip(self.products_df["product_id"], self.products_df["title"]))

        if user_id is None and product_id is None:
            return []

        # case 1 only content
        if user_id is None and product_id is not None:
            return self.content_model.recommend_similar(product_id, top_k)

        # case 2 only user based
        if user_id is not None and product_id is None:
            return self.cf_model.recommend_for_user(user_id, top_k)

        # case 3 combine
        content_recs = self.content_model.recommend_similar(product_id, top_k=top_k*2)
        cf_recs = self.cf_model.recommend_for_user(user_id, top_k=top_k*2)

        scores = {}

        for rec in content_recs:
            pid = rec["product_id"]
            scores[pid] = scores.get(pid, 0.0) + w_content * rec["score"]

        for rec in cf_recs:
            pid = rec["product_id"]
            scores[pid] = scores.get(pid, 0.0) + w_cf * rec["score"]

        # sort and trim
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        result = [self._to_dict(pid, sc, title_map) for pid, sc in ranked if pid in title_map]
        return result
