from django.test import TestCase
# from .services import CountryControllerService

import json, re
# Create your tests here.

# print(os.getcwd())
with open('./jira_auto_tool/eula_data.json', 'r') as f :
    json_obj = json.load(f)

for eula in json_obj :
    cntryLst = eula['data']['Country']['value'].splitlines()
    countries = cntryLst[1:] if len(cntryLst) >= 2 else cntryLst

    filter_countries = [
        country.strip() for country in countries if country.strip() and not country.startswith("(") and not country.startswith(")") and not country.startswith("*")
        ]
    
    processed_cntry = [] 
    for country in filter_countries :
        for sub_country in country.split(' / ') :
            processed_cntry.append(sub_country.strip())
    
    print(processed_cntry)
