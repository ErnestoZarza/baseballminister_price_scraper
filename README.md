# Baseball Minister price scraper


This small application is designed to scrape prices from the website Baseball Minister to study the prices of certain equipment needed to play baseball/softball. 

As a softball player it is necessary to have the right equipment to avoid injuries and achieve the best performance, and even better if you get a good deal for them.

## Getting Started

For extracting the data we are going to use the https://www.baseballminister.de/ website. 
Especially the search section, because it is easy to form the url with the category or keyword we are interested in.

Example: https://www.baseballminister.de/search/?qs=softballschläger


## Deployment

This application was implemented using the following technologies:


* [Python](https://www.python.org/) - Programming Language


## Requirements

* Python 3.x.x (3.12.3 recommend)


## Running the application

To run this application, clone the repository on your local machine and execute the following commands.

```
$ git clone https://github.com/ErnestoZarza/baseballminister_price_scraper.git
$ cd baseballminister_price_scraper
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt

Then....
$ python3 main.py
Scraping data for https://www.baseballminister.de/search/?qs=softballschläger
{'total_count': 80, 'avg_price': Decimal('71.26'), 'max_price': Decimal('165.01'), 'min_price': Decimal('9.95')}