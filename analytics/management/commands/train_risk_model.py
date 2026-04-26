import numpy as np
from django.core.management.base import BaseCommand
from django.db.models import Avg, Count, Q
from core.models import StudentProfile, Attendance, Grade
from analytics.models import StudentRisk


class Command(BaseCommand):
    help = 'Train the at-risk prediction model and store predictions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--passing-marks',
            type=float,
            default=40.0,
            help='Marks below this threshold = failing (default: 40)',
        )
        parser.add_argument(
            '--risk-threshold',
            type=float,
            default=50.0,
            help='Risk score above this = High risk (default: 50)',
        )

    def handle(self, *args, **options):
        passing_marks = options['passing_marks']
        risk_threshold = options['risk_threshold']

        students = StudentProfile.objects.all()
        if not students.exists():
            self.stdout.write(self.style.WARNING('No students found. Nothing to train.'))
            return

        self.stdout.write(f'Building training data for {students.count()} students...')

        features = []
        labels = []
        student_ids = []

        for student in students:
            # Feature 1: Attendance percentage
            total_classes = Attendance.objects.filter(student=student).count()
            if total_classes > 0:
                present_count = Attendance.objects.filter(student=student, status='P').count()
                attendance_pct = (present_count / total_classes) * 100
            else:
                attendance_pct = 100.0

            # Feature 2: Average marks across all subjects
            avg_data = Grade.objects.filter(student=student).aggregate(Avg('marks'))
            avg_marks = float(avg_data['marks__avg'] or 0)

            # Feature 3: Number of subjects with marks below passing
            failing_count = Grade.objects.filter(
                student=student, marks__lt=passing_marks
            ).values('subject').distinct().count()

            # Feature 4: Total subjects enrolled
            total_subjects = Grade.objects.filter(student=student).values('subject').distinct().count()

            # Feature 5: Fail ratio (failing subjects / total subjects)
            fail_ratio = failing_count / total_subjects if total_subjects > 0 else 0

            # Feature 6: Number of absences
            absence_count = Attendance.objects.filter(student=student, status='A').count()

            feature_row = [attendance_pct, avg_marks, failing_count, total_subjects, fail_ratio, absence_count]
            features.append(feature_row)
            student_ids.append(student.user_id)

            # Label: at-risk if attendance < 75% OR avg marks < passing OR fail ratio >= 0.5
            is_at_risk = 1 if (attendance_pct < 75 or avg_marks < passing_marks or fail_ratio >= 0.5) else 0
            labels.append(is_at_risk)

        X = np.array(features)
        y = np.array(labels)

        self.stdout.write(f'Features shape: {X.shape}')
        self.stdout.write(f'At-risk students: {sum(y)} / {len(y)}')

        # Train model inline (no need for sklearn for simple threshold-based rules)
        # But we also use RandomForest for more nuanced predictions when enough data
        model_version = 'v1.0'

        if len(y) >= 10:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import cross_val_score

            clf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
            scores = cross_val_score(clf, X, y, cv=min(5, len(y)), scoring='accuracy')
            self.stdout.write(f'Cross-validation accuracy: {scores.mean():.2f} (+/- {scores.std():.2f})')

            clf.fit(X, y)

            if clf.n_classes_ > 1:
                predictions = clf.predict_proba(X)[:, 1] * 100
            else:
                predictions = clf.predict(X).astype(float) * 100
            model_version = 'v1.0-ml'
        else:
            # Rule-based fallback for small datasets
            self.stdout.write('Not enough data for ML model. Using rule-based scoring.')
            predictions = []
            for row in features:
                att, avg, fail_c, total_s, fail_r, abs_c = row
                score = 0
                if att < 75:
                    score += (75 - att) * 0.8
                if avg < passing_marks:
                    score += (passing_marks - avg) * 0.6
                if fail_r >= 0.5:
                    score += 20
                if abs_c > total_s * 0.3:
                    score += 15
                predictions.append(min(score, 100))

        # Store predictions
        StudentRisk.objects.all().delete()
        created_count = 0

        for i, student_id in enumerate(student_ids):
            risk_score = round(float(predictions[i]), 2)
            risk_score = max(0, min(100, risk_score))

            if risk_score >= risk_threshold:
                risk_level = 'high'
            elif risk_score >= risk_threshold * 0.5:
                risk_level = 'medium'
            else:
                risk_level = 'low'

            # Recalculate stats for storage
            student = StudentProfile.objects.get(user_id=student_id)
            total_classes = Attendance.objects.filter(student=student).count()
            if total_classes > 0:
                present_count = Attendance.objects.filter(student=student, status='P').count()
                att_pct = round((present_count / total_classes) * 100, 2)
            else:
                att_pct = 100.0

            avg_data = Grade.objects.filter(student=student).aggregate(Avg('marks'))
            avg_m = round(float(avg_data['marks__avg'] or 0), 2)

            fail_subj = Grade.objects.filter(
                student=student, marks__lt=passing_marks
            ).values('subject').distinct().count()

            StudentRisk.objects.create(
                student=student,
                risk_score=risk_score,
                risk_level=risk_level,
                attendance_pct=att_pct,
                avg_marks=avg_m,
                failing_subjects=fail_subj,
                model_version=model_version,
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Successfully stored {created_count} risk predictions (model: {model_version})'
        ))
