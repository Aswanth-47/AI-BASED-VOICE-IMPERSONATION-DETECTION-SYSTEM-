from django.contrib import admin
from .models import VoiceAnalysis, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_analyses', 'ai_detected', 'human_detected', 'created_at']
    search_fields = ['user__username', 'user__email']


@admin.register(VoiceAnalysis)
class VoiceAnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'file_name', 'result', 'confidence_score', 'duration', 'analyzed_at']
    list_filter = ['result', 'analyzed_at']
    search_fields = ['user__username', 'file_name']
    readonly_fields = ['analyzed_at']
    ordering = ['-analyzed_at']
