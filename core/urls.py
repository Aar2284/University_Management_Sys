from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    
    path('', views.login_view, name='login'), 
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_user, name='logout'),
    
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('take-attendance/', views.take_attendance, name='take_attendance'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('manage-grades/', views.manage_grades, name='manage_grades'),
    path('create-assignment/', views.create_assignment, name='create_assignment'),
    path('student-submissions/', views.teacher_submissions, name='teacher_submissions'),
    path('class-results/', views.teacher_results, name='teacher_results'),

    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('my-attendance/', views.student_attendance, name='student_attendance'),
    path('my-assignments/', views.student_assignments, name='student_assignments'),
    path('submission-success/<int:submission_id>/', views.submission_success, name='submission_success'),

    path('submit-work/<int:assignment_id>/', views.submit_work, name='submit_work'),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="pass_reset/password_reset.html"), name="password_reset"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="pass_reset/password_reset_done.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="pass_reset/password_reset_confirm.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="pass_reset/password_reset_complete.html"), name="password_reset_complete"),
]