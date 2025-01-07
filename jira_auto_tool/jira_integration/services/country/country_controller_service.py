from .country_config import CountryConfig

class CountryControllerService :
    def __init__(self) -> None:
        self.country_config = CountryConfig()
        
    def get_country_2_code(self, country) :
        return self.country_config.get_country_mapping().get(country, 'Unknown')
        
    def get_country(self, country_value) :
        countries_lst = self.process_country_lst(country_value)
        countries = countries_lst[1:] if len(countries_lst) >= 2 else countries_lst

        filter_countries = [
            country.strip() for country in countries if country.strip() and not country.startswith("(") and not country.startswith(")") and not country.startswith("*")
        ]

        filter_countries = filter_countries[0].split(', ') if ', ' in filter_countries[0] else filter_countries

        processed_cntry = []
        for country in filter_countries :
            for sub_country in country.split(' / ') :
                processed_cntry.append(sub_country.strip())

        return processed_cntry
        
    
    def process_country_lst(self, country_value) :
        countries = country_value.splitlines()
        
        if 'Others국가' in countries[0] :
            return ['Japan']
        return countries
