from bs4 import BeautifulSoup
import concurrent.futures
import json, re, requests, time

# Base url for the parser to load and scrape for the information.
base_url = 'https://personvardi.pmlp.gov.lv'

def search_by_name(name):
    # This function loads the url and parses it for a
    # specific name information.

    # Prepare a url for the request.
    url = base_url + '/index.php?name=' + name.upper()
    request = requests.get(url)

    if request.status_code != 200:
        request.raise_for_status()
        return

    soup = BeautifulSoup(request.text, 'html.parser')

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
        data['explanation'] = None

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
        result = search_by_url(base_url + path)
        data = result

        # We found everything we need, we can skip other rows now.
        break

    return data

def search_by_url(url):
    # This function loads the url and parses it for a specific
    # name information from the provided url.

    request = requests.get(url)

    if request.status_code != 200:
        request.raise_for_status()

    soup = BeautifulSoup(request.text, 'html.parser')

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

# Names to search for.
names = ["maris", "māris", "irīna"]

# Collection of parsed names.
collection = []

# Debug information.
tm1 = time.perf_counter()

with concurrent.futures.ThreadPoolExecutor() as executor:
    # Collection of concurrent tasks.
    futures = []

    for name in names:
        # Search each name concurrently by it's name.
        futures.append(executor.submit(search_by_name, name=name))

    for future in concurrent.futures.as_completed(futures):
        data = future.result()
        # If search of the name returned necessary information,
        # add it to the collection.
        if data:
            collection.append(data)

# Debug information.
tm2 = time.perf_counter()

# Write output into a json file.
with open('output/results.json', 'w') as fp:
    json.dump(collection, fp, ensure_ascii=False)

# Debug information.
tm3 = time.perf_counter()

print(f'Parse time: {tm2-tm1:0.2f} seconds')
print(f'File write time: {tm3-tm2:0.2f} seconds')
print(f'Total time elapsed: {tm3-tm1:0.2f} seconds')
