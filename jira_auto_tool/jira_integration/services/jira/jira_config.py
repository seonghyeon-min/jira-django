import os
from jira import JIRA, JIRAError
from dotenv import load_dotenv

class JiraConfig :
    def __init__(self) :
        load_dotenv(verbose=True)
        
        self.domain = os.getenv("JIRA_SERVER")
        self.username = os.getenv("JIRA_USERNAME")
        self.api_token = os.getenv("JIRA_API_TOKEN")
        self.headers = {
            "Accept" : "application/json",
            "Content-Type" : "application/json"
        }

    def get_domain(self) :
        return self.domain
    
    def get_username(self) :
        return self.username
    
    def get_api_token(self) :
        return self.api_token
    
    def get_headers(self) :
        return self.headers
    
    