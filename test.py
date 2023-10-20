import json
import time

filename = 'bnb_erc20.json'

# Capture the start time
start_time = time.time()

# Load the JSON data from file
with open(filename, 'r') as file:
    data = json.load(file)

# Calculate the duration
duration = time.time() - start_time

print(f"Loading {filename} took {duration:.4f} seconds")
