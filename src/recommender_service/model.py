from collections import Counter
import logging
import os
import pandas as pd

book_ID_column_name = 'new-id'

RESULTS_TO_RECOMMEND = 10

def get_implicit_ratings(ratings_df):
    """Filter ratings with implicit ratings (represented by 0)
    and groups these ratings by book ISBN.

    Returns tuple of (implicit_ratings, ratings_groupby_book)
    """
    implicit_ratings = ratings_df[ratings_df['Book-Rating'] == 0]
    return implicit_ratings

def load_data():
    """Return tuple of dataframes in order (users, books, ratings).
        Expects path in environment variables under DATA_DIR_URL key.
    """
    users_df_url = os.getenv("USERS_DATA_URL")
    ratings_df_url = os.getenv("RATINGS_DATA_URL")
    books_df_url = os.getenv("BOOKS_DATA_URL")

    users_df = pd.read_csv(users_df_url)
    ratings_df = pd.read_csv(ratings_df_url)
    books_df = pd.read_csv(books_df_url)

    return users_df, books_df, ratings_df, book_ID_column_name


def recommend_books_for_book_ISBN(book_ISBN, implicit_ratings, books_df, top_n=RESULTS_TO_RECOMMEND):
    """Simple colaborative filtering recommendation technique. For given book, retrieve all people who read it,
    then retrieve all the books theyve collectively read and return top_n most common.
    """
    logging.warning(f"Recommending for book {book_ISBN}")

    try:
        user_ids = implicit_ratings[implicit_ratings['ISBN'] == book_ISBN]['User-ID'].values
        recommended_books_with_scores = get_most_common_books_for_users(user_ids, implicit_ratings, top_n=top_n)
        return get_json_from_book_scores(recommended_books_with_scores, books_df)
    except KeyError as e:
        return "{}"


def get_most_common_books_for_users(user_ids, implicit_ratings, top_n=RESULTS_TO_RECOMMEND):
    return Counter(implicit_ratings[implicit_ratings['User-ID'].isin(user_ids)]['ISBN'].values).most_common(top_n)

def get_json_from_book_scores(books_with_scores, books_df):
    """Utility method for transforming results to json."""
    recommended_books_ISBN = [book[0] for book in books_with_scores]
    data_json = books_df[books_df['ISBN'].isin(recommended_books_ISBN)].to_json(orient='index')
    return data_json


def recommend_books_for_book_ID(book_ID, implicit_ratings, books_df, top_n=RESULTS_TO_RECOMMEND):
    """Simple colaborative filtering recommendation technique. For given book, retrieve all people who read it,
    then retrieve all the books theyve collectively read and return top_n most common.
    """
    if book_ID_column_name in implicit_ratings.columns:
        user_ids = implicit_ratings[implicit_ratings[book_ID_column_name] == book_ID]['User-ID'].values
        recommended_books_with_scores = get_most_common_books_for_users(user_ids, implicit_ratings, top_n=top_n)
        return get_json_from_book_scores(recommended_books_with_scores, books_df)
    else:
        return "{}"


def find_book_in_dataset(book_string, books_df):
    """ Find book entry in dataset from string. 
        Splits string into words and return results containing all words in book_string.
        Case insensitive.
        For simplicity return just first result.
    """

    books_with_lower = books_df['Book-Title'].str.lower()
    book_string = book_string.lower().split(" ")
    bool_indices = books_with_lower.str.contains(book_string[0])
    
    for word in book_string:
        bool_indices = bool_indices & books_with_lower.str.contains(word)
    logging.warning(f"Found {len(books_df[bool_indices])} possible results for string {book_string}")

    return books_df[bool_indices].iloc[0]
