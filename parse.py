from bs4 import BeautifulSoup
import concurrent.futures
import json
import requests
import time

min_record_id = 2
max_record_id = 127130
base_url = 'https://personvardi.pmlp.gov.lv/index.php?name='

def get_data(url):
    request = requests.get(url)

    if request.status_code != 200:
        request.raise_for_status()

    soup = BeautifulSoup(request.text, 'html.parser')
    data = {}

    for item in soup.select('table.table tr'):
        key = item.select('th')[0].text
        value = item.select('td')[0].text

        match key:
            case 'Vārds':
                data['name'] = value.lower()

            case 'Sastopams':
                data['count'] = int(value)

            case 'Skaidrojums':
                data['explanation'] = value if value else None

            case _:
                pass

    return data

collection = []
tm1 = time.perf_counter()

with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []

    for record_id in range(min_record_id, 1000):
        url = base_url + str(record_id)
        futures.append(executor.submit(get_data, url=url))

    for future in concurrent.futures.as_completed(futures):
        data = future.result()
        if data:
            collection.append(data)

tm2 = time.perf_counter()

with open('output/results.json', 'w') as fp:
    json.dump(collection, fp)

tm3 = time.perf_counter()

print(f'Parse time: {tm2-tm1:0.2f} seconds')
print(f'File write time: {tm3-tm2:0.2f} seconds')
print(f'Total time elapsed: {tm3-tm1:0.2f} seconds')
