# -*- coding: utf-8 -*-
from django.shortcuts import render
from forms.forms import UserForm
import numpy as np
import pandas as pd
import isbnlib
import pages.my_path
import requests
import os
import zipfile
import pages.Tools


def index(request):
    submitbutton = request.POST.get("submit")

    bookname = ''
    authorname = ''
    result_list = []
    worst_list = []
    result_list_html = []

    # Upload from URL and unzip
    zipurl = 'http://www2.informatik.uni-freiburg.de/~cziegler/BX/BX-CSV-Dump.zip'
    resp = requests.get(zipurl)
    # assuming the subdirectory tempdata has been created:
    zname = os.path.join(r'pages\data', "BX-CSV-Dump.zip")
    zfile = open(zname, 'wb')
    zfile.write(resp.content)
    zfile.close()
    #
    with zipfile.ZipFile(r'pages\data\BX-CSV-Dump.zip', 'r') as zip_ref:
        zip_ref.extractall(r'pages\data')
    #
    # # path to upload files
    #
    # # replace special char '\"' in CSV
    # string = r'pages\data\BX-Book-Ratings.csv'
    # string2 = r'pages\data\BX-Books.csv'
    #
    # pages.Tools.replace_special_char(string)
    # pages.Tools.replace_special_char(string2)

    form = UserForm(request.POST or None)
    if form.is_valid():
        bookname = form.cleaned_data.get("book_name")
        authorname = form.cleaned_data.get("author_name")

        bookname = bookname.lower()
        authorname = authorname.lower()

        files_path = pages.my_path.my_path()
# ----

        # load ratings
        # path should be in diff file
        ratings = pd.read_csv(files_path + r'\BX-Book-Ratings.csv', encoding='cp1251', sep=';')
        ratings = ratings[ratings['Book-Rating'] != 0]
        # ISBN check in ratings
        ratings['validISBN'] = ''
        ratings['validISBN'] = ratings['ISBN'].apply(isbnlib.is_isbn10)
       # print(ratings[ratings.duplicated(keep=False)])  # duplicates check

        # load books
        books = pd.read_csv(files_path + r'\BX-Books.csv', encoding='cp1251', sep=';', error_bad_lines=False)
        # ISBN check in books
        books['validISBN'] = ''
        books['validISBN'] = books['ISBN'].apply(isbnlib.is_isbn10)
        #print(books[books.duplicated(keep=False)])

        dataset = pd.merge(ratings, books, on=['ISBN'])  # rather use all merge parameters - better for code-reader

        dataset['ISBN'] = dataset.ISBN.astype(str)

        # dataset_lowercase = dataset.apply(lambda x: x.str.lower() if (x.dtype == 'object') else x) //doesnt work for me - debugging
        dataset_lowercase = dataset.apply(lambda x: x.astype(str).str.lower())
        dataset['ISBN'] = dataset['ISBN'].str.upper()  # doesn't need to be - just x in ISBN looks strange

        # Upload all readers (user_id) of the fellowship of the ring (the lord of the rings, part 1 and also where author is Tolkien
        tolkien_readers = dataset_lowercase['User-ID'][
            (dataset_lowercase['Book-Title'] == bookname) & (
                dataset_lowercase['Book-Author'].str.contains(authorname))]

        tolkien_readers = tolkien_readers.tolist()
        tolkien_readers = np.unique(tolkien_readers)

        # final dataset - books read by tolkien readers
        books_of_tolkien_readers = dataset_lowercase[(dataset_lowercase['User-ID'].isin(tolkien_readers))]

        # Number of ratings per other books in dataset
        number_of_rating_per_book = books_of_tolkien_readers.groupby(['Book-Title']).agg('count').reset_index()
        # select only books which have actually higher number of ratings than threshold
        books_to_compare = number_of_rating_per_book['Book-Title'][number_of_rating_per_book['User-ID'] >= 8]

        books_to_compare = books_to_compare.tolist()
        ratings_data_raw = books_of_tolkien_readers[['User-ID', 'Book-Rating', 'Book-Title']][
            books_of_tolkien_readers['Book-Title'].isin(books_to_compare)]
        # MN need to convert Book Rating to int and fill NA
        ratings_data_raw['Book-Rating'].fillna(value=0, inplace=True)
        ratings_data_raw['Book-Rating'] = pd.to_numeric(ratings_data_raw['Book-Rating'])

        # group by User and Book and compute mean
        ratings_data_raw_nodup = ratings_data_raw.groupby(['User-ID', 'Book-Title'])['Book-Rating'].mean()

        # print('rating prumer')
        # print(ratings_data_raw_nodup)

        # reset index to see User-ID in every row
        ratings_data_raw_nodup = ratings_data_raw_nodup.to_frame().reset_index()

        dataset_for_corr = ratings_data_raw_nodup.pivot(index='User-ID', columns='Book-Title', values='Book-Rating')

        # print('Dataset For Cor ------------------')
        # print(dataset_for_corr)

        LoR_list = [
            bookname]  # // do we really need list???? - only value



        # for each of the trilogy book compute:
        for LoR_book in LoR_list:

            # Take out the Lord of the Rings selected book from correlation dataframe
            dataset_of_other_books = dataset_for_corr.copy(deep=False)
            # print('dataset_of_otherbooks deeps false before drop')
            # print(dataset_of_other_books)
            dataset_of_other_books.drop([LoR_book], axis=1, inplace=True)

            # print('Dataset_of_other_books without LoR_list')
            # print(dataset_of_other_books)
            # empty lists
            book_titles = []
            correlations = []
            avgrating = []

            # corr computation - this doesnt make sense to me at all
            for book_title in list(dataset_of_other_books.columns.values):

                book_titles.append(book_title)
                correlations.append(dataset_for_corr[LoR_book].corr(dataset_of_other_books[book_title]))

                tab = (ratings_data_raw[ratings_data_raw['Book-Title'] == book_title].groupby(
                    ratings_data_raw['Book-Title']).mean())
                avgrating.append(tab['Book-Rating'].min())
            # final dataframe of all correlation of each book
            corr_fellowship = pd.DataFrame(list(zip(book_titles, correlations, avgrating)),
                                           columns=['book', 'corr', 'avg_rating'])
            # print(corr_fellowship.head())

            # top 10 books with highest corr
            result_list.append(corr_fellowship.sort_values('corr', ascending=False).head(10))

            # worst 10 books
            worst_list.append(corr_fellowship.sort_values('corr', ascending=False).tail(10))
             # print("Correlation for book:", LoR_list[0])
             # print("Average rating of LOR:", ratings_data_raw[ratings_data_raw['Book-Title']=='the fellowship of the ring (the lord of the rings, part 1'].groupby(ratings_data_raw['Book-Title']).mean()))
            # result_numpy = np.array(result_list)
            # result_numpy = result_numpy.shape()
            # result_list_df = pd.DataFrame(result_numpy)
            # result_list_html = result_list_df.to_html()
            names = ['book', 'corr', 'avg_rating']
            result_list_np = np.array(result_list)
            result_list_pd = pd.DataFrame([list(l) for l in result_list_np]).stack().apply(pd.Series).reset_index(0,
                                                                                                                  drop=True)
            result_list_pd.columns = list(names)
            result_list_html = result_list_pd.to_html()

# -----
    context = {'form': form, 'bookname': bookname, 'authorname': authorname,
               'submitbutton': submitbutton, 'result_list_html': result_list_html}

    return render(request, 'pages/index.html', context)
