from http import HTTPStatus
from .data.data_controller import ExcelManipulateService
from .eula.eula_verification_service import EulaVerificationService

class ApplicationManager:
    def __init__(self, content) :
        self.excelManipulateService = ExcelManipulateService(content)
        self.eulaVerificationService = EulaVerificationService()
        self.verification_result = {
            'status' : None,
            'checks' : []
        }    
        
    async def verify_eula_attachment(self, *description) :
        try :
            platform, npv = description[0], description[1]

            self.excelManipulateService.build_basic_data_structure()
            eula_structure_data = self.excelManipulateService.get_data()
            
            response_verify = await self.eulaVerificationService.verify_data_with_api(eula_structure_data, platform, npv)
            
            self.verification_result['status'] = 'verified' if response_verify['statusCode'] == HTTPStatus.OK else 'non-verified'
            self.verification_result['checks'].append(response_verify)
            
            return self.verification_result
        
        except Exception as e :
            return {
                'status' : 'error',
                'checks' : str(e)
            }