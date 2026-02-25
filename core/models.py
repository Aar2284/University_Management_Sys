from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Max

# 1. CORE AUTHENTICATION
class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    
    # THE MISSING LINK: This connects a Subject to a specific Teacher!
    teacher = models.ForeignKey('TeacherProfile', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

# 2. TEACHER MODELS & HISTORY
class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    department = models.CharField(max_length=100)
    
    def __str__(self):
        return self.user.username

class TeacherSubjectHistory(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True) # True = Highlighted/Teaching Now, False = History
    assigned_date = models.DateField(auto_now_add=True)

    class Meta:
        # This prevents the admin from assigning the exact same subject twice
        unique_together = ('teacher', 'subject') 

    def __str__(self):
        return f"{self.teacher.user.username} - {self.subject.name}"

# 3. STUDENT MODELS, ATTENDANCE & GRADES
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    roll_number = models.CharField(max_length=20, unique=True)
    batch_year = models.CharField(max_length=10)
    
    def __str__(self):
        return self.roll_number

class Attendance(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10)
    
    # auto_now_add=True means "Save the exact clock time when this is created"
    time = models.TimeField(auto_now_add=True, null=True) 

    def __str__(self):
        return f"{self.student.user.username} - {self.date} {self.time}"

class Grade(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks = models.DecimalField(max_digits=5, decimal_places=2)

    def get_relative_grade(self):
        # 1. Find the highest marks any student got in THIS specific subject
        highest_score_dict = Grade.objects.filter(subject=self.subject).aggregate(Max('marks'))
        highest_score = highest_score_dict['marks__max']

        # 2. Safety check: prevent dividing by zero if no one has marks or highest is 0
        if not highest_score or highest_score == 0:
            return {'letter': 'F', 'point': 0.0}

        # 3. Calculate the relative percentage
        relative_percentage = (self.marks / highest_score) * 100

        # 4. Assign the dynamic grade based on the curve
        if relative_percentage >= 90:
            return {'letter': 'O', 'point': 10.0}  
        elif relative_percentage >= 80:
            return {'letter': 'A+', 'point': 9.0}
        elif relative_percentage >= 70:
            return {'letter': 'A', 'point': 8.0}
        elif relative_percentage >= 60:
            return {'letter': 'B+', 'point': 7.0}
        elif relative_percentage >= 50:
            return {'letter': 'B', 'point': 6.0}
        elif relative_percentage >= 40:
            return {'letter': 'C', 'point': 5.0}
        else:
            return {'letter': 'F', 'point': 0.0}
            
    def __str__(self):
        return f"{self.student.user.username} - {self.subject.name}: {self.marks}"

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    due_date = models.DateField()

    def __str__(self):
        return f"{self.title} - {self.subject.code}"
    
class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    
    # CHANGE 'Student' TO 'StudentProfile' (Or whatever your exact class name is!)
    student = models.ForeignKey('StudentProfile', on_delete=models.CASCADE) 
    
    pdf_file = models.FileField(upload_to='submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('assignment', 'student') 

    def __str__(self):
        return f"{self.student.user.username} - {self.assignment.title}"