# Domain.com.au result scraper
# TODO: Google maps API to get nearest train station and walking time to station
# TODO: nbn API to find when and what nbn

from bs4 import BeautifulSoup
from urllib.request import urlopen
import re

# URL stuff
base_url = "https://www.domain.com.au/rent/?suburb=newtown-nsw-2042,redfern-nsw-2016,enmore-nsw-2042&ptype=apartment-unit-flat&bedrooms=3&ssubs=1&sort=dateupdated-desc&excludedeposittaken=1"
page_modifier = '&page='
page_num = 1
url = base_url + page_modifier + str(page_num)

# Load the first page
page = urlopen(url)
soup = BeautifulSoup(page, 'html.parser')

# Get total number of pages
page_num_max = int(soup.find_all('a', attrs={'class': 'paginator__page-button'})[-1].text)

# Get search results
listings = soup.find_all('li', attrs={'class': 'search-results__listing'})

listing_dict = {}
while page_num <= page_num_max:
    if page_num > 1:
        url = base_url + page_modifier + str(page_num)
        page = urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')
        listings = soup.find_all('li', attrs={'class': 'search-results__listing'})

    for listing in listings:
        # Get the price
        price = listing.find('p', attrs={'class': 'listing-result__price'})
        if price is not None:
            # Get the text
            price_text = price.text

            # filter out the garbage around the actual price
            price_text = price_text.replace(',', '').replace('$', '')
            price_possibilities = price_text.split('$')[0].split(' ')
            for price_possibility in price_possibilities:
                # 5 digits is too many
                if len(price_possibility) > 4:
                    price_possibility = price_possibility[0:4]
                    # Decimal points are of no concern now
                    price_possibility = price_possibility.replace('.', '')

                # Remove all the extra text
                price_possibility = re.sub('[^0-9]', '', price_possibility)

                # If it's a number it's our number
                if price_possibility.isdigit():
                    price = price_possibility
        else:
            # If there is no price, don't even bother
            continue

        # Get the address
        address = listing.find('meta', attrs={'itemprop': 'name'})
        if address is not None:
            address = str(address)
            # cbf finding the proper way to do this
            address = address.split("<meta content=\"")[-1].split("\" data-reactid=\"")[0]

        # Get Bedroom, Bathroom, and Car park numbers
        bed_num = 0
        bath_num = 0
        car_num = 0
        property_features = listing.find_all('span', attrs={'class': 'property-feature__feature-text-container'})
        if property_features:
            bed_num = int(property_features[0].text[0])
            bath_num = int(property_features[1].text[0])
            car_num = property_features[2].text[0]
            if car_num == '−':
                car_num = 0
            else:
                car_num = int(car_num)

        # Get URL
        url = listing.find_all('a', href=True)
        if url:
            url = url[0]['href']

        # Add the listing to the dictionary

        listing_dict[url] = {
            'price': price,
            'address': address,
            'bedrooms': bed_num,
            'bathrooms': bath_num,
            'cars': car_num
        }

    # Get ready for the next page
    page_num += 1
print(listing_dict)