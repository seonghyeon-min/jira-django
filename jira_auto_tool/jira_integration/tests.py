from django.test import TestCase
# from .services import CountryControllerService

import json, re, httpx, asyncio
# Create your tests here.

def test_processing() : 
    with open('./jira_auto_tool/eula_data.json', 'r') as f :
        json_obj = json.load(f)

    for eula in json_obj :
        cntryLst = eula['data']['Country']['value'].splitlines()

        if 'Others국가' in cntryLst[0] :
            cntryLst = ['Japan']

        countries = cntryLst[1:] if len(cntryLst) >= 2 else cntryLst

        filter_countries = [
            country.strip() for country in countries if country.strip() and not country.startswith("(") and not country.startswith(")") and not country.startswith("*")
            ]
        filter_countries = filter_countries[0].split(', ') if ', ' in filter_countries[0] else filter_countries

        processed_cntry = [] 
        for country in filter_countries :
            for sub_country in country.split(' / ') :
                processed_cntry.append(sub_country.strip())


        print(processed_cntry)

async def test_verification() :
    async with httpx.AsyncClient() as client :
        response = await client.get(f'http://127.0.0.1:8000/api/v1/issue/SMARTTVIC-33402/verify')
        print(response.json())
        
asyncio.run(test_verification())