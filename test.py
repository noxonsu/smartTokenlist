import json

input_file = "eth_erc20.json"
output_file = "eth_erc20_withp8skip.json"

with open(input_file, "r") as f:
    data = json.load(f)

for item in data:
    if item["contract_address"] == "0x0cd5cda0e120f7e22516f074284e5416949882c2":
        break
    item["p8skip"] = True

with open(output_file, "w") as f:
    json.dump(data, f, indent=4)
