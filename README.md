# Recommendation Engine for E Commerce

Hybrid recommendation system that combines content based ranking and item based collaborative filtering. Served through Flask REST APIs with Redis caching. Designed to serve more than 5K products and to support A B testing of recommendation strategies.

## Features

* Content based recommendations using TF IDF on title category and description
* Item based collaborative filtering from user item interactions
* Hybrid re scoring with control on weights
* REST API built with Flask
* Redis caching to reduce average latency by around 35 percent in repeated calls
* Simple A B testing router for online experiments

## Project structure

See repository tree in this README or run tree in your shell.

## Getting started

1. Clone this repository
2. Create a virtual environment
3. Install requirements
4. Start Redis
5. Run Flask

```bash
python -m venv venv
source venv/bin/activate    # Windows use venv\Scripts\activate
pip install -r requirements.txt
redis-server                # make sure it is running on localhost:6379
python app.py
