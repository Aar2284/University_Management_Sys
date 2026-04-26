from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from analytics.models import StudentRisk


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
