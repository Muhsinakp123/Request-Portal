from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_View, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/employee/', views.employee_dashboard, name='employee_dashboard'),
    path('dashboard/technician/', views.technician_dashboard, name='technician_dashboard'),

    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<int:user_id>/', views.reset_password, name='reset_password'),

    path('profile/', views.profile, name='profile'),

    path('create_requests/', views.create_requests, name='create_requests'),
    path('employee/my-requests/', views.my_requests, name='my_requests'),
    path('employee/request-history/', views.request_history, name='request_history'),
    path('employee/request/update/<int:pk>/', views.update_request, name='update_request'),
    path('delete/<int:pk>/', views.delete_request, name='delete_request'),
    
    # Admin routes
    path('dashboard/admin/view-users/', views.view_users, name='view_users'),
    path('dashboard/admin/manage-requests/', views.manage_requests, name='manage_requests'),
    path('dashboard/admin/reports/', views.reports, name='reports'),
    
    
    # Technician URLs
    path('technician/assigned-tasks/', views.assigned_tasks, name='assigned_tasks'),
    path('technician/update-progress/<int:pk>/', views.update_progress, name='update_progress'),
    path('technician/completed-tasks/', views.completed_tasks, name='completed_tasks'),
    path("technician/accept/<int:pk>/", views.accept_task, name="accept_task"),
    path('reject-task/<int:pk>/', views.reject_task, name='reject_task'),





]
