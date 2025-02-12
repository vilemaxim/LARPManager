from django.urls import path
from .views import edit_profile, profile_view

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('orginal_index/', views.orginal_index, name='orginal_index'),
    path('profile/', profile_view, name='profile_view'),
    path('profile/edit/', edit_profile, name='edit_profile'),
]
