from django.urls import path
from .views import upload_csv, history, download_pdf, login_view # Added login_view

urlpatterns = [
    path('login/', login_view, name='login'), # Added this line
    path('upload/', upload_csv, name='upload_csv'),
    path('history/', history, name='history'),
    path('report/<int:pk>/', download_pdf, name='download_pdf'),
]