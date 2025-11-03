# recommender/collaborative.py
from typing import List
import pandas as pd
import numpy as np


class ItemCFRecommender:
    def __init__(self, interactions_df: pd.DataFrame):
        self.interactions_df = interactions_df
        # pivot to user x item
        # for scale 5K products x few K users this is fine
        user_item = (
            interactions_df
            .groupby(["user_id", "product_id"])
            .size()
            .unstack(fill_value=0)
        )
        self.user_item = user_item
        # compute item item similarity using cosine
        item_matrix = user_item.T
        item_norms = np.linalg.norm(item_matrix, axis=1, keepdims=True)
        # avoid div by zero
        item_norms[item_norms == 0] = 1.0
        sim_matrix = (item_matrix @ item_matrix.T) / (item_norms @ item_norms.T)
        self.items = item_matrix.index.tolist()
        self.sim_matrix = sim_matrix

        # map product to index
        self.item_to_index = {item_id: idx for idx, item_id in enumerate(self.items)}

    def recommend_for_user(self, user_id: str, top_k: int = 10) -> List[dict]:
        if user_id not in self.user_item.index:
            return []
        user_vector = self.user_item.loc[user_id].values
        # find items user has interacted with
        interacted_indices = np.where(user_vector > 0)[0]

        scores = np.zeros(len(self.items))
        for idx in interacted_indices:
            scores += self.sim_matrix[idx]

        # zero out already interacted items
        scores[interacted_indices] = 0

        top_indices = scores.argsort()[::-1][:top_k]
        recs = []
        for idx in top_indices:
            recs.append({
                "product_id": self.items[idx],
                "score": float(scores[idx])
            })
        return recs
