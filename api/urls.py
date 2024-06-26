"""
URL configuration for social_network project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import signup, login, search_users, send_friend_request, respond_to_friend_request, list_friends, list_pending_requests

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('search/', search_users, name='search_users'),
    path('send-friend-request/', send_friend_request, name='send_friend_request'),
    path('respond-to-friend-request/', respond_to_friend_request, name='respond_to_friend_request'),
    path('friends/', list_friends, name='list_friends'),
    path('pending-requests/', list_pending_requests, name='list_pending_requests')
]
