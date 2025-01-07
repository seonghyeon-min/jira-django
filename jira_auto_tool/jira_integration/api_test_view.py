from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages

import json
from .service import JiraService

@csrf_exempt
@require_http_methods(["POST"])
def create_issue(request):
    try:
        data = json.loads(request.body)
        project_key = data.get('project_key')
        summary = data.get('summary')
        description = data.get('description')
        issue_type = data.get('issue_type', 'Story') # default is Stroy;
        
        if not all([project_key, summary, description]) :
            return JsonResponse({
                'error' : 'Missing required fields'
            }, status=400)
            
        jira_service = JiraService()
        if jira_service.connect() :
            issue = jira_service.create_issue(project_key, summary, description, issue_type)
        
        return JsonResponse({
            'key': issue.key,
            'summary' : issue.fields.summary,
            'description' : issue.fields.description,
            'status' : issue.fields.status.name,
            'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None
        })

    except Exception as e :
        return JsonResponse({'error' : str(e)}, status=500)
    
@require_http_methods(["GET"]) 
def get_issue(request, issue_key):
    try :
        jira_service = JiraService()
        if jira_service.connect() :
            issue = jira_service.get_issue(issue_key)
        
        return JsonResponse({
            'key': issue.key,
            'summary' : issue.fields.summary,
            'description' : issue.fields.description,
            'status' : issue.fields.status.name,
            'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None
        })
    
    except Exception as e :
        return JsonResponse({'error' : str(e)}, status=500)
    
    