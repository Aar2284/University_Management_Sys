from django.contrib import admin
from .models import StudentRisk, PlagiarismReport


@admin.register(StudentRisk)
class StudentRiskAdmin(admin.ModelAdmin):
    list_display = ['student', 'risk_level', 'risk_score', 'attendance_pct', 'avg_marks', 'failing_subjects', 'predicted_at']
    list_filter = ['risk_level', 'predicted_at']
    search_fields = ['student__user__username', 'student__roll_number']


@admin.register(PlagiarismReport)
class PlagiarismReportAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'submission_a', 'submission_b', 'similarity_score', 'checked_at']
    list_filter = ['assignment', 'checked_at']
    search_fields = ['assignment__title']
