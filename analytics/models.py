from django.db import models
from core.models import StudentProfile


class StudentRisk(models.Model):
    RISK_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, help_text="0-100, higher = more risk")
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS)
    attendance_pct = models.DecimalField(max_digits=5, decimal_places=2)
    avg_marks = models.DecimalField(max_digits=5, decimal_places=2)
    failing_subjects = models.IntegerField(default=0)
    model_version = models.CharField(max_length=50, default='v1.0')
    predicted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-risk_score']

    def __str__(self):
        return f"{self.student.user.username} - {self.risk_level} ({self.risk_score}%)"
