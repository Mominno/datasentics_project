from flask import Flask, request, abort, jsonify
import redis
import json

from model import ( get_implicit_ratings,
                    load_data,
                    recommend_books_for_book_ISBN,
                    find_book_in_dataset,
                )
import logging

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)

# preload data to memory for fast access
_, books_df, ratings_df = load_data()
implicit_ratings, ratings_by_books = get_implicit_ratings(ratings_df)

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

    recommended_books = recommend_for_book_ISBN(book['ISBN'])
    save_book_to_redis(book, recommended_books)
    return recommended_books

@app.route('/recommend_for_user_input', methods=['POST'])
def recommend():
    book_name = request.form['book_name']
    try:
        book = find_book_in_dataset(book_name, books_df)
        logging.warning(f"Recommending for {book['ISBN']}")
        books = get_book_recommendation_data(book)
        return jsonify({"data": books, "status_code": 200})
    except IndexError as e:
        logging.warning(f"Recommending failed for string {book_name}")
        return jsonify({"message": "Book not found", "data": "{}", "status_code": 404})

# @app.route('/recommend_for_ISBN', methods=['POST'])
def recommend_for_book_ISBN(book_ISBN, top_n=5):
    """Recommends books for given ISBN. Expects body with keys book_ISBN and top_n.
    Return error when book_ISBN is missing.
    top_n results default to 5.
    Books are returned as json schema {book_index: {'ISBN': book_value,...}...}
    """
    logging.warning(f"Recommending for book {book_ISBN}")

    recommended_books_with_scores = recommend_books_for_book_ISBN(
                                book_ISBN,
                                ratings_by_books,
                                implicit_ratings, 
                                top_n=top_n,
                            )
    if recommended_books_with_scores is not None:
        recommended_books_ISBN = [book[0] for book in recommended_books_with_scores]
        data = books_df[books_df['ISBN'].isin(recommended_books_ISBN)].to_json(orient='index')
        return data
    else:
        return "{}"

def main():
    app.run()

if __name__ == "__main__":
    main()