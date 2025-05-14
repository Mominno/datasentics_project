from collections import defaultdict
import pandas as pd
import re


def clear_ratings_from_unknown_ISBNS(ratings_df, books_df):
    indices_to_drop = []
    is_isbn_in_books = defaultdict(bool)
    for ISBN in books_df['ISBN']:
        is_isbn_in_books[ISBN] = True

    for index, rated_book_ISBN in ratings_df['ISBN'].items():
        
        if not is_isbn_in_books[rated_book_ISBN]:
            # print(index, rated_book_ISBN)
            indices_to_drop.append(index)
    # print(indices_to_drop)
    print(f"Dropped {len(indices_to_drop)} indices.")
    return ratings_df.drop(indices_to_drop)


def check_dataset_ISBN(dataframe):
    # first transform isbn into correct format 
    dataframe['ISBN_is_valid'] = dataframe['ISBN'].apply(transform_ISBN)
    dataframe['ISBN_is_valid'] = dataframe['ISBN_is_valid'].apply(check_if_ISBN_is_valid)
    return dataframe


def get_clean_ISBN_values(dataframe):
	dataframe = check_dataset_ISBN(dataframe)
	return dataframe[dataframe['ISBN_is_valid']].reset_index(drop=True)


def transform_ISBN(isbn):
    pattern = "[xX0-9-]+"
    match = re.fullmatch(pattern, isbn)
    if match:
        return match.group(0)


def check_if_ISBN_is_valid(ISBN):
    if ISBN is None:
        return False
    total_weighted_sum = 0
    i = 10
    for num in ISBN:
        if num == 'X' or num == 'x':
            num = 10
        elif num == '-':
            continue
        total_weighted_sum += i * int(num)
        i -= 1
    return total_weighted_sum % 11 == 0


def add_new_index_to_books(books_df):
    sorted_books = books_df.sort_values(by=['Book-Author', 'Book-Title'])
    new_ids = []
    current_id = 0
    prev_title = None
    prev_author = None
    for index, row in sorted_books.iterrows():
        if prev_author is None or prev_title is None:
            prev_author = row['Book-Author']
            prev_title = row['Book-Title']
            new_ids.append(current_id)
            continue
    
        if row['Book-Author'] == prev_author:
            # same author
            if row['Book-Title'] != prev_title:
                current_id += 1
        else:
            current_id += 1
        new_ids.append(current_id)
        prev_author = row['Book-Author']
        prev_title = row['Book-Title']
    sorted_books['new-id'] = new_ids
    new_books_df = sorted_books.sort_index()#.to_csv('trans_books.csv')
    return new_books_df
        

def main():
	# load data 
	users_csv_path = './Users.csv'
	ratings_csv_path = './Ratings.csv'
	books_df = pd.read_csv('./Books.csv')
	users_df = pd.read_csv(users_csv_path)
	ratings_df = pd.read_csv(ratings_csv_path)

	books_df['Year-Of-Publication'] = books_df['Year-Of-Publication'].astype('category')
	books_df['Publisher'] = books_df['Publisher'].astype('category')

	# now clean from corrupted isbn
	clean_ratings_df = get_clean_ISBN_values(ratings_df)
	clean_books_df = get_clean_ISBN_values(books_df)
    # we could alternatively enhance our dataset by looking up these missing ISBNs and adding them in books_Df
    clean_ratings_df = clear_ratings_from_unknown_ISBNS(clean_ratings_df, books_df)

	clean_books_df_with_id = add_new_index_to_books(clean_books_df)

	clean_ratings_with_id = pd.merge(ratings_df, clean_books_df_with_id[['ISBN', 'new-id']], on='ISBN')


	# export cleaned data
	clean_books_df_with_id.to_csv('trans_books.csv')
	clean_ratings_with_id.to_csv('trans_ratings.csv')



if __name__ == '__main__':
	main()