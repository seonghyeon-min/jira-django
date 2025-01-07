class CountryConfig :
    def __init__(self) :
        self.country_mapping = {
            # GDPR Countries (18개국)
            'Bulgaria': 'BG',
            'Croatia': 'HR',
            'Cyprus': 'CY',
            'Czech': 'CZ',
            'Estonia': 'EE',
            'Greece': 'GR',
            'Hungary': 'HU',
            'Iceland': 'IS',
            'Latvia': 'LV',
            'Liechtenstein': 'LI',
            'Lithuania': 'LT',
            'Luxemburg': 'LU',
            'Malta': 'MT',
            'Romania': 'RO',
            'Slovakia': 'SK',
            'Slovenia': 'SI',
            'Poland': 'PL',
            'Belgium': 'BE',

            "Switzerland": "CH",
            "Austria": "AT",
            "Finland": "FI",
            "Ireland": "IE",
            "Portugal": "PT",
            "Netherlands": "NL",
            "Sweden": "SE",
            "Denmark": "DK",
            "Norway": "NO",
            
            # GDPR 1개국 (UK)
            'United Kingdom': 'GB',
            'UK': 'GB',
            '영국': 'GB',

            "France": "FR",
            "Spain": "ES",
            "Italy": "IT",
            "Germany": "DE",
            
            "중국" : "CN", # wasu? 

            # Global 12개국
            'United States': 'US',
            'USA': 'US',
            'China': 'CN',

            '뉴질랜드' : 'NZ',
            'New Zealand': 'NZ',
            'Thailand': 'TH',
            'Brazil': 'BR',
            '브라질' : 'BR',
            'Canada': 'CA',
            '캐나다' : 'CA',
            '멕시코' : 'MX',
            'Mexico': 'MX',
            '호주' : 'AU',
            'Australia': 'AU',
            '칠레' : 'CL',
            'Chile': 'CL',
            '아르헨티나' : 'AR',
            'Argentina': 'AR',
            '콜롬비아': 'CO',
            'Colombia': 'CO',
            '페루' : 'PE',
            'Peru': 'PE',
            '인도' : 'IN',
            'India': 'IN',

            # Korea
            'Korea': 'KR',
            '한국': 'KR',
            'South Korea': 'KR',
            
            '태국' : 'TH',
            'Thailand' : 'TH',
            'Kosovo' : 'XK',
            
            # representive Others global
            'Japan' : 'JP'
            }
        
    def get_country_mapping(self) :
        return self.country_mapping