from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Avg, Count
from analytics.models import StudentRisk
from core.models import StudentProfile, Attendance, Grade, Subject, TeacherSubjectHistory


@login_required(login_url='login')
def at_risk_students(request):
    if not request.user.is_teacher:
        return redirect('student_dashboard')

    risk_data = StudentRisk.objects.select_related('student__user').all()

    high_risk = risk_data.filter(risk_level='high')
    medium_risk = risk_data.filter(risk_level='medium')
    low_risk = risk_data.filter(risk_level='low')

    context = {
        'risk_data': risk_data,
        'high_risk': high_risk,
        'medium_risk': medium_risk,
        'low_risk': low_risk,
        'total_students': risk_data.count(),
    }
    return render(request, 'analytics/at_risk.html', context)


@login_required(login_url='login')
def live_dashboard(request):
    if not request.user.is_teacher:
        return redirect('student_dashboard')

    teacher = request.user.teacherprofile
    active_subjects = TeacherSubjectHistory.objects.filter(
        teacher=teacher, is_active=True
    ).select_related('subject')

    # Chart 1: Subject-wise average marks (bar chart)
    subject_names = []
    subject_avgs = []
    for h in active_subjects:
        avg = Grade.objects.filter(subject=h.subject).aggregate(Avg('marks'))['marks__avg']
        subject_names.append(f"{h.subject.name} ({h.subject.code})")
        subject_avgs.append(round(float(avg or 0), 2))

    # Chart 2: Attendance distribution per subject (pie chart)
    att_labels = []
    att_present = []
    att_absent = []
    for h in active_subjects:
        total = Attendance.objects.filter(subject=h.subject).count()
        present = Attendance.objects.filter(subject=h.subject, status='P').count()
        att_labels.append(h.subject.code)
        att_present.append(present)
        att_absent.append(total - present)

    # Chart 3: Grade distribution (histogram-like breakdown)
    grade_buckets = {'O': 0, 'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C': 0, 'F': 0}
    all_grades = Grade.objects.filter(subject__in=[h.subject for h in active_subjects])
    for g in all_grades:
        if g.marks >= 90: grade_buckets['O'] += 1
        elif g.marks >= 80: grade_buckets['A+'] += 1
        elif g.marks >= 70: grade_buckets['A'] += 1
        elif g.marks >= 60: grade_buckets['B+'] += 1
        elif g.marks >= 50: grade_buckets['B'] += 1
        elif g.marks >= 40: grade_buckets['C'] += 1
        else: grade_buckets['F'] += 1

    # Chart 4: Student performance scatter (marks vs attendance %)
    scatter_x = []  # attendance %
    scatter_y = []  # avg marks
    scatter_text = []
    for student in StudentProfile.objects.all():
        total_cls = Attendance.objects.filter(student=student).count()
        if total_cls == 0:
            continue
        present = Attendance.objects.filter(student=student, status='P').count()
        att_pct = round((present / total_cls) * 100, 1)
        avg_mark = Grade.objects.filter(student=student).aggregate(Avg('marks'))['marks__avg']
        if avg_mark is not None:
            scatter_x.append(att_pct)
            scatter_y.append(round(float(avg_mark), 1))
            scatter_text.append(student.user.username)

    context = {
        'subject_names': subject_names,
        'subject_avgs': subject_avgs,
        'att_labels': att_labels,
        'att_present': att_present,
        'att_absent': att_absent,
        'grade_labels': list(grade_buckets.keys()),
        'grade_values': list(grade_buckets.values()),
        'scatter_x': scatter_x,
        'scatter_y': scatter_y,
        'scatter_text': scatter_text,
    }
    return render(request, 'analytics/live_dashboard.html', context)
