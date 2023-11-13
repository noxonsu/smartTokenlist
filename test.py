import json
import os

#load json file
with open('bnb_erc20.json') as f:
    data = json.load(f)

toSave = {}


for i in data:
    i['contract_address'].lower()
    #load summaries if file exists in /summaries/contract_address.json
    if os.path.isfile('summaries/'+i['contract_address']+'.json'):
        with open('summaries/'+i['contract_address']+'.json') as f:
            summary = json.load(f)
            i['summary'] = summary
            toSave[i['contract_address']] = i

#save to json file
with open('bnb_erc20_full.json', 'w') as outfile:
    json.dump(toSave, outfile, indent=4)
