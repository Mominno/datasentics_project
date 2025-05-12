# import
import pandas as pd
import numpy as np

# load ratings # load books
path_to_ratings = 'Downloads/BX-Book-Ratings.csv'
path_to_books = 'Downloads/BX-Books.csv'

RATING_PER_BOOK_THRESHOLD = 8

def load_data(path_to_ratings, path_to_books):
    ratings = pd.read_csv(path_to_ratings, encoding='cp1251', sep=';')
    ratings = ratings[ratings['Book-Rating']!=0]
    books = pd.read_csv(path_to_books,  encoding='cp1251', sep=';',error_bad_lines=False)
    return books, ratings


def transform_data(books, ratings):
    dataset = pd.merge(ratings, books, on=['ISBN'])
    dataset_lowercase=dataset.apply(lambda x: x.str.lower() if(x.dtype == 'object') else x)
    return dataset_lowercase

def get_users_for_book_and_author(book, author, dataset):
    readers = dataset_lowercase['User-ID'][(dataset_lowercase['Book-Title']==book) & (dataset_lowercase['Book-Author'].str.contains(author))]
    readers = readers.tolist()
    readers = np.unique(readers)
    return readers

def get_dataset_with_correlations(readers, dataset_lowercase):
    books_of_tolkien_readers = dataset_lowercase[(dataset_lowercase['User-ID'].isin(readers))]

    # Number of ratings per other books in dataset
    number_of_rating_per_book = books_of_tolkien_readers.groupby(['Book-Title']).agg('count').reset_index()

    #select only books which have actually higher number of ratings than threshold

    books_to_compare = number_of_rating_per_book['Book-Title'][number_of_rating_per_book['User-ID'] >= RATING_PER_BOOK_THRESHOLD]
    books_to_compare = books_to_compare.tolist()

    ratings_data_raw = books_of_tolkien_readers[['User-ID', 'Book-Rating', 'Book-Title']][books_of_tolkien_readers['Book-Title'].isin(books_to_compare)]

    # group by User and Book and compute mean
    ratings_data_raw_nodup = ratings_data_raw.groupby(['User-ID', 'Book-Title'])['Book-Rating'].mean()

    # reset index to see User-ID in every row
    ratings_data_raw_nodup = ratings_data_raw_nodup.to_frame().reset_index()

    dataset_for_corr = ratings_data_raw_nodup.pivot(index='User-ID', columns='Book-Title', values='Book-Rating')
    return dataset_for_corr

def compute_correlations_for_book(LoR_book, dataset_for_corr, n_books_to_fetch=10):
    #Take out the Lord of the Rings selected book from correlation dataframe
    dataset_of_other_books = dataset_for_corr.copy(deep=False)
    ## usage of inplace keyword is deprecated - it should be clear that value is being overwritten
    dataset_of_other_books.drop([LoR_book], axis=1, inplace=True)
      
    # empty lists
    book_titles = []
    correlations = []
    avgrating = []

    # corr computation
    for book_title in list(dataset_of_other_books.columns.values):
        book_titles.append(book_title)
        correlations.append(dataset_for_corr[LoR_book].corr(dataset_of_other_books[book_title]))
        tab=(ratings_data_raw[ratings_data_raw['Book-Title']==book_title].groupby(ratings_data_raw['Book-Title']).mean())
        avgrating.append(tab['Book-Rating'].min())
    # final dataframe of all correlation of each book   
    corr_fellowship = pd.DataFrame(list(zip(book_titles, correlations, avgrating)), columns=['book','corr','avg_rating'])
    corr_fellowship.head()

    # top 10 books with highest corr
    result_list.append(corr_fellowship.sort_values('corr', ascending = False).head(n_books_to_fetch))
    
    #worst 10 books
    worst_list.append(corr_fellowship.sort_values('corr', ascending = False).tail(n_books_to_fetch))
    return result_list, worst_list

if __name__ == "__main__":
    books, ratings = load_data(path_to_ratings, path_to_books)
    dataset_lowercase = transform_data(books, ratings)

    book = 'the fellowship of the ring (the lord of the rings, part 1)'
    author = "tolkien"
    readers = get_users_for_book_and_author(book, author, dataset_lowercase)
    dataset_for_corr = get_dataset_with_correlations(readers, dataset_lowercase)
    result_list, worst_list = compute_correlations_for_book(book, dataset_for_corr)        
    print("Correlation for book:", book)
    #print("Average rating of LOR:", ratings_data_raw[ratings_data_raw['Book-Title']=='the fellowship of the ring (the lord of the rings, part 1'].groupby(ratings_data_raw['Book-Title']).mean()))
    print(result_list)