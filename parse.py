from Personvardi import Personvardi
import concurrent.futures
import json, time

# Names to search for.
names = []

with open('input/names_extended.json') as json_file:
    names = json.load(json_file)

# Collection of parsed names.
collection = {}

# Debug information.
tm1 = time.perf_counter()

with concurrent.futures.ThreadPoolExecutor() as executor:
    # Collection of concurrent tasks.
    futures = []
    personvardi = Personvardi()

    for item in names:
        for name in item["names"]:
            # Search each name concurrently by it's name.
            futures.append(executor.submit(personvardi.search_by_name, name=name))

        for name in item["additional_names"]:
            # Search each name concurrently by it's name.
            futures.append(executor.submit(personvardi.search_by_name, name=name))

    for future in concurrent.futures.as_completed(futures):
        data = future.result()
        # If search of the name returned necessary information,
        # add it to the collection.
        if data:
            collection[data['name'].lower()] = data

# Debug information.
tm2 = time.perf_counter()

# Write output into a json file.
with open('output/personvardi.json', 'w') as fp:
    json.dump(collection, fp, ensure_ascii=False)

# Debug information.
tm3 = time.perf_counter()

print(f'Parse time: {tm2-tm1:0.2f} seconds')
print(f'File write time: {tm3-tm2:0.2f} seconds')
print(f'Total time elapsed: {tm3-tm1:0.2f} seconds')
