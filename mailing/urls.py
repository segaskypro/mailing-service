from django.urls import path
from . import views

app_name = 'mailing'

urlpatterns = [
    path('', views.index, name='index'),
    path('mailings/', views.mailing_list, name='mailing_list'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]