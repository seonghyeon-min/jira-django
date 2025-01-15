from datetime import datetime
from typing import List, Dict, Optional, Any
import re
from dataclasses import dataclass
from asgiref.sync import async_to_sync
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.jira.jira_controller import JiraController
from .services.application_manager import ApplicationManager

@dataclass
class AttachmentInfo:
    filename: str
    size: int
    created: str
    mime_type: str
    verification_status: Optional[Dict[str, Any]] = None

class IssueVerificationTest (APIView) :
    SMARTMEDIA_KEYWORKD = 'smartmediaproduct'
    EXCEL_EXTENSION = '.xlsx'
    PLATFORM_PATTERN = r'<td[^>]*id="tplatform"[^>]*>(.*?)</td>'
    NPV_PATTERN = r'<td[^>]*id="(?:tpsw|tnpv)"[^>]*>(.*?)</td>'
    
    def get(self, request) :
        issue_key = request.GET.get('issue_key')
        comment_key = request.GET.get('comment_key')
        
        if not issue_key or not comment_key :
            return self.create_error_response(
                'Missing issue_key, comment_key parameter',
                status.HTTP_400_BAD_REQUEST
            )
            
        return async_to_sync(self._get_async)(request, issue_key, comment_key)
    
    async def _get_async(self, request, issue_key, comment_key) :
        try :
            jira_service = JiraController()
            if not jira_service.connect() :
                return self.create_error_response(
                    'Failed to connect to Jira Service (check your id, pw, api token)',
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            issue = jira_service.get_issue(issue_key)
            
            self.validate_issue_status(issue, jira_service)
            
            attachment_data, verification_result = await self.process_attachments(
                issue, jira_service, comment_key
            )
            
            return self.create_success_response(attachment_data, verification_result)
        
        except Exception as e :
            return self.create_error_response(str(e))
    
    async def process_attachments(self, issue, jira_service, comment_key) :
        attachment_data = []
        verification_result = None
        
        self.validate_issue_requirements(issue, jira_service)
        
        latest_attachment = self.get_latest_attachment_file(issue)
        latest_attachment_info = self.create_attachment_info(latest_attachment)
        
        verification_result = await self._verify_attachment(latest_attachment, issue)
        latest_attachment_info.verification_status = verification_result
        
        self.handle_verification_success(jira_service, verification_result, issue, comment_key)
        
        attachment_data.append(latest_attachment_info)
        
        return attachment_data, verification_result
    
    def validate_issue_status(self, issue, jira_service) -> None :
        issue_status = jira_service.get_jira_status(issue)
        
        # if issue_status.lower() == 'closed' :
        #     raise ValueError(f"Issue status is {issue_status}")
        
    def validate_issue_requirements(self, issue, jira_service) :
        EXPECTED_COMPONENT_NAME = '09. 디바이스약관'

        component_name = jira_service.get_component_name(issue)
        if not component_name or component_name.strip() != EXPECTED_COMPONENT_NAME :
            raise ValueError(f'Invalid component name: {component_name}')
        
        if not hasattr(issue.fields, 'attachment') or not issue.fields.attachment :
            raise ValueError('No attachment found in the issue')
        
    def get_latest_attachment_file(self, issue) :
        valid_attachemnt = [
            (attachment, self.parse_creation_time(attachment.created))
            for attachment in issue.fields.attachment
            if (self.SMARTMEDIA_KEYWORKD in str(getattr(attachment, 'filename', '')).lower() and
                self.is_valid_excel_file(attachment.filename))
        ]
        
        if not valid_attachemnt :
            raise ValueError("No valid attachment found matching criteria") 
        
        return max(
            valid_attachemnt,
            key=lambda x: x[1] or datetime.min
        )[0]
            
    def create_attachment_info(self, attachment) -> AttachmentInfo :
        return AttachmentInfo(
            filename = attachment.filename,
            size=attachment.size,
            created=attachment.created,
            mime_type=attachment.mimeType,
        )
    
    def is_valid_excel_file(self, filename: str) :
        return (
            filename.lower().endswith(self.EXCEL_EXTENSION) and 
            self.SMARTMEDIA_KEYWORKD.lower() in filename.lower()
        )
        
    async def _verify_attachment(self, attachment, issue) :
        platform, npv = self.extract_platform_and_npv(issue.fields.description)
        applicationManager = ApplicationManager(attachment.get())
        return await applicationManager.verify_eula_attachment(platform, npv)
    
    def extract_platform_and_npv(self, description: str) :
        description = description.replace('&quot;', '"').replace('&#x27;', "'")
        description = description.replace('\n', ' ').replace('\r', '')
        
        platform_match = re.search(self.PLATFORM_PATTERN, description)
        npv_match = re.search(self.NPV_PATTERN, description)
        
        if not (platform_match and npv_match) :
            raise ValueError('Failed to extract platform and npv from issue description')
        
        return (
            platform_match.group(1).strip(),
            npv_match.group(1).strip()
        )
    
    def parse_creation_time(self, created_time: str) -> Optional[datetime] :
        try :
            return datetime.fromisoformat(created_time.replace('Z', '+00:00'))

        except (ValueError, AttributeError) :
            return None
    
    # comment 남길 issue를 조정 or rendering 할 수 있는 html 생성
    def handle_verification_success(self, jira_service, verification_result, issue, comment_key) -> None :
        jira_service.leave_comment_result(verification_result, comment_key, issue)
        
    def create_success_response(
        self, 
        attachment_data: List, 
        verification_result: Dict
    ) : 
        return Response(
            {
                'statusCode' : verification_result['checks'][0]['statusCode'],
                'message': verification_result['checks'][0]['detail'],
                'data' : {
                    'has_attachments' : bool(attachment_data),
                    'verification_status': verification_result,
                }
            }, status=verification_result['checks'][0]['statusCode']
        )
        
    def create_error_response(
        self, message: str,
        statusCode : int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ) :
        return Response(
            {
                'statusCode' : statusCode,
                'message' : message,
            }, 
            status=statusCode
        )