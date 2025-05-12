from flask import Flask, request, render_template, abort
import json
import logging
import os
import requests

# basic config and app setup
app = Flask(__name__)

gateway_service_name = os.getenv('gateway_service_url')
gateway_service_port = os.getenv('gateway_service_port')
end_point_name = 'recommend'
# api_gateway_get_book = 'http://gateway:5000/recommend'

api_gateway_get_book = f'http://{gateway_service_name}:{gateway_service_port}/{end_point_name}'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', template_folder='/templates')
    else:
        book_name = request.form['book_name']
        # here make call to api gateway
        response = requests.post(api_gateway_get_book, data={'book_name': book_name})
        if response.status_code == 200:
            response_json = response.json()
            cached_data = response_json['data']
            books = list(json.loads(cached_data).values())
            model_book = json.loads(response_json['model_book'])
            logging.debug(f'{model_book = }')
            return render_template('returned_book_items.html', template_folder='/templates', books=books, model_book=model_book)
        else:
            logging.warning(f"Call to gateway failed: {response.status_code}, {response.text}")
            return render_template('index.html', template_folder='/templates')

if __name__ == "__main__":
    app.run()