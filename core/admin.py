from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Subject, TeacherProfile, TeacherSubjectHistory, StudentProfile, Attendance, Grade, Assignment

# 1. Customizing the User Admin
class CustomUserAdmin(UserAdmin):
    # This adds your custom role checkboxes to the admin screen!
    fieldsets = UserAdmin.fieldsets + (
        ('Role Configuration', {'fields': ('is_student', 'is_teacher')}),
    )

admin.site.register(User, CustomUserAdmin)

# 2. Registering standard models
admin.site.register(Subject)
admin.site.register(TeacherProfile)
admin.site.register(StudentProfile)
admin.site.register(Attendance)
admin.site.register(Grade)

# 3. Customizing the History Table view for better admin UX
class TeacherSubjectHistoryAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'is_active', 'assigned_date')
    list_filter = ('is_active', 'subject')

admin.site.register(TeacherSubjectHistory, TeacherSubjectHistoryAdmin)

admin.site.register(Assignment)