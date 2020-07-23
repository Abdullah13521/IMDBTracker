import requests
from bs4 import BeautifulSoup
import pandas as pd
from test import SendMessage
import lxml

# Enter your account email
sender = "email"
receivers = ["", ""]

top_movies_url = 'https://www.imdb.com/chart/top/'
top_tv_url = 'https://www.imdb.com/chart/toptv/'

# get the top movies and tv shows
movie_page = requests.get(top_movies_url)
movie_soup = BeautifulSoup(movie_page.content, 'lxml')

tv_page = requests.get(top_tv_url)
tv_soup = BeautifulSoup(tv_page.content, 'lxml')

movieActors = []
movieTitles = []
movieDirectors = []
tvActors = []
tvTitles = []

def findInfo(soup, actors, titles, directors = None):
    """ Finds the actors and titles for tv shows or movies and fills them """
    # filter for only the required info
    allInfo = soup.findAll('td', class_ = 'titleColumn')

    # check if it's for movies
    if directors != None:
        for movie in allInfo:
            stars = movie.find('a')['title'].split(',')
            actors.append(stars[1:])
            directors.append(stars[:1])
            movieTitle = movie.find('a').contents[0]
            titles.append(movieTitle)
    else:
        for movie in allInfo:
            stars = movie.find('a')['title'].split(',')
            actors.append(stars)
            movieTitle = movie.find('a').contents[0]
            titles.append(movieTitle)

movieRatings = []
tvRatings = []

def getRatings(soup, ratings):
    """ gets the rating for every movie or tv show """
    allRatings = soup.findAll('td', class_ ='ratingColumn imdbRating')

    for rating in allRatings:
        ratings.append(float(rating.find('strong').contents[0]))

# fill the lists with the required info
findInfo(movie_soup, movieActors, movieTitles, movieDirectors)
getRatings(movie_soup, movieRatings)

findInfo(tv_soup, tvActors, tvTitles)
getRatings(tv_soup, tvRatings)

# create two data frames for the info
movies = pd.DataFrame(list(zip(movieTitles, movieActors, movieDirectors, movieRatings)), columns = ['Movie Title', 'Actors', 'Director', 'Rating'])
shows = pd.DataFrame(list(zip(tvTitles, tvActors, tvRatings)), columns = ['Show Title', 'Actors', 'Rating'])

# get the old movies and show info from the csv files
oldTopMovies = pd.read_csv('top_movies.csv')
oldTopShows = pd.read_csv('top_shows.csv')

# compare the old movies and shows
newMovies = movies[oldTopMovies['Movie Title'] != movies['Movie Title']]
newShows = shows[oldTopShows['Show Title'] != shows['Show Title']]

# check if there's new top movies
if len(newMovies) > 0:
    # Send an email to notify
    titles = '\n'.join(newMovies['Movie Title'])

    # loop through each receiver
    for receiver in receivers:
        SendMessage(sender, receiver, "New Top Movie!", "",
        "New movies have been added to the top 250!\n" + titles)

# check if there's new top shows
if len(newShows) > 0:
    # Send an email to notify
    titles = '\n'.join(newShows['Show Title'])

    # loop through each receiver
    for receiver in receivers:
        SendMessage(sender, receiver, "New Top Show!", "",
        "New shows have been added to the top 250!\n" + titles)

# export the new files
movies.to_csv("top_movies.csv", index=False)
shows.to_csv("top_shows.csv", index=False)
