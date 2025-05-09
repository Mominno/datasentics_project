from flask import Flask, request, render_template, abort
import json
import logging
import os
import requests

# basic config and app setup
app = Flask(__name__)
api_gateway_get_book = 'http://gateway:5000/recommend'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', template_folder='/templates')
    else:
        book_name = request.form['book_name']
        # here make call to api gateway
        response = requests.post(api_gateway_get_book, data={'book_name': book_name})
        if response.status_code == 200:
            # books = list()
            cached_data = response.json()['data']
            books = list(json.loads(cached_data).values())
            return render_template('returned_book_items.html', template_folder='/templates', books=books)
        else:
            logging.warning(f"Call to gateway failed: {response.status_code}, {response.text}")
            return render_template('index.html', template_folder='/templates')
            # return response

# @app.route('/recommend', methods=['POST'])
# def recommend():
#     book_name = request.form['book_name']
#     try:
#         book = find_book_in_dataset(book_name, books_df)
#         logging.warning(f"Recommending for {book['ISBN']}")
#         books = get_book_recommendation_data(book)
#         return render_template('returned_book_items.html', template_folder='/templates', books=books)

#     except IndexError as e:
#         logging.warning(f"Recommending failed for string {book_name}")
#         abort(404, "Book not found")

if __name__ == "__main__":
    app.run()