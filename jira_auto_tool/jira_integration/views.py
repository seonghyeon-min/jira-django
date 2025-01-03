from typing import List, Dict, Optional, Any
import re
from dataclasses import dataclass
from asgiref.sync import async_to_sync, sync_to_async
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import JiraService

@dataclass
class AttachmentInfo:
    filename: str
    size: int
    mime_type: str
    verification_status: Optional[Dict[str, Any]] = None

class IssueVerification (APIView) :
    SMARTMEDIA_KEYWORKD = 'smartmediaproduct'
    EXCEL_EXTENSION = '.xlsx'
    PLATFORM_PATTERN = r'<td id="tplatform"[^>]*>(.*?)</td>'
    NPV_PATTERN = r'<td id="(?:tnpv|tpsw)"[^>]*>(.*?)</td>'
    
    def get(self, request, issue_key) :
        return async_to_sync(self._get_async)(request, issue_key)
    
    async def _get_async(self, request, issue_key) :
        try :
            jira_service = JiraService()
            if not jira_service.connect() :
                return self.create_error_response(
                    'Failed to connect to Jira Service (check your id, pw, api token)',
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            issue = jira_service.get_issue(issue_key)
            attachment_data, verification_result = await self.process_attachments(
                issue, jira_service
            )
            
            return self.create_success_response(attachment_data, verification_result)
        
        except Exception as e :
            return self.create_error_response(str(e))
    
    async def process_attachments(self, issue, jira_service) :
        attachment_data = []
        verification_result = None
        
        if not hasattr(issue.fields, 'attachment') or not issue.fields.attachment :
            return attachment_data, verification_result
        
        for attachment in issue.fields.attachment :
            if self.SMARTMEDIA_KEYWORKD not in str(getattr(attachment, 'filename', '')).lower() :
                continue
            
            attachment_info = self.create_attachment_info(attachment)
            
            if self.is_valid_excel_file(attachment_info.filename) :
                verification_result = await self._verify_attachment(
                    attachment, issue, jira_service
                )
                attachment_info.verification_status = verification_result
                
                if verification_result['checks'][0]['statusCode'] :
                    await self.handle_verification_success(
                        jira_service, verification_result
                    )
                    
            attachment_data.append(attachment_info)
        
        return attachment_data, verification_result
            
    def create_attachment_info(self, attachment) -> AttachmentInfo :
        return AttachmentInfo(
            filename = attachment.filename,
            size=attachment.size,
            mime_type=attachment.mimeType
        )
    
    def is_valid_excel_file(self, filename: str) :
        return (
            filename.lower().endswith(self.EXCEL_EXTENSION) and 
            self.SMARTMEDIA_KEYWORKD.lower() in filename.lower()
        )
        
    async def _verify_attachment(self, attachment, issue, jira_service) :
        platform, npv = self.extract_platform_and_npv(issue.fields.description)
        return await jira_service.verify_attachment(attachment, platform, npv)
    
    def extract_platform_and_npv(self, description: str) :
        platform_match = re.search(self.PLATFORM_PATTERN, description)
        npv_match = re.search(self.NPV_PATTERN, description)
        
        print(platform_match, npv_match)
        if not (platform_match and npv_match) :
            raise ValueError('Failed to extract platform and npv from issue description')
        
        return (
            platform_match.group(1).strip(),
            npv_match.group(1).strip()
        )
    
    async def handle_verification_success(self, jira_service, verification_result) -> None :
        jira_service.leave_comment_result(verification_result, 'ITPLAT-1142')
        
    def create_success_response(
        self, 
        attachment_data: List, 
        verification_result: Dict
    ) : 
        return Response(
            {
                'statusCode' : status.HTTP_200_OK if bool(attachment_data) else status.HTTP_204_NO_CONTENT,
                'message': 'Verification completed' if bool(attachment_data) else 'No Content',
                'data' : {
                    'has_attachments' : bool(attachment_data),
                    'verification_status': verification_result,
                }
            }, status=status.HTTP_200_OK if bool(attachment_data) else status.HTTP_204_NO_CONTENT
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