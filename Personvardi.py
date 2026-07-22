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

        # The register also contains double names (e.g. "Nimmija Una"),
        # which the search endpoint returns as substring matches too.
        # Splitting into words lets us require a whole-word/phrase match
        # ("Una" inside "Nimmija Una") while still rejecting names that
        # merely contain the search term as a substring ("Guna", "Ūna").
        name_words = name.lower().split()
        word_count = len(name_words)

        rows = soup.select('table.table tbody tr')

        if not rows:
            # No rows are provided, that means, the word is incorrect.
            print(f'{name} not found')
            return data

        found_exact = False
        compound_count = 0

        for row in rows:
            # Table row contains cells which describe
            # the name, the count of registered names
            # and the date, when it's celebrated.
            cells = row.select('td')

            if not cells:
                continue

            row_name = cells[0].text
            row_words = row_name.lower().split()

            is_match = any(
                row_words[i:i + word_count] == name_words
                for i in range(len(row_words) - word_count + 1)
            )

            if not is_match:
                # Found name does not match the one we are searching for,
                # for example, "Dans" does not match "Bogdans".
                # We can skip this row.
                continue

            row_count = int(cells[1].text)

            if row_name.lower() != name.lower():
                # A double name that fully contains the searched name as
                # one of its parts (e.g. "Nimmija Una" contains "Una").
                # Its registrations count towards the searched name too,
                # but it has no detail page of its own to follow.
                compound_count += row_count
                continue

            found_exact = True
            data['name'] = row_name.capitalize()   # The first cell contains name.
            data['count'] = row_count              # The second cell contains count of the registered names.
            data['explanation'] = None             # Be default, the name explanation is empty.

            # Table row also can contain a link inside one
            # of the cells, therefore we are searching for it.
            link = row.find('a')

            if not link or not link.get('href'):
                # Link does not exist, we already have everything we can.
                continue

            # Each href looks like "./index.php?name=14427".
            # We can use the base_url and just append the path to it.
            path = link['href'][1:]
            soap = self.__request_data(path)
            data.update(self.__process_name_details(soap))

        if not found_exact and compound_count == 0:
            print(f'{name} not found')
            return {}

        if not found_exact:
            data['name'] = name.capitalize()
            data['count'] = 0
            data['explanation'] = None

        data['count'] += compound_count

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
