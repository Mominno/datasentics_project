# recommender wrapper api

from flask import Flask, request, render_template, jsonify
import logging
import os
import time
import redis
import requests

import pandas as pd

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)
logging.basicConfig(format='%(asctime)s %(message)s')


prefix = os.getenv("DATA_DIR_URL")
books_csv_path = 'Books.csv'
books_df = pd.read_csv("/".join([prefix, books_csv_path]))


def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

def find_book_in_dataset(book_string, books_df):
    books_with_lower = books_df['Book-Title'].str.lower()
    book_string = book_string.lower().split(" ")
    bool_indices = books_with_lower.str.contains(book_string[0])
    for word in book_string:
        bool_indices = bool_indices & books_with_lower.str.contains(word)
    return books_df[bool_indices].iloc[0]


@app.route('/recommend', methods=['POST'])
def recommend():
    book_name = request.form['book_name']
    book = find_book_in_dataset(book_name, books_df)
    try:
        book_ISBN = book['ISBN']
        # look into redis
        # fetch
        # or call api and store
        r = requests.post('http://model:5000/recommend_for_ISBN', data={'book_ISBN': book_ISBN})
        if r.status_code == 200:
            books = list(r.json().values())
        else:
            logging.warning(f"Call to model_api failed: {r.json()}")
        return render_template('returned_book_items.html', template_folder='/templates', books=books)

    except IndexError as e:
        # TODO return page with error
        return jsonify({"Message": "Book nof found"})

    

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', template_folder='/templates')

@app.route('/hello')
def hello():
    count = get_hit_count()
    return f'Hello World! I have been seen {count} times.\n'

if __name__ == "__main__":
    app.run()



