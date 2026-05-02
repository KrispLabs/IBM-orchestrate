from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_tests_view, name='generate-tests'),
    path('update/', views.update_tests_view, name='update-tests'),
]

# Made with Bob
