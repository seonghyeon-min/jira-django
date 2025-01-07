from http import HTTPStatus
from typing import Dict, Optional
import httpx
import logging

logger = logging.getLogger(__name__)

class EulaResponseHandler:
    """Handle EULA API responses and status codes"""
    
    @staticmethod
    def create_response(status_code: int, message: str = None, data: Optional[Dict] = None) -> Dict:
        """Create standardized response format"""
        response = {
            'statusCode': status_code,
            'response': {
                'statusCode': status_code,
                'messages': message or EulaResponseHandler._get_default_message(status_code)
            }
        }
        
        if data:
            response['response'].update(data)
        
        if status_code != HTTPStatus.OK:
            logger.error(f"Error response: {status_code} - {message}")
        else:
            logger.info(f"Success response: {status_code}")
            
        return response

    @staticmethod
    def _get_default_message(status_code: int) -> str:
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
        return status_messages.get(status_code, f"Unexpected status code: {status_code}")

class EulaControllerService:
    def __init__(self, base_url: str = "http://10.159.73.19:8888/api/v1/terms/terms_group"):
        self.base_url = base_url
        self.response_handler = EulaResponseHandler()

    async def get_eula_by_country_and_platform(self, platform: str, country: str, npv: str) -> Dict:
        """
        Get EULA data by country and platform
        
        Args:
            platform: Platform identifier
            country: Country code
            npv: NPV version
        
        Returns:
            Dict: EULA data or error response
        """
        async with httpx.AsyncClient() as client:
            try:
                return await self._make_eula_request(client, platform, country, npv)
            except Exception as e:
                return await self._handle_request_exception(e)

    async def _make_eula_request(self, client: httpx.AsyncClient, platform: str, country: str, npv: str) -> Dict:
        """Make EULA API request and handle response"""
        try:
            response = await client.get(
                self.base_url,
                params=self._get_request_params(platform, country, npv),
                timeout=10.0
            )
            return self._handle_response(response, platform, country, npv)
        except httpx.TimeoutException as e:
            return self._handle_timeout_error(e)

    def _get_request_params(self, platform: str, country: str, npv: str) -> Dict:
        """Get request parameters"""
        return {
            "platform": platform,
            "country": country,
            "npv": npv
        }

    def _handle_response(self, response: httpx.Response, platform: str, country: str, npv: str) -> Dict:
        """Handle API response"""
        if response.status_code == HTTPStatus.OK:
            return self.response_handler.create_response(
                status_code=HTTPStatus.OK,
                data=response.json()
            )
        
        if response.status_code == HTTPStatus.NOT_FOUND:
            return self.response_handler.create_response(
                status_code=HTTPStatus.NOT_FOUND,
                message=f"EULA not found for platform: {platform}, country: {country}, npv: {npv}"
            )
        
        return self.response_handler.create_response(
            status_code=response.status_code,
            message=f"API error: {response.text}"
        )

    def _handle_timeout_error(self, error: httpx.TimeoutException) -> Dict:
        """Handle timeout errors"""
        return self.response_handler.create_response(
            status_code=HTTPStatus.GATEWAY_TIMEOUT,
            message=f"Request timeout: {str(error)}"
        )

    async def _handle_request_exception(self, error: Exception) -> Dict:
        """Handle various request exceptions"""
        if isinstance(error, httpx.ConnectError):
            return self.response_handler.create_response(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                message="Unable to connect to EULA server"
            )
        
        if isinstance(error, httpx.RequestError):
            return self.response_handler.create_response(
                status_code=HTTPStatus.BAD_GATEWAY,
                message=f"Request error: {str(error)}"
            )
        
        return self.response_handler.create_response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=f"Internal server error: {str(error)}"
        )
