from django.urls import path
from . import views

# app_name = 'codeflowapp'


urlpatterns = [
    path('', views.index, name='index'),
    path('leaderboard', views.leaderboard, name='leaderboard'),
    path('resources', views.resources_list, name='resources'),
    path('resources/<slug:slug>/', views.resource_detail, name='resource_detail'),
    path('resources/<slug:slug>/download/', views.download_resource, name='download_resource'),
    path('resources/<slug:slug>/rate/', views.rate_resource, name='rate_resource'),
    path('courses', views.courses, name='courses'),
    path('courses/<slug:course_slug>/', views.lessons, name='course_detail'),
    # path('courses/lessons', views.lessons, name='lessons'),
    # path('quiz/<int:quiz_id>/start/', views.quiz_start, name='quiz_start'),
    # path('quiz/attempt/<int:attempt_id>/', views.quiz_question, name='quiz_question'),
    path('login', views.login_user, name='login'),
    path('register', views.register_user, name='register'),
    path('logout', views.logout_user, name='logout'),
]
