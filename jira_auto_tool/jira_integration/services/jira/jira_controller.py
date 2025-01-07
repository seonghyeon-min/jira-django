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
        
    
    def leave_comment_result(self, verify_data, issue_key) :
        if not self.jira_client :
            self.connect()
        
        try :
            responseBody = verify_data['checks'][0]
            comment = "Verification Results:\n"
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
                
            self.jira_client.add_comment(issue_key, comment)
        
        except Exception as e:
            self.jira_client.add_comment(issue_key, f"Error Leaving comment : {str(e)}")