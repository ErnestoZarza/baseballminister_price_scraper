from price_scraper import BaseBallMinisterPriceScraper
from utils import ScrapeStatus


def main():
    try:
        scraper = BaseBallMinisterPriceScraper()
        category = 'softballschläger'
        result, statistics, scraper_status = scraper.get_prices(category=category)
        if scraper_status == ScrapeStatus.VALID_PRICES:
            print(statistics)
        elif scraper_status == ScrapeStatus.NOT_FOUND:
            print(f'Unfortunately we could not find prices for this category: {category}')
        else:
            print('An unexpected error happened while trying to scrape baseballminister.de')

    except Exception as e:
        print(
            f'Something went wrong while scraping prices from baseballminister.de: {e}'
        )


if __name__ == "__main__":
    main()
