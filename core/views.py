from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from streamlit import form
from .forms import StudentSignUpForm
from django.utils import timezone
from .models import User, StudentProfile, Attendance, TeacherSubjectHistory, Grade, Subject, Assignment, Submission
import datetime
from django.db.models import Avg
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# ==========================================
# --- AUTHENTICATION VIEWS ---
# ==========================================

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_teacher:
            return redirect('teacher_dashboard')
        elif request.user.is_student:
            return redirect('student_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                if user.is_teacher:
                    return redirect('teacher_dashboard')
                elif user.is_student:
                    return redirect('student_dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'core/login.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('login')

def signup_view(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            return redirect('student_dashboard')
    else:
        form = StudentSignUpForm()
        
    return render(request, 'core/signup.html', {'form': form})


# ==========================================
# --- STUDENT VIEWS ---
# ==========================================

from django.db.models import Avg

@login_required(login_url='login')
def student_dashboard(request):
    # Safety check: if teacher accidentally gets here, send them back
    if request.user.is_teacher:
        return redirect('teacher_dashboard')

    # 1. Get Total Classes Attended (Count where status is 'P')
    classes_attended = Attendance.objects.filter(student__user=request.user, status='P').count()

    # 2. Get Overall Average Grade
    # Assuming your model is named Grade and has a 'marks' field (like we used for teachers)
    avg_data = Grade.objects.filter(student__user=request.user).aggregate(Avg('marks'))
    if avg_data['marks__avg']:
        grade_avg = f"{round(avg_data['marks__avg'])}%"
    else:
        grade_avg = "N/A"

    # 3. Get Active/Missing Assignments
    # Grabbing all assignments for now. You can filter this later based on submission status!
    missing_assignments = Assignment.objects.count()

    # 4. Get Recent Attendance Timeline (Grab the last 5 records)
    recent_attendance = Attendance.objects.filter(student__user=request.user).order_by('-date')[:5]

    context = {
        'classes_attended': classes_attended,
        'grade_avg': grade_avg,
        'missing_assignments': missing_assignments,
        'attendance_records': recent_attendance,
    }
    
    return render(request, 'student_side/student_dashboard.html', context)

# ==========================================
# --- TEACHER VIEWS ---
# ==========================================

@login_required(login_url='login')
def teacher_dashboard(request):
    if not request.user.is_teacher:
        return redirect('student_dashboard')
        
    teacher = request.user.teacherprofile
    
    # 1. Get all subject history entries for this teacher
    all_subject_histories = TeacherSubjectHistory.objects.filter(teacher=teacher).select_related('subject')
    
    # 2. Filter for just the ACTIVE ones for calculations
    active_subject_histories = all_subject_histories.filter(is_active=True)
    
    # Get the IDs of active subjects
    active_subject_ids = active_subject_histories.values_list('subject_id', flat=True)
    
    # --- CORRECTED: Use 'marks' instead of 'raw_marks' ---
    overall_avg_data = Grade.objects.filter(subject_id__in=active_subject_ids).aggregate(Avg('marks'))
    overall_avg_score = round(overall_avg_data['marks__avg'] or 0)

    # --- CORRECTED: Calculate Per-Subject Averages ---
    subject_averages = []
    for history in active_subject_histories:
        avg_data = Grade.objects.filter(subject=history.subject).aggregate(Avg('marks'))
        avg_score = round(avg_data['marks__avg'] or 0)
        subject_averages.append({
            'subject_name': history.subject.name,
            'subject_code': history.subject.code,
            'average': avg_score
        })

    # --- Existing sidebar data ---
    total_students = StudentProfile.objects.count()
    active_subjects_count = active_subject_histories.count()
    
    context = {
        'subjects': all_subject_histories, 
        'total_students': total_students,
        'active_subjects_count': active_subjects_count,
        'overall_avg_percentage': overall_avg_score,
        'subject_averages': subject_averages, 
    }
    return render(request, 'teacher_side/teacher_dashboard.html', context)


# Make sure you import Subject, StudentProfile, and Attendance at the top of your views.py!

@login_required(login_url='login')
def take_attendance(request):
    # Keep students out
    if not request.user.is_teacher:
        return redirect('student_dashboard')

    if request.method == 'POST':
        # 1. Grab the Subject and Date from the form
        subject_id = request.POST.get('subject')
        date = request.POST.get('date')
        
        subject = Subject.objects.get(id=subject_id)
        students = StudentProfile.objects.all()
        
        # 2. Loop through every student and save their specific status
        for student in students:
            # The HTML form will send variables like 'student_1', 'student_2', etc.
            # Default to 'A' (Absent) if nothing is found
            status = request.POST.get(f'student_{student.user_id}', 'A') 
            
            # Create or update the attendance record
            Attendance.objects.update_or_create(
                student=student,
                subject=subject,
                date=date,
                defaults={'status': status}
            )
        
        # Once saved, refresh the page or send them to the dashboard
        return redirect('teacher_dashboard')

    # IF GET REQUEST: Load the page with the dropdown options
    subjects = Subject.objects.all()
    students = StudentProfile.objects.all()
    
    context = {
        'subjects': subjects,
        'students': students,
    }
    return render(request, 'teacher_side/teacher_attendance.html', context)


@login_required(login_url='login')
def mark_attendance(request):
    if request.method == 'POST':
        if not request.user.is_teacher:
            return redirect('student_dashboard')
            
        student_id = request.POST.get('student_id')
        status = request.POST.get('status')
        # We need to capture the Subject ID now too! (See Step 2b below)
        # For now, let's assume the teacher is marking for their first active subject
        # (We will make this smarter later, but this keeps it simple for now)
        teacher_history = TeacherSubjectHistory.objects.filter(teacher__user=request.user, is_active=True).first()
        subject = teacher_history.subject if teacher_history else None
        
        student = get_object_or_404(StudentProfile, user__id=student_id)
        
        # --- THE CHANGE: Use .create() instead of .get_or_create() ---
        # This allows multiple entries per day
        Attendance.objects.create(
            student=student,
            subject=subject, 
            date=datetime.date.today(),
            status=status
        )
            
        if status == 'P':
            messages.success(request, f"Marked {student.user.username} as Present!")
        else:
            messages.error(request, f"Marked {student.user.username} as Absent!")
        
    return redirect('take_attendance')

@login_required(login_url='login')
def manage_grades(request):
    # Keep students out
    if not request.user.is_teacher:
        return redirect('student_dashboard')

    if request.method == 'POST':
        # Grab the data the teacher submitted
        subject_id = request.POST.get('subject')
        student_id = request.POST.get('student')
        marks = request.POST.get('marks')
        
        subject = Subject.objects.get(id=subject_id)
        student = StudentProfile.objects.get(user_id=student_id)
        
        # Create or update the student's grade
        Grade.objects.update_or_create(
            student=student,
            subject=subject,
            defaults={'marks': marks}
        )
        return redirect('manage_grades') # Refresh the page after saving

    # IF GET REQUEST: Load the subjects and students to show in the dropdowns!
    subjects = Subject.objects.all()
    students = StudentProfile.objects.all()
    
    context = {
        'subjects': subjects,
        'students': students,
    }
    return render(request, 'teacher_side/teacher_grades.html', context)

@login_required(login_url='login')
def student_attendance(request):
    if request.user.is_teacher:
        return redirect('teacher_dashboard')

    attendance_records = Attendance.objects.filter(student__user=request.user).order_by('-date')
    
    total_classes = attendance_records.count()
    attended_classes = attendance_records.filter(status='P').count()
    
    if total_classes > 0:
        health_percentage = int((attended_classes / total_classes) * 100)
    else:
        health_percentage = 100 

    context = {
        'attendance_records': attendance_records,
        'health_percentage': health_percentage,
        'attended_classes': attended_classes,
        'total_classes': total_classes
    }
    return render(request, 'student_side/student_attendance.html', context)

@login_required(login_url='login')
def create_assignment(request):
    if request.method == 'POST' and request.user.is_teacher:
        title = request.POST.get('title')
        subject_id = request.POST.get('subject_id')
        due_date = request.POST.get('due_date')

        try:
            # Find the subject and create the assignment
            subject = Subject.objects.get(id=subject_id)
            Assignment.objects.create(
                title=title,
                subject=subject,
                due_date=due_date
            )
            messages.success(request, f"Assignment '{title}' pushed to {subject.code} successfully!")
        except Subject.DoesNotExist:
            messages.error(request, "Invalid subject selected.")
        except Exception as e:
            messages.error(request, f"Error creating assignment: {e}")

    # Redirect right back to the dashboard
    return redirect('teacher_dashboard')

from .models import Submission # Make sure to import Submission at the top!

# 1. UPDATE your existing student_assignments view:
@login_required(login_url='login')
def student_assignments(request):
    if request.user.is_teacher:
        return redirect('teacher_dashboard')

    assignments = Assignment.objects.all().order_by('due_date')
    # Get a list of assignment IDs this student has already submitted
    submitted_ids = Submission.objects.filter(student__user=request.user).values_list('assignment_id', flat=True)

    context = {
        'assignments': assignments,
        'submitted_ids': submitted_ids, # Pass this to the template
    }
    return render(request, 'student_side/student_assignments.html', context)

# 2. ADD the new Upload View:
@login_required(login_url='login')
def submit_work(request, assignment_id):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        student = request.user.studentprofile 
        
        # Create the submission
        submission = Submission.objects.create(
            assignment=assignment,
            student=student,
            pdf_file=request.FILES['pdf_file']
        )      
        return redirect('submission_success', submission_id=submission.id)
    return redirect('student_assignments')

@login_required(login_url='login')
def submission_success(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id, student__user=request.user)
    
    # Check if a grade already exists (unlikely right after submission, but good for the logic)
    grade = Grade.objects.filter(student=submission.student, subject=submission.assignment.subject).first()
    
    context = {
        'submission': submission,
        'grade': grade
    }
    return render(request, 'student_side/submission_success.html', context)

# 3. ADD the Teacher Submissions View:
@login_required(login_url='login')
def teacher_submissions(request):
    if not request.user.is_teacher:
        return redirect('student_dashboard')
    
    current_teacher = request.user.teacherprofile
    # Get all submissions for assignments in subjects taught by this teacher
    submissions = Submission.objects.filter(assignment__subject__teachersubjecthistory__teacher=current_teacher).order_by('-submitted_at')
    
    context = {
        'submissions': submissions
    }
    return render(request, 'teacher_side/teacher_submissions.html', context)

@login_required(login_url='login')
def teacher_results(request):
    if not request.user.is_teacher:
        return redirect('student_dashboard')
    
    current_teacher = request.user.teacherprofile
    # Get all grades for subjects taught by this teacher
    grades = Grade.objects.filter(subject__teacher=current_teacher).order_by('subject', '-marks')
    
    context = {
        'grades': grades
    }
    return render(request, 'teacher_side/teacher_results.html', context)

def student_signup(request):
    # If they are already logged in, send them away
    if request.user.is_authenticated:
        return redirect('student_dashboard')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # MAGICAL STEP: Automatically create their StudentProfile!
            StudentProfile.objects.create(user=user)
            
            # Automatically log them in right after signing up
            login(request, user)
            return redirect('student_dashboard')
    else:
        form = UserCreationForm()
        
    return render(request, 'registration/signup.html', {'form': form})