from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('analyze/', views.analyze_audio_view, name='analyze'),
    path('history/', views.analysis_history, name='history'),
    path('analysis/<int:pk>/', views.analysis_detail, name='analysis_detail'),
    path('analysis/<int:pk>/delete/', views.delete_analysis, name='delete_analysis'),
]
