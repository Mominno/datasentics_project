from collections import Counter
import os
import pandas as pd


def get_implicit_ratings(ratings_df):
    """Filter ratings with implicit ratings (represented by 0)
    and groups these ratings by book ISBN.

    Returns tuple of (implicit_ratings, ratings_groupby_book)
    """
    implicit_ratings = ratings_df[ratings_df['Book-Rating'] == 0]
    ratings_by_books = implicit_ratings.groupby("ISBN")
    return implicit_ratings, ratings_by_books

def load_data():
    """Return tuple of dataframes in order (users, books, ratings).
        Expects path in environment variables under DATA_DIR_URL key.
    """
    prefix = os.getenv("DATA_DIR_URL" )

    users_csv_path = 'Users.csv'
    ratings_csv_path = 'Ratings.csv'
    books_csv_path = 'Books.csv'
    users_df = pd.read_csv("/".join([prefix, users_csv_path]))
    ratings_df = pd.read_csv("/".join([prefix, ratings_csv_path]))
    books_df = pd.read_csv("/".join([prefix, books_csv_path]))
    return users_df, books_df, ratings_df


def recommend_books_for_book_ISBN(book_ISBN, ratings_by_books, implicit_ratings, top_n=5):
    """Simple colaborative filtering recommendation technique. For given book, retrieve all people who read it,
    then retrieve all the books theyve collectively read and return top_n most common.
    """
    indices = ratings_by_books.groups[book_ISBN]
    user_ids = implicit_ratings.loc[indices, 'User-ID'].values
    return Counter(implicit_ratings[implicit_ratings['User-ID'].isin(user_ids)]['ISBN'].values).most_common(top_n)

    
