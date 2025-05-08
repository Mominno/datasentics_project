from flask import Flask, request, render_template, jsonify, abort
import json
import logging
import os
import pandas as pd
import redis
import requests
import time

# basic config and app setup
app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)
logging.basicConfig(format='%(asctime)s %(message)s')

# preload data
prefix = os.getenv("DATA_DIR_URL")
books_csv_path = 'Books.csv'
books_df = pd.read_csv("/".join([prefix, books_csv_path]))

model_api_url = 'http://model:5000/recommend_for_ISBN'


def save_book_to_redis(book, value, ttl_seconds=300):
    """Save book to redis. Default time to live is 5 min."""

    cache_key = book['ISBN']
    logging.warning("Saving to redis")
    cache.setex(cache_key, ttl_seconds, json.dumps(value))


def get_book_recommendation_data(book):
    """Implements redis cache for books based on ISBN."""

    cached_data = cache.get(book['ISBN'])
    if cached_data:
        logging.warning("Cache hit!")
        return json.loads(cached_data)

    recommended_books = read_book_from_model_api(book)
    save_book_to_redis(book, recommended_books)
    return recommended_books


def read_book_from_model_api(book):
    """Make request to model API. Returns 502 if model unavailable."""

    book_ISBN = book['ISBN']
    logging.warning(f"Calling model_api for {book_ISBN}")
    response = requests.post(model_api_url, data={'book_ISBN': book_ISBN})
    if response.status_code == 200:
        logging.warning(f"Call successful  {book_ISBN}")
        books = list(response.json().values())
        return books
    else:
        logging.warning(f"Call to model_api failed: {response.status_code}, {response.text}")
        abort(502)


def find_book_in_dataset(book_string, books_df):
    """ Find book entry in dataset from string. 
        Splits string into words and return results containing all words in book_string.
        Case insensitive.
        For simplicity return just first result.
    """

    books_with_lower = books_df['Book-Title'].str.lower()
    book_string = book_string.lower().split(" ")
    bool_indices = books_with_lower.str.contains(book_string[0])
    for word in book_string:
        bool_indices = bool_indices & books_with_lower.str.contains(word)
    logging.warning(f"Found {len(books_df[bool_indices])} possible results for string {book_string}")
    return books_df[bool_indices].iloc[0]


@app.route('/recommend', methods=['POST'])
def recommend():
    book_name = request.form['book_name']
    try:
        book = find_book_in_dataset(book_name, books_df)
        logging.warning(f"Recommending for {book['ISBN']}")
        books = get_book_recommendation_data(book)
        return render_template('returned_book_items.html', template_folder='/templates', books=books)

    except IndexError as e:
        logging.warning(f"Recommending failed for string {book_name}")
        abort(404, "Book not found")
        

    
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', template_folder='/templates')


if __name__ == "__main__":
    app.run()



