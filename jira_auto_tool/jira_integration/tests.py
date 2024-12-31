from django.test import TestCase
# from .services import CountryControllerService

import json, re
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


async def verify_data_with_api(self, data, platform, npv):
    eula_verificaiton_by_country = {}  # {"KR": True or False}
    eulaControllerService = EulaControllerService()
    countryControllerService = CountryControllerService()

    for eula in data:
        cntryLst = self._get_country_list(eula['data']['Country']['value'])
        termsLst = eula['data']['Country']['terms_lst']

        cleaned_cntry_list = countryControllerService.get_country(cntryLst)
        await self._process_countries_for_eula(cleaned_cntry_list, termsLst, eula_verificaiton_by_country, platform, npv, eulaControllerService, countryControllerService)

    return eula_verificaiton_by_country

def _get_country_list(self, country_value):
    cntryLst = country_value.splitlines()

    # If 'Others국가' is present, override with 'Japan'
    if 'Others국가' in cntryLst[0]:
        return ['Japan']
    return cntryLst

async def _process_countries_for_eula(self, cleaned_cntry_list, termsLst, eula_verificaiton_by_country, platform, npv, eulaControllerService, countryControllerService):
    for cntry in cleaned_cntry_list:
        country2Code = countryControllerService.country_mapping.get(cntry, 'Unknown')

        if country2Code == 'Unknown':
            eula_verificaiton_by_country[cntry] = False
            continue

        apiData = await eulaControllerService.getEulaByCountryAndPlatform(platform, country2Code, npv)

        eula_verificaiton_by_country[country2Code] = self._compare_and_sync_eula(termsLst, apiData)

def _compare_and_sync_eula(self, termsLst, apiData):
    return EulaControllerService.compareDataAndSyncStatus(termsLst, apiData)

