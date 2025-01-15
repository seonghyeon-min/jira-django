from jira import JIRA, JIRAError
from .jira_config import JiraConfig

class JiraController :
    def __init__(self) :
        self.jira_config = JiraConfig()
        
    def connect(self) :
        try :
            self.jira_client = JIRA(
                server = self.jira_config.get_domain(),
                token_auth = self.jira_config.get_api_token()        
            )
            
            return True
        
        except JIRAError as e :
            pass
        
    def get_issue(self, issue_key) :
        if not self.jira_client :
            self.connect()
        
        try :
            issue = self.jira_client.issue(issue_key)
            
            if hasattr(issue, 'raw') and 'fields' in issue.raw :
                return issue
            
        except Exception as e :
            raise ValueError(str(e))
    
    def get_jira_status(self, issue) :
        try :
            if hasattr(issue.fields, 'status') and issue.fields.status :
                return issue.fields.status.name
            
        except Exception as e: 
            raise ValueError(str(e))

    def get_attachment_detail(self, issue) :
        attachment_info = []
    
        try:
            if hasattr(issue.fields, 'attachment') and issue.fields.attachment:
                for attachment in issue.fields.attachment:
                    attachment_data = {
                        'id': attachment.id,
                        'filename': attachment.filename,
                        'size': attachment.size,  # Size in bytes
                        'created': attachment.created,
                        'createdType': type(attachment.created),# Creation timestamp
                        'mime_type': attachment.mimeType,
                        'content': attachment.content,  # URL to download the attachment
                    }
                    attachment_info.append(attachment_data)
                    
            return attachment_info
                    
        except AttributeError as e:
            raise ValueError(f"Error processing attachments: {str(e)}")
        
    def get_component_name(self, issue) :
        components = self.get_issue_components(issue) 
        return components[0]['name'] if components else None
        
    def get_issue_components(self, issue) :
        if not hasattr(issue.fields, 'components') or not issue.fields.components :
            raise ValueError("No components found in the issue.")
        
        components = [
            {
                'name' : component.name,
                'id' : component.id
            }
            for component in issue.fields.components
        ]
        
        return components
    
    # leave_key regulation ?
    def leave_comment_result(self, verify_data, leave_key, issue_key) :
        if not self.jira_client :
            self.connect()
        
        try :
            responseBody = verify_data['checks'][0]
            comment = "Verification Results:\n"
            comment += f"Issue-key : {issue_key}\n"
            comment += f"Status: {verify_data['status']}\n\n"

            if isinstance(responseBody, dict) and responseBody['statusCode'] != 200 :
                comment += f"❌ Error Message: {responseBody['detail']}\n\n"
            
            else :
                passed_countries = []
                failed_countries = []
                country_results = responseBody['verification_results']
                
                for country, result in country_results.items() :
                    if result : 
                        passed_countries.append(country)
                    else :
                        failed_countries.append(country)

                comment += "✅ Passed Countries:\n"
                if passed_countries :
                    for country in sorted(passed_countries) :
                        comment += f"- {country}\n"
                else :
                    comment += "None\n"
                
                comment += "\n❌ Failed Countries:\n"
                if failed_countries: 
                    for country in sorted(failed_countries) :
                        comment += f"- {country}\n"
                else :
                    comment += "None\n"
                
            self.jira_client.add_comment(leave_key, comment)
        
        except Exception as e:
            self.jira_client.add_comment(leave_key, f"Error Leaving comment : {str(e)}")