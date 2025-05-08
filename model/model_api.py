from flask import Flask, request, abort


from model import get_implicit_ratings, load_data, recommend_books_for_book_ISBN
import logging

app = Flask(__name__)


# preload data to memory for fast access
_, books_df, ratings_df = load_data()
implicit_ratings, ratings_by_books = get_implicit_ratings(ratings_df)


@app.route('/recommend_for_ISBN', methods=['POST'])
def recommend_for_book_ISBN():
    """Recommends books for given ISBN. Expects body with keys book_ISBN and top_n.
    Return error when book_ISBN is missing.
    top_n results default to 5.
    Books are returned as json schema {book_index: {'ISBN': book_value,...}...}
    """
    
    if 'book_ISBN' not in request.form:
        abort(400, "Missing 'book_ISBN' in body.")

    book_ISBN = request.form['book_ISBN']
    logging.warning(f"Recommending for book {book_ISBN}")
    
    if 'top_n' in request.form:
        top_n = request.form['top_n']
    else:
        top_n = 5

    recommended_books_with_scores = recommend_books_for_book_ISBN(
                                book_ISBN,
                                ratings_by_books,
                                implicit_ratings, 
                                top_n=top_n,
                            )
    recommended_books_ISBN = [book[0] for book in recommended_books_with_scores]
    data = books_df[books_df['ISBN'].isin(recommended_books_ISBN)].to_json(orient='index')
    return data

def main():
    app.run()

if __name__ == "__main__":
    main()