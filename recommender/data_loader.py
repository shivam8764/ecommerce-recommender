# recommender/data_loader.py
import pandas as pd
from config import PRODUCTS_CSV, INTERACTIONS_CSV


def load_products():
    df = pd.read_csv(PRODUCTS_CSV)
    # expected columns
    # product_id,title,category,description,price,img_url
    return df


def load_interactions():
    df = pd.read_csv(INTERACTIONS_CSV)
    # expected columns
    # user_id,product_id,interaction_type,ts
    # you can later weight interaction_type for ranking
    return df
