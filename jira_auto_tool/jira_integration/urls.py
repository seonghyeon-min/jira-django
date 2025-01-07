from django.urls import path
from . import old_view, api_test_view
from .old_view import IssueVerification
from .views import IssueVerificationTest

urlpatterns = [
    # form-based
    # path('', views.search_issues_form, name='search_issues_form'),
    # path('issue/new/', views.create_issue_form, name='create_issue_form'),
    # path('issue/<str:issue_key>/view/', views.view_issue, name='view_issue'),
    # path('issue/<str:issue_key>/comment/', views.add_comment, name='add_comment'),
    # path('issue/create/', api_test_view.create_issue, name='create_issue'),
    # path('issue/<str:issue_key>/', api_test_view.get_issue, name='get_issue'),
    
    #Rest-Framework
    path('issue/<str:issue_key>/verify/', IssueVerification.as_view(), name='issue_verification'),
    path('issue/<str:issue_key>/verify-test/', IssueVerificationTest.as_view(), name='issue_verification_test'),
]