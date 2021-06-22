from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    path('templates/', views.index_template, name='index_template'),
    path('upload', views.upload, name='upload'),
    path('csv_export/', views.csv_export, name='csv_export'),
    path('upload_complete/', views.upload_complete, name='upload_complete'),
]
