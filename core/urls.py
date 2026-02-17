from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),              # Главная страница
    path('login/', views.user_login, name='login'),   # Страница входа
    path('logout/', views.user_logout, name='logout'), # Выход
    path('quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('lecture/<int:lecture_id>/', views.lecture_detail, name='lecture_detail'),
    path('my-results/', views.student_results, name='student_results'),

    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    

    path('teacher/lecture/create/', views.create_lecture, name='create_lecture'),
    
    path('teacher/quiz/create/', views.create_quiz, name='create_quiz'),
    path('teacher/quiz/<int:quiz_id>/manage/', views.manage_quiz, name='manage_quiz'),
    path('teacher/quiz/<int:quiz_id>/add-question/', views.add_question, name='add_question'),
    
    path('teacher/grading/', views.grading_list, name='grading_list'),
    path('teacher/grading/<int:submission_id>/', views.grade_submission, name='grade_submission'),
]