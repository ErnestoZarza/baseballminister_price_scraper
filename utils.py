from enum import Enum
import os


USER_AGENT_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/117.0.5938.132 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/117.0.5938.132 Safari/537.36 Edg/117.0.2045.43",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_1) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Version/16.5 Safari/537.36",
]


class ScrapeStatus(Enum):
    VALID_PRICES = 1
    NOT_FOUND = 2
    REQUEST_ERROR = 3
    PARSING_ERROR = 4
    TOO_MANY_REQUESTS_ERROR = 5
    SERVER_ERROR = 6
    OTHER_ERROR = 7


class DataHelper:
    def __init__(self):
        self.file_path = None

    def set_filepath(self, filepath):
        self.file_path = filepath

    def get_content(self, relative_path):
        abs_path = os.path.join(os.path.dirname(self.file_path), relative_path)
        with open(abs_path, 'r') as file:
            return file.read()
