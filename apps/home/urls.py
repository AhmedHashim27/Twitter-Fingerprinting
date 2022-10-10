# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [
    path('output/', views.index, name='home'),
    path('', views.input, name='home'),
    path('analyze/', views.analyze, name='home'),
    path('track/<str:account>/', views.track, name='home'),
]
