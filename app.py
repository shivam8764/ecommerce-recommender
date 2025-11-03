# app.py
from flask import Flask, request, jsonify
from config import PRODUCTS_CSV, INTERACTIONS_CSV
from recommender.data_loader import load_products, load_interactions
from recommender.content_based import ContentRecommender
from recommender.collaborative import ItemCFRecommender
from recommender.hybrid import HybridRecommender
from recommender.cache import Cache
from recommender.ab_testing import ABTester

products_df = load_products()
interactions_df = load_interactions()

content_model = ContentRecommender(products_df)
cf_model = ItemCFRecommender(interactions_df)
hybrid_model = HybridRecommender(products_df, content_model, cf_model)
cache = Cache()
ab_tester = ABTester()

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/recommend/content/<product_id>", methods=["GET"])
def recommend_content(product_id):
    top_k = int(request.args.get("top_k", 10))
    cache_key = cache.make_key("content", product_id=product_id, top_k=top_k)
    cached = cache.get(cache_key)
    if cached:
        return jsonify({"source": "cache", "results": cached})
    recs = content_model.recommend_similar(product_id, top_k)
    cache.set(cache_key, recs)
    return jsonify({"source": "model", "results": recs})


@app.route("/recommend/user/<user_id>", methods=["GET"])
def recommend_user(user_id):
    top_k = int(request.args.get("top_k", 10))
    cache_key = cache.make_key("user", user_id=user_id, top_k=top_k)
    cached = cache.get(cache_key)
    if cached:
        return jsonify({"source": "cache", "results": cached})
    recs = cf_model.recommend_for_user(user_id, top_k)
    cache.set(cache_key, recs)
    return jsonify({"source": "model", "results": recs})


@app.route("/recommend/hybrid", methods=["GET"])
def recommend_hybrid():
    user_id = request.args.get("user_id")
    product_id = request.args.get("product_id")
    top_k = int(request.args.get("top_k", 10))
    w_content = float(request.args.get("w_content", 0.5))
    w_cf = float(request.args.get("w_cf", 0.5))
    cache_key = cache.make_key(
        "hybrid",
        user_id=user_id or "",
        product_id=product_id or "",
        top_k=top_k,
        wc=w_content,
        wcf=w_cf
    )
    cached = cache.get(cache_key)
    if cached:
        return jsonify({"source": "cache", "results": cached})
    recs = hybrid_model.recommend(user_id, product_id, top_k, w_content, w_cf)
    cache.set(cache_key, recs)
    return jsonify({"source": "model", "results": recs})


@app.route("/recommend/ab", methods=["GET"])
def recommend_ab():
    user_id = request.args.get("user_id")
    product_id = request.args.get("product_id")
    top_k = int(request.args.get("top_k", 10))
    if not user_id:
        return jsonify({"error": "user_id is required for A B"}), 400

    variant = ab_tester.assign(user_id)

    if variant == "content":
        recs = content_model.recommend_similar(product_id, top_k) if product_id else []
    elif variant == "hybrid":
        recs = hybrid_model.recommend(user_id, product_id, top_k)
    else:
        recs = cf_model.recommend_for_user(user_id, top_k)

    return jsonify({
        "variant": variant,
        "results": recs
    })


@app.route("/feedback", methods=["POST"])
def feedback():
    payload = request.get_json()
    # you can log this to DB or file
    # payload can be {user_id, product_id, action:clicked or purchased, ts}
    print("feedback", payload)
    return jsonify({"status": "received"}), 201


if __name__ == "__main__":
    app.run(debug=True)
