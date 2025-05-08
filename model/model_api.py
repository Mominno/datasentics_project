from flask import Flask, request

from model import get_implicit_ratings, load_data, recommend_books_for_book_ISBN

app = Flask(__name__)

_, books_df, ratings_df = load_data()
implicit_ratings, ratings_by_books = get_implicit_ratings(ratings_df)

@app.route('/recommend_for_ISBN', methods=['POST'])
def recommend_for_book_ISBN():
	# Model already presumes we goot a correct name but lets still check to be sure
	# first try to find book in data
	if 'book_ISBN' not in request.form:
		return jsonify({'code': 400,'message': "Missing 'book_ISBN' in body."})
	book_ISBN = request.form['book_ISBN']
	# get list of book_names
	if 'top_n' in request.form:
		top_n = request.form['top_n']
	else:
		top_n = 5

	# book_names = books_df['Book-Name'].unique()
	# if book_name not in book_names:
	# 	return {'message': 'book not found in dataset'}
	
	# get ISBN for name
	# book_ISBN = find_book_ISBN_in_dataset(book_name)
	recommended_books_ISBN = recommend_books_for_book_ISBN(
								book_ISBN,
								ratings_by_books,
								implicit_ratings, 
								top_n=top_n,
							)
	# here add titles authors and shiny stuff-
	return recommended_books_ISBN

def main():
	app.run()

if __name__ == "__main__":
	main()