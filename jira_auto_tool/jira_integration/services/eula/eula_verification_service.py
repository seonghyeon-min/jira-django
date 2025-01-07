from http import HTTPStatus
from .eula_controller_service import EulaControllerService
from ..country.country_controller_service import CountryControllerService

class EulaVerificationService :
    def __init__(self) :
        self.eula_service = EulaControllerService()
        self.country_service = CountryControllerService()
        
    async def verify_data_with_api(self, 
                                    data: list, 
                                    platform: str,
                                    npv: str) -> dict :
        
        if not await self._check_server_status() :
            return self._create_error_response(
                HTTPStatus.SERVICE_UNAVAILABLE,
                "Eula-Server-connection-failed"
            )
            
        try :
            return await self._process_eula_data(data, platform, npv)
        
        except Exception as e :
            return self._create_error_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                f"Error processing Eula-data : {str(e)}"
            )
        
    async def _check_server_status(self) -> bool :
        server_status = await self.eula_service.eula_server_test_connection()
        return server_status['detail'].get('server_reachable', False)
    
    def _create_error_response(self,
                                statusCode : int,
                                message: str) :
        return {
            "statusCode" : statusCode,
            "detail" : message
        }
        
    async def _process_eula_data(self,
                                data: dict,
                                platform: str,
                                npv: str) -> dict :
        verfication_result = {}
        
        for eula in data :
            country_results = await self._process_country_data(
                eula['data']['Country'],
                platform,
                npv
            )
            verfication_result.update(country_results)
            
        if isinstance(verfication_result, dict) and any(isinstance(v, bool) for v in verfication_result.values()):
            response = {
                "statusCode": HTTPStatus.OK,
                "detail": "Eula-verification-successful",
                "verification_results": verfication_result
            }

        return response
        # return verfication_result
    
    
    async def _process_country_data(self, country_data: dict, platform: str, npv: str) -> dict:
        country_results = {}
        terms_lst = country_data['terms_lst']
        countries = self.country_service.get_country(country_data['value'])
        
        for country in countries :
            result = await self._verify_country_eula(
                country,
                terms_lst,
                platform, 
                npv
            )
            country_results.update(result)
            
        return country_results
    
    async def _verify_country_eula(self,
                                country: str,
                                terms_lst: list,
                                platform: str,
                                npv: str) -> dict :
        country2Code = self.country_service.get_country_2_code(country)
        country_key = 'global' if country2Code == 'JP' else country
        
        if country2Code == 'Unknown' :
            return {country_key : False}
        
        try :
            responseBody = await self.eula_service.get_eula_by_country_and_platform(
                platform, country2Code, npv
            )
            
            if responseBody.get('statusCode') == 404 : 
                return {country_key : False}
            
            is_verified = self.eula_service.compare_term_data_sync_status(
                terms_lst,
                responseBody
            )
            
            return {country_key : is_verified}
        
        except Exception as e :
            return {country_key: False}