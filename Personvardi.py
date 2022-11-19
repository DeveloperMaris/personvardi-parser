import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class Personvardi:

    # Base url for the parser to load and scrape for the information.
    __base_url: str = 'https://personvardi.pmlp.gov.lv'

    # init method or constructor
    def __init__(self):
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)

        self.session = requests.Session()
        self.session.mount('https://', adapter)

    def search_by_name(self, name):
        # This function loads the url and parses it for a
        # specific name information.

        path = '/index.php?name=' + name.upper()
        soup = self.__request_data(path)
        data = self.__process_name_list(name, soup)

        return data

    def __process_name_list(self, name, soup):
        # Process a list of names to retrieve
        # the information for a specific name
        # Example: https://personvardi.pmlp.gov.lv/index.php?name=maris

        # A dictionary, which will contain all the necessary
        # information about the name, count of it and the
        # detailed explanation.
        data = {}

        # Search for the table in the page,
        # which contains all the information.
        for row in soup.select('table.table tbody tr'):
            # Table row contains cells which describe
            # the name, the count of registered names
            # and the date, when it's celebrated.
            cells = row.select('td')

            if not cells:
                # No rows are provided, that means, the word is incorrect.
                print(f'{name} not found')
                break

            if not cells[0].text.lower() == name.lower():
                # Found name does not match the one we are searching for,
                # for example, "Dans" does not match "Bogdans".
                # We can skip this row.
                continue

            data['name'] = cells[0].text.capitalize()   # The first cell contains name.
            data['count'] = int(cells[1].text)          # The second cell contains count of the registered names.
            data['explanation'] = None                  # Be default, the name explanation is empty.

            # Table row also can contain a link inside one
            # of the cells, therefore we are searching for it.
            link = row.find('a')

            if not link:
                # Link does not exist, but we already found everything we can,
                # we can skip other rows now.
                break

            href = link['href']

            if not href:
                # We found everything we can, we can skip other rows now.
                break

            # Each href looks like "./index.php?name=14427".
            # We can use the base_url and just append the path to it.
            path = href[1:]
            soap = self.__request_data(path)
            data = self.__process_name_details(soap)

            # We found everything we need, we can skip other rows now.
            break

        return data


    def __process_name_details(self, soup):
        # Process a list of information for a specific name
        # Example: https://personvardi.pmlp.gov.lv/index.php?name=45630

        # A dictionary, which will contain all the necessary
        # information about the name, count of it and the
        # detailed explanation.
        data = {}

        # Search for the table in the page,
        # which contains all the information.
        for row in soup.select('table.table tbody tr'):
            # Table row contains cells which are constructed
            # in the form of key | value.
            key = row.select('th')[0].text
            value = row.select('td')[0].text

            match key:
                case 'Vārds':
                    # Value contains name.
                    data['name'] = value.capitalize()

                case 'Sastopams':
                    # Value contains count of the registered names.
                    data['count'] = int(value)

                case 'Skaidrojums':
                    # Value contains name explanation possibly.
                    data['explanation'] = value if value else None

                case _:
                    # Other unneeded values are ignored.
                    pass

        return data

    def __request_data(self, path) -> BeautifulSoup:
        # Prepare a url for the request.
        url = self.__base_url + path
        response = self.session.get(url, timeout=10)

        if response.status_code != 200:
            print(response.raise_for_status())

        return BeautifulSoup(response.text, 'html.parser')
