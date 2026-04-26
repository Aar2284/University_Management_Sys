from django.contrib import admin
from .models import StudentRisk


@admin.register(StudentRisk)
class StudentRiskAdmin(admin.ModelAdmin):
    list_display = ['student', 'risk_level', 'risk_score', 'attendance_pct', 'avg_marks', 'failing_subjects', 'predicted_at']
    list_filter = ['risk_level', 'predicted_at']
    search_fields = ['student__user__username', 'student__roll_number']
