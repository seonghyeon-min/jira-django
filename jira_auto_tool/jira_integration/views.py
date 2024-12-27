import re
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages

import json
from .services import JiraService

async def view_issue(request, issue_key) :
    try :
        jira_service = JiraService()
        if jira_service.connect() :
            issue = jira_service.get_issue(issue_key)            
            
            attachment_data = []
            
            if hasattr(issue.fields, 'attachment') and issue.fields.attachment :
                for attachment in issue.fields.attachment :
                    if 'smartmediaproduct' in str(getattr(attachment, 'filename', '')).lower() :
                        attachment_info = {
                            'filename' : attachment.filename,
                            'size': attachment.size,
                            'mime_type': attachment.mimeType,
                            'verification_status' : None,
                        }
                    
                        if (str(attachment_info['filename']).lower().endswith('.xlsx')) and \
                            'smartmediaproduct'.lower() in str(attachment_info['filename']).lower() :
                            try :
                                platform_match = re.search(r'<td id="tplatform"[^>]*>(.*?)</td>', issue.fields.description)
                                npv_match = re.search(r'<td id="tnpv"[^>]*>(.*?)</td>', issue.fields.description)
                                if platform_match and npv_match :
                                    platform = platform_match.group(1).strip()
                                    npv = npv_match.group(1).strip()
                                
                                verification_result = await jira_service.verify_attachment(attachment, platform, npv)
                                attachment_info['verification_status'] = verification_result
                                
                            except Exception as verify_error :
                                attachment_info['verification_status'] = {
                                    'status' : 'error',
                                    'messages' : str(verify_error)
                                }
                                
                        attachment_data.append(attachment_info)
        
            context = {
                'issue' : issue,
                'has_attachments' : bool(attachment_data),
                'attachment_data' : attachment_data,
            }
                        
            return render(request, 'jira_integration/view_issue.html', context)
        
        else:
            messages.error(request, 'Failed to connect to Jira.')
            return render(request, 'jira_integration/view_issue.html', {'issue': None})
        
    except Exception as e:
        messages.error(request, f'Error fetching issue: {str(e)}')
        return render(request, 'jira_integration/view_issue.html', {'issue': None})
    
