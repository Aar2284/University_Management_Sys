from django.urls import path
from . import views

urlpatterns = [
    path('at-risk/', views.at_risk_students, name='at_risk_students'),
]
