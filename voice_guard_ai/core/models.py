from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    total_analyses = models.IntegerField(default=0)
    ai_detected = models.IntegerField(default=0)
    human_detected = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def detection_accuracy(self):
        if self.total_analyses == 0:
            return 0
        return round((self.ai_detected + self.human_detected) / self.total_analyses * 100, 1)


class VoiceAnalysis(models.Model):
    RESULT_CHOICES = [
        ('human', 'Human Voice'),
        ('ai', 'AI Generated'),
        ('uncertain', 'Uncertain'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analyses')
    audio_file = models.FileField(upload_to='audio_uploads/')
    file_name = models.CharField(max_length=255)
    file_size = models.FloatField(default=0)  # in KB
    duration = models.FloatField(default=0)   # in seconds
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='uncertain')
    confidence_score = models.FloatField(default=0.0)  # 0 to 100
    analyzed_at = models.DateTimeField(auto_now_add=True)

    # Feature scores (0-100)
    spectral_score = models.FloatField(default=0.0)
    pitch_score = models.FloatField(default=0.0)
    rhythm_score = models.FloatField(default=0.0)
    noise_score = models.FloatField(default=0.0)
    formant_score = models.FloatField(default=0.0)

    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-analyzed_at']

    def __str__(self):
        return f"{self.user.username} - {self.file_name} - {self.result}"

    @property
    def result_badge_class(self):
        return {
            'human': 'badge-human',
            'ai': 'badge-ai',
            'uncertain': 'badge-uncertain',
        }.get(self.result, 'badge-uncertain')

    @property
    def result_icon(self):
        return {
            'human': '👤',
            'ai': '🤖',
            'uncertain': '❓',
        }.get(self.result, '❓')
