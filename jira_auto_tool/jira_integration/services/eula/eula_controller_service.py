from http import HTTPStatus
from typing import Dict, Optional
from .eula_config import EulaConfig
import httpx

class EulaResponseHandler :
    @staticmethod
    def create_response(statusCode: int, returnValue: Optional[Dict] = None) -> Dict :
        response = {
            'statusCode': statusCode,
            'returnValue' : returnValue or EulaResponseHandler._get_default_message(statusCode)
        }
        return response
        
    @staticmethod
    def _get_default_message(statusCode: int) -> str:
        """Get default message for HTTP status code"""
        status_messages = {
            HTTPStatus.OK: "Success",
            HTTPStatus.BAD_REQUEST: "Invalid request parameters",
            HTTPStatus.UNAUTHORIZED: "Unauthorized access",
            HTTPStatus.FORBIDDEN: "Access forbidden",
            HTTPStatus.NOT_FOUND: "Resource not found",
            HTTPStatus.INTERNAL_SERVER_ERROR: "Internal server error",
            HTTPStatus.BAD_GATEWAY: "Bad gateway",
            HTTPStatus.SERVICE_UNAVAILABLE: "Service unavailable",
            HTTPStatus.GATEWAY_TIMEOUT: "Gateway timeout"
        }
        return status_messages.get(statusCode, f"Unexpected status code: {statusCode}")

class EulaControllerService :
    def __init__(self) :
        self.baseUrl = "http://10.159.73.19:8888/api/v1/terms/terms_group"
        self.response_handler = EulaResponseHandler()
        
    async def eula_server_test_connection(self) -> dict :
        results = {
            'status': False,
            'detail': {
                'server_reachable' : False
            }
        }

        try :
            async with httpx.AsyncClient() as client :
                try :
                    response = await client.get(self.baseUrl, timeout=10.0)
                    results['status'] = str(response.status_code)[0] in ['2', '3', '4'] #2xx, 3xx, 4xx
                    results['detail']['server_reachable'] = results['status']
                
                except httpx.ConnectError as e:
                    return results
                
                except httpx.RequestError as e:
                    return results
        
        except Exception as e:
            pass
                    
        finally :
            return results
    
    async def get_eula_by_country_and_platform(self,
                                                platform: str,
                                                country: str,
                                                npv: str) -> dict :        
        async with httpx.AsyncClient() as client :
            try :
                return await self._make_eula_request(client, platform, country, npv)
            except Exception as e:
                return await self._handle_request_exception(e)
            
    async def _make_eula_request(self, client: httpx.AsyncClient, platform: str, country: str, npv: str) -> Dict :
        try:
            response = await client.get(
                self.baseUrl,
                params=self._get_request_params(platform, country, npv),
                timeout=10.0
            )   
            return self._handle_response(response, platform, country, npv)
        
        except httpx.TimeoutException as e:
            return self._handle_timeout_error(e)
        
    def _get_request_params(self, platform: str, country: str, npv: str) -> Dict :
        return {
            'platform': platform,
            'country': country,
            'npv': npv
        }
    
    def _handle_response(self, response: httpx.Response, platform: str, country: str, npv: str) -> Dict :
        if response.status_code == HTTPStatus.OK :
            return self.response_handler.create_response(
                statusCode = HTTPStatus.OK,
                returnValue = response.json()
            )
            
        if response.status_code == HTTPStatus.NOT_FOUND :
            return self.response_handler.create_response(
                statusCode = HTTPStatus.NOT_FOUND,
                returnValue = {
                    "message": f"Terms group not found for platform: {platform}, country: {country}, npv: {npv}"
                }
            )
            
        return self.response_handler.create_response(
            statusCode =  response.status_code,
            returnValue = {
                "message" : f"API Error : {response.text}"
            }
        )
        
    def _handle_timeout_error(self, error: httpx.TimeoutException) -> Dict :
        return self.response_handler.create_response(
            statusCode = HTTPStatus.REQUEST_TIMEOUT,
            returnValue = {
                "message" : f"Request timed out : {str(error)}"
            }
        )
        
    async def _handle_request_exception(self, error: Exception) -> Dict :
        if isinstance(error, httpx.ConnectError) :
            return self.response_handler.create_response(
                statusCode = HTTPStatus.SERVICE_UNAVAILABLE,
                returnValue = {
                    "message" : f"Service Unavailable : {str(error)}"
                }
            )
            
        if isinstance(error, httpx.RequestError) :
            return self.response_handler.create_response(
                statusCode = HTTPStatus.BAD_GATEWAY,
                returnValue = {
                    "message" : f"Request Error : {str(error)}"
                }
            )
        
        return self.response_handler.create_response(
            statusCode = HTTPStatus.INTERNAL_SERVER_ERROR,
            returnValue = {
                "message" : f"Internal Server Error : {str(error)}"
            }
        )
        
    def compare_term_data_sync_status(self, loaclBody: list, responseBody: dict) -> Dict :
        eula_config = EulaConfig()
        terms_mapping = eula_config.get_terms_mapping()
        
        sync_tp = dict()
        sync_tp_result = dict()
        
        for data in loaclBody :
            terms_name = list(data.keys())[0].strip()
            terms_code = data[list(data.keys())[0]]['tp_code']
            terms_name = terms_mapping.get(terms_name)
            
            if terms_code != [] :
                sync_tp[terms_name] = terms_code
                
        if 'error' in responseBody and responseBody['error'] :
            pass
        
        try :    
            if responseBody['statusCode'] == 200 :
                for tn, tc in sync_tp.items() :
                    if tn in responseBody['response']['terms_lst'].keys() :
                        tpLst = [d['terms_mgt_tp_code'] for d in responseBody['response']['terms_lst'][tn]]
                        sync_tp_result[tn] = set(tpLst) == set(tc)
        
        except KeyError as e :
            pass
        
        if all(sync_tp_result.values()) :
            return True
        else :
            return False