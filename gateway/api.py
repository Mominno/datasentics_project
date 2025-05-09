from flask import Flask, request, jsonify
import json
import logging
import requests

# basic config and app setup
app = Flask(__name__)

logging.basicConfig(format='%(asctime)s %(message)s')

# preload data
# prefix = os.getenv("DATA_DIR_URL")
# books_csv_path = 'Books.csv'
# books_df = pd.read_csv("/".join([prefix, books_csv_path]))

# model_api_url = 'http://model:5000/recommend_for_ISBN'
get_name_endpoint_url = 'http://recommender_service:5000/recommend_for_user_input'


@app.route('/recommend', methods=['POST'])
def recommend_for_name():
    """Calls recommender service API. Returns 502 if unavailable."""
    book_name = request.form['book_name']
    logging.warning(f"Calling recommender service for {book_name}")
    response = requests.post(get_name_endpoint_url, data={'book_name': book_name})
    if response.status_code == 200:
        # book_ISBN = book['ISBN']
        # book_ISBN = response.json['ISBN']
        # logging.warning(f"Calling recommender service for {book_ISBN}")
        # response = requests.post(model_api_url, data={'book_ISBN': book_ISBN})
        # if response.status_code == 200:
        logging.warning(f"Gateway returning {response.json()}")
        return response.json()
    else:
        logging.warning(f"Call to model_api failed: {response.status_code}, {response.text}")
        return jsonify({"message": "Recommender service unavailable", "status_code": 502, "data": {}})


if __name__ == "__main__":
    app.run()



