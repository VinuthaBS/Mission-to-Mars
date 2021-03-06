# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup

import pandas as pd
import datetime as dt

# Set the executable path and initialise chrome browser in splinter
def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': '/Users/vinuthaphani/.wdm/drivers/chromedriver/mac64/87.0.4280.88/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemisphere_data(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try / except for error handling
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
    
    except AttributeError:
        return None, None

    return news_title, news_p

# ### Featured Images
def featured_image(browser):

    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Check if the Full Image link exists on the loaded page and enter SCRAPE code only if it exists 
    # else update the return variable with static text indicating the change in the html design of webpage
    scrape_yn = browser.is_element_present_by_id('full_image', wait_time=1)
    if (scrape_yn == False):
        img_url = None
        # https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars
    else:
        # Start of SCRAPE code
        # Find and click the full image button
        full_image_elem = browser.find_by_id('full_image')
        full_image_elem.click()

        # Find the more info button and click that
        browser.is_element_present_by_text('more info', wait_time=1)
        more_info_elem = browser.links.find_by_partial_text('more info')
        more_info_elem.click()

        # Parse the resulting html with soup
        html = browser.html
        img_soup = soup(html, 'html.parser')

        try:
            # Find the relative image url
            img_url_rel = img_soup.select_one('figure.lede a img').get("src")
        
        except AttributeError:
            return None

        # Use the base URL to create an absolute URL
        img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

# ### Mars Facts Table Scrape
def mars_facts():
    try:
        # use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
      return None

    df.columns=['Description', 'Value']
    df.set_index('Description', inplace=True)

    return df.to_html()

# ### Hemisphere data scrape
def hemisphere_data(browser):

    # Visit hemisphere data URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    
    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []
    
    # 3. Code to retrieve the image urls and titles for each hemisphere.
    links = browser.find_by_css('a.itemLink.product-item h3')

    # loop through each of the links on the main page corresponding to each hemisphere
    for num in range(len(links)):
    
        # dictionary to hold img_url and title
        hemisphere = {}
        # click the h3 tag link having the hemisphere title to get the jpg image
        browser.find_by_css('a.itemLink.product-item h3')[num].click()
        # identify the jpg link to get full resolution image
        img_jpg = browser.find_by_text("Sample").first
        # write the img_url into hemisphere dict
        hemisphere["img_url"] = img_jpg["href"]
        # write the title into hemisphere dict
        hemisphere["title"] = browser.find_by_css("h2.title").text
        # append the updated dict to the hemisphere_image_urls list
        hemisphere_image_urls.append(hemisphere)
        # get back to the initial page to pick the next hemisphere link
        browser.back()

    return hemisphere_image_urls


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())