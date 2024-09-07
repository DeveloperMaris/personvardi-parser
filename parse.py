from Personvardi import Personvardi
from collections import OrderedDict
import concurrent.futures
import json
import time
import argparse
import os
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Timing decorator to measure function execution time
def timing(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        logging.debug(f'Starting {func.__name__}')
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            logging.error(f'Error in {func.__name__}: {e}')
            raise
        end_time = time.perf_counter()
        logging.debug(f'{func.__name__} took {end_time - start_time:0.2f} seconds')
        return result
    return wrapper

# Set up argument parsing
parser = argparse.ArgumentParser(description='Process some JSON data.')
parser.add_argument('input_file', type=str, help='Path to the input JSON file')
args = parser.parse_args()

# Validate input file path
if not os.path.isfile(args.input_file):
    logging.error(f'The file {args.input_file} does not exist.')
    raise FileNotFoundError(f'The file {args.input_file} does not exist.')

# Function to load JSON data
@timing
def load_json(file_path):
    logging.debug(f'Loading JSON file from {file_path}')
    with open(file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        logging.debug(f'Loaded {len(data)} items from JSON file')
        return data

# Function to save JSON data
@timing
def save_json(file_path, data):
    logging.debug(f'Saving JSON data to {file_path}')
    with open(file_path, 'w', encoding='utf-8') as fp:
        json.dump(data, fp, ensure_ascii=False, indent=4)
    logging.debug('Data successfully saved')

# Start timing
tm1 = time.perf_counter()

# Load names from the input JSON file
names = load_json(args.input_file)

# Collection of parsed names
collection = {}

# Process names using concurrent futures
@timing
def process_names(names):
    logging.debug('Starting name processing')
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create a list of tasks
        futures = [
            executor.submit(Personvardi().search_by_name, name=name)
            for item in names
            for name in item["names"] + item["additional_names"]
        ]
        
        # Collect results
        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
                if data:
                    collection[data['name'].lower()] = data
                    logging.debug(f'Collected data for name: {data["name"]}')
            except Exception as e:
                logging.error(f'Error retrieving result from future: {e}')

process_names(names)

# Order the collection by keys
logging.debug('Sorting the collection by keys')
sorted_collection = OrderedDict(sorted(collection.items()))

# Save sorted collection to JSON
save_json('output/personvardi.json', sorted_collection)

# Print total elapsed time
tm2 = time.perf_counter()
print(f'Total time elapsed: {tm2 - tm1:0.2f} seconds')
