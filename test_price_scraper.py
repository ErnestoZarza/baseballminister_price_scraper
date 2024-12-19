from decimal import Decimal
from unittest.mock import patch

import pytest

from price_scraper import BaseBallMinisterPriceScraper
from utils import DataHelper, ScrapeStatus


@pytest.fixture
def test_data():
    return DataHelper()


@pytest.fixture
def local_data(test_data):
    test_data.set_filepath(__file__)
    return test_data


@patch(
    'price_scraper.BaseBallMinisterPriceScraper._get_response_with_retry_strategy'
)
def test_baseball_minister_get_prices(mock_request, local_data):
    response = local_data.get_content('data/baseball_minister_softballschlaeger.html')
    mock_request.return_value.text = response
    mock_request.return_value.status_code = 200
    scraper = BaseBallMinisterPriceScraper()
    result, price_statistics, status = scraper.get_prices()

    expected_data = [
        {'price': Decimal('89'), 'brand': 'Rawlings'},
        {'price': Decimal('110'), 'brand': 'Easton'},
        {'price': Decimal('49'), 'brand': 'Easton'}
    ]
    expected_statistics = {
        'avg_price': Decimal('71.26'),
        'max_price': Decimal('165.01'),
        'min_price': Decimal('9.95'),
        'total_count': 80
    }

    assert result[:3] == expected_data
    assert price_statistics == expected_statistics
    assert status == ScrapeStatus.VALID_PRICES


@patch(
    'price_scraper.BaseBallMinisterPriceScraper._get_response_with_retry_strategy'
)
def test_baseball_minister_get_prices__no_results_response(mock_request, local_data):
    response = local_data.get_content('data/baseballminister_no_results.html')
    mock_request.return_value.text = response
    mock_request.return_value.status_code = 200
    scraper = BaseBallMinisterPriceScraper()
    result, statistics, scraper_status = scraper.get_prices()

    assert result == []
    assert statistics == {}
    assert scraper_status == ScrapeStatus.NOT_FOUND
