from django.urls import path
from . import views

app_name = 'characters'

urlpatterns = [
	path('create/', views.create_or_edit_character_view, name='create_character'),
    path('my-characters/', views.character_list_view, name='character_list'),
	path('<int:character_id>/edit/', views.create_or_edit_character_view, name="edit_character"),
	
	path('get_common_skills/', views.get_common_skills, name='get_common_skills'),
	path('get_race_skills/', views.get_race_skills, name='get_race_skills'),
	path('get_race_starting_affinity/', views.get_race_starting_affinity, name='get_race_starting_affinity'),
    path('get_event_details/', views.get_event_details, name='get_event_details'),
	path('get_affinity_skills/', views.get_affinity_skills, name='get_affinity_skills'),
	path('add_skill/', views.add_skill, name='add_skill'),
    #Marshel Area
	path('approve/', views.character_approval_list, name='approval_list'),
	path('approve/<int:character_id>/', views.character_approval_view, name='approval_view'),
	path('<int:character_id>/print/', views.generate_character_sheet, name='print_character_sheet'),
]
