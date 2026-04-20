from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('trade/', views.place_trade, name='place_trade'),
    path('wallet/', views.wallet_view, name='wallet'),
    path('history/', views.history_view, name='history'),
    path('account/', views.account_view, name='account'),
    path('agency/', views.agency_view, name='agency'),
    path('subordinate/', views.subordinate_data_view, name='subordinate_data'),
    path('commission/', views.commission_detail_view, name='commission_detail'),
    path('invitation/', views.invitation_rules_view, name='invitation_rules'),
    path('withdraw-history/', views.withdraw_history_view, name='withdraw_history'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
