from flask import Flask, request, jsonify
import json
import logging
import os
import requests

# basic config and app setup
app = Flask(__name__)

logging.basicConfig(format='%(asctime)s %(message)s')

# endpoint_url = 'http://recommender_service:5000/recommend_for_user_input'
recommender_service_name = os.getenv('recommender_service_url')
recommender_service_port = os.getenv('recommender_service_port')

end_point_name = 'recommend_for_user_input'

endpoint_url = f'http://{recommender_service_name}:{recommender_service_port}/{end_point_name}'

@app.route('/recommend', methods=['POST'])
def recommend_for_name():
    """Calls recommender service API. Returns 502 if unavailable."""
    book_name = request.form['book_name']
    logging.warning(f"Calling recommender service for {book_name}")
    response = requests.post(endpoint_url, data={'book_name': book_name})
    if response.status_code == 200:
        logging.warning(f"Gateway returning {json.dumps(response.json(), indent=4)}")
        return response.json()
    else:
        logging.warning(f"Call to model_api failed: {response.status_code}, {response.text}")
        return jsonify({"message": "Recommender service unavailable", "status_code": 502, "data": {}})


if __name__ == "__main__":
    app.run()



