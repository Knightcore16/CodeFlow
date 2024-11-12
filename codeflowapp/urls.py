from django.urls import path
from . import views

# app_name = 'codeflowapp'


urlpatterns = [
    path('', views.index, name='index'),
    path('leaderboard', views.leaderboard, name='leaderboard'),
    path('resources', views.resources, name='resources'),
    path('courses', views.courses, name='courses'),
    # path('courses/lessons', views.lessons, name='lessons'),
    path('courses/<slug:course_slug>/', views.lessons, name='course_detail'),
    path('quiz/<int:quiz_id>/start/', views.quiz_start, name='quiz_start'),
    path('quiz/attempt/<int:attempt_id>/', views.quiz_question, name='quiz_question'),
    path('login', views.login_user, name='login'),
    path('register', views.register_user, name='register'),
    path('logout', views.logout_user, name='logout'),
]
