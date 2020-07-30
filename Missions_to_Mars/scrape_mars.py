from splinter import Browser
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time

def init_browser(url):

    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)

    browser.visit(url)
    time.sleep(3)

    # HTML object
    html = browser.html

    browser.quit()
    
    # Parse HTML with Beautiful Soup
    return BeautifulSoup(html, 'html.parser')

def scrape():
    # Scrape the latest news headlie from the NASA Mars News Site
    # --------------------------------------------------------- #
    news_soup = init_browser('https://mars.nasa.gov/news/')

    # Retrieve latest news title and paragraph text and assign to variables
    news_article = news_soup.find('div', class_='list_text')
    news_title = news_article.find('a').text
    news_p = news_article.find('div', class_='article_teaser_body').text

    # --------------------------------------------------------- #
    # Scrape the featured image for JPL Mars Space Images website
    # --------------------------------------------------------- #
    featured_soup = init_browser('https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars')

    featured_image_url = featured_soup.find('a', class_='button fancybox')['data-fancybox-href']

    #concatenate shortened url to image with website url
    jpl_website = 'https://www.jpl.nasa.gov'
    featured_image_url = jpl_website + featured_image_url

    # --------------------------------------------------------- #
    # Scrape the latest Mars weather tweet from the Mars Weather twitter page
    # --------------------------------------------------------- #
    twit_soup = init_browser('https://twitter.com/marswxreport?lang=en')

    tweets = twit_soup.find_all('span', class_='css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0')

    tweet_text = []
    for tweet in tweets:
        tweet_text.append(tweet.text)

    weather_tweets = []
    for text in tweet_text:
        if 'InSight sol' in text:
            weather_tweets.append(text)

    mars_weather = weather_tweets[0]

    # --------------------------------------------------------- #
    # Scrape Mars Facts webpage table using Pandas
    # --------------------------------------------------------- #
    mars_facts_url = 'https://space-facts.com/mars/'

    tables = pd.read_html(mars_facts_url)
    df = tables[0]
    df.columns = ['', 'values']

    facts_html_table = df.to_html(index=False, justify='left')

    # --------------------------------------------------------- #
    # Scrape Mars Hemispheres website for several image URLs
    # --------------------------------------------------------- #
    # Need to use browser variable for this scrape, so can't call the init_browser function
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)

    mars_hemi_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(mars_hemi_url)

    # HTML object
    html = browser.html
    hemi_soup = BeautifulSoup(html, 'html.parser')

    hemisphere_image_urls = []
    main_url = 'https://astrogeology.usgs.gov'

    links = hemi_soup.find_all('a', class_='itemLink product-item')

    for link in links:
        heading = link.find('h3')
        if heading != None:
            text = heading.text

            browser.click_link_by_partial_text(text)
            time.sleep(2)
            html_temp = browser.html
            soup_temp = BeautifulSoup(html_temp, 'html.parser')

            img = soup_temp.find('img', class_='wide-image')
            short_url = img['src']
            img_url = main_url + short_url

            hemi_dict = {}
            hemi_dict['title'] = text
            hemi_dict['img_url'] = img_url
            hemisphere_image_urls.append(hemi_dict)

            browser.back()
    
    scraped_data_dict = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image_url": featured_image_url,
        "mars_weather": mars_weather,
        "facts_html_table": facts_html_table,
        "hemisphere_image_urls": hemisphere_image_urls
    }

    # Close the browser after scraping
    browser.quit()

    return scraped_data_dict



