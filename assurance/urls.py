
from django.contrib import admin
from django.urls import path
from  . import views

urlpatterns = [
    path('<str:reference>/', views.load_assurance, name='load_assurance'),
    path('<str:reference>/send', views.send_assurance, name='send_assurance'),
]
