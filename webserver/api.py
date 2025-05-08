# recommender wrapper api

from flask import Flask, request, render_template
import time
import redis

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)

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

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
	data = request.form 
	return data
	# return render_template('greeting.html', say=request.form['book'])

@app.route('/', methods=['GET'])
def index():
	return render_template('index.html')

@app.route('/hello')
def hello():
    count = get_hit_count()
    return f'Hello World! I have been seen {count} times.\n'

if __name__ == "__main__":
	app.run()



