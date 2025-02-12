from django.urls import path
from . import views

app_name = "events" 
urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('<int:event_id>/', views.event_detail, name='event_detail'),
    path('<int:event_id>/register/', views.register_event, name='register_event'),
    path('<int:event_id>/start-checkin/', views.start_checkin, name='start_checkin'),
    path('approvals/', views.event_approval_list, name='event_approval_list'),
    path('approvals/<int:registration_id>/', views.event_approval_view, name='event_approval_view'),
    path('<int:event_id>/check-in/', views.check_in, name='check_in'),
]
