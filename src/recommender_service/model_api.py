from flask import Flask, request, abort, jsonify
import redis
import json

from model import ( get_implicit_ratings,
                    load_data,
                    recommend_books_for_book_ID,
                    find_book_in_dataset,
                )
import logging

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)

# preload data to memory for fast access
_, books_df, ratings_df, book_ID_column_name = load_data()
implicit_ratings = get_implicit_ratings(ratings_df)


def save_book_to_redis(book, value, ttl_seconds=300):
    """Save book to redis. Default time to live is 5 min."""

    # cache_key = book['ISBN']
    cache_key = int(book[book_ID_column_name])
    logging.warning("Saving to redis")
    cache.setex(cache_key, ttl_seconds, json.dumps(value))

def get_book_recommendation_data(book):
    """Implements redis cache for books based on ISBN."""

    # cached_data = cache.get(book['ISBN'])
    cached_data = cache.get(int(book[book_ID_column_name]))
    
    if cached_data:
        logging.warning("Cache hit!")
        return json.loads(cached_data)

    # recommended_books = recommend_for_book_ISBN(book['ISBN'])
    recommended_books = recommend_books_for_book_ID(book[book_ID_column_name], implicit_ratings, books_df)
    save_book_to_redis(book, recommended_books)
    return recommended_books

@app.route('/recommend_for_user_input', methods=['POST'])
def recommend():
    book_name = request.form['book_name']
    try:
        book = find_book_in_dataset(book_name, books_df)
        logging.warning(f"Recommending for {book['ISBN']}")
        books = get_book_recommendation_data(book)
        return jsonify({"data": books, "status_code": 200, "model_book": book.to_json(orient='index')})
    except IndexError as e:
        logging.warning(f"Recommending failed for string {book_name}")
        return jsonify({"message": "Book not found", "data": "{}", "status_code": 404})


def main():
    app.run()

if __name__ == "__main__":
    main()