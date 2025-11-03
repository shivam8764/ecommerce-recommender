# recommender/content_based.py
from typing import List
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


class ContentRecommender:
    def __init__(self, products_df: pd.DataFrame):
        self.products_df = products_df.reset_index(drop=True)
        self.products_df["text"] = (
            self.products_df["title"].fillna("") + " " +
            self.products_df["category"].fillna("") + " " +
            self.products_df["description"].fillna("")
        )
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=20000)
        self.tfidf_matrix = self.vectorizer.fit_transform(self.products_df["text"])
        # map product_id to index
        self.id_to_index = {
            pid: idx for idx, pid in enumerate(self.products_df["product_id"].tolist())
        }

    def recommend_similar(self, product_id: str, top_k: int = 10) -> List[dict]:
        if product_id not in self.id_to_index:
            return []
        idx = self.id_to_index[product_id]
        cosine_similarities = linear_kernel(
            self.tfidf_matrix[idx:idx+1],
            self.tfidf_matrix
        ).flatten()
        # get top_k+1 because first one is itself
        related_indices = cosine_similarities.argsort()[::-1][1:top_k+1]
        results = []
        for i in related_indices:
            row = self.products_df.iloc[i]
            results.append({
                "product_id": row["product_id"],
                "title": row["title"],
                "score": float(cosine_similarities[i])
            })
        return results
