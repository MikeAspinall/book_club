import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def scrape_website(url, timeout=10):
    """
    Scrape a website and return a BeautifulSoup object.

    Returns:
        BeautifulSoup object if successful, otherwise None.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()  # Raises for 4xx/5xx responses
        return BeautifulSoup(response.text, "html.parser")

    except requests.exceptions.RequestException as e:
        print(f"‼️ Skipping URL '{url}': {e}")
        return None
    

def extract_author_name(book, soup):
    """
    """
    author_name = soup.find('span', class_ ='ContributorLink__name').text
    if author_name:
        return author_name    
    else:
        print(f"‼️ Error in author_name for {book}")


def extract_author_link(book, soup):
    """
    """
    author_link = soup.find('a', class_ ='ContributorLink')['href']
    if author_link:
        return author_link    
    else:
        print(f"‼️ Error in author_link for {book}")


def extract_image(book, soup):
    """
    """
    image = soup.find('img', class_ ='ResponsiveImage', role = 'presentation')['src']
    if image:
        return image    
    else:
        print(f"‼️ Error in image for {book}")


def extract_genres(book, soup):
    """
    """
    # Find the container
    genres_list = soup.find("div", {"data-testid": "genresList"})

    # Find all genre label spans inside it
    if genres_list:
        try:
            genres = [g.get_text(strip=True) for g in genres_list.find_all("span", class_="Button__labelItem")]
        except:
            pass

        irrelevant_genres = ['Book Club',
                             'Audiobook',
                             'Adult',
                             'Novels',
                             'The United States Of America',
                             'Literary Fiction',
                             '...more']

        for g in irrelevant_genres:
            try:
                genres.remove(g)
            except ValueError as e:
                pass
    
        if genres:
            return genres
        else:
            genres = ['none']
            return genres


def extract_description(book, soup):
    """
    """
    description = soup.find('span', class_ ='Formatted').text
    description = description.replace("               ", "")
    description = re.sub(r"\n", " ", description)
    if description:
        return description    
    else:
        print(f"‼️ Error in description for {book}")


def extract_rating(book, soup):
    """
    """
    rating = soup.find('div', class_ ='RatingStatistics__rating').text
    if rating:
        return rating    
    else:
        print(f"‼️ Error in rating for {book}")


def extract_ratings_reviews(book, soup):
    """
    """
    ratings_count_raw = soup.find('div', class_ = "RatingStatistics__meta")['aria-label']
    
    matches = re.findall(r"(\d[\d,]*)\s+(?=ratings|reviews)", ratings_count_raw)
    counts = [m.replace(",", "") for m in matches]

    if matches and counts:
        ratings_count = counts[0]
        reviews_count = counts[1]
        return ratings_count, reviews_count
    else:
        print(f"‼️ Error in ratings_reviews for {book}")


def extract_publication_date(book, soup):
    """
    """
    featured_details = soup.find('div', class_ = "FeaturedDetails").text
    match = re.search(r"First published\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})", featured_details)
    
    if match:
        publication_date = match.group(1)
        return publication_date
    else:
        print(f"‼️ Error in publication_date for {book}")


def scrape_details(book,url):
    """
    """
    soup = scrape_website(url)
    if soup != None:
        image = extract_image(book,soup)
        author_link = extract_author_link(book,soup)
        author_name = extract_author_name(book,soup)
        genres = extract_genres(book,soup)
        description = extract_description(book,soup)
        rating = extract_rating(book,soup)
        no_ratings, no_reviews = extract_ratings_reviews(book,soup)
        publication_date = extract_publication_date(book,soup)

        df = pd.DataFrame({
            'Book': [book],
            'image': [image],
            'author_link': [author_link],
            'author_name': [author_name],
            'genres': [genres],
            'description': [description],
            'goodreads_rating': [rating],
            'no_ratings': [no_ratings],
            'no_reviews': [no_reviews],
            'publication_date': [publication_date]
        })
        print(f"✅ {book} details scraped")

        return df
    else:
        print(f"❌ {book} not scraped")