# 🎓 UniManage: Intelligent University Management System

<div align="center">
  
  **Core Languages** <br>
  [![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
  [![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](#)
  [![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)](#)
  [![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](#)
  <br><br>**Frameworks & Architecture** <br>
  [![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](#)
  [![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)](#)
  <br><br>**Upcoming Integrations** <br>
  [![Data Science Ready](https://img.shields.io/badge/Data_Science-Ready-FF6F00?style=for-the-badge&logo=jupyter&logoColor=white)](#)
  <br><br>
  **A modern, role-based educational platform featuring secure document handling, real-time theme transitions, and an architecture ready for Machine Learning integration.**
</div>

---

## 📑 Table of Contents
- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [Project Architecture](#-project-architecture)
- [Interactive Folder Tree](#-interactive-folder-tree)
- [Installation & Setup](#-installation--setup)
- [Data Science Roadmap](#-data-science-roadmap)

---

## 🚀 About the Project
**UniManage** bridges the gap between students and faculty through a seamless, highly secure web portal. Built on Django, it utilizes a custom unified user model to intelligently route users to specific dashboards based on their role (`is_student` vs `is_teacher`). 

Beyond standard CRUD operations, this project emphasizes **modern UI/UX** (featuring the experimental View Transitions API for dark mode) and **Data Privacy** (securely routing uploaded PDF submissions only to the authorized professor).

---

## ✨ Key Features

### 👨‍🏫 Teacher Portal
* **Role-Based Access Control (RBAC):** Teachers are automatically routed to a dedicated dashboard.
* **Live Attendance Tracking:** Interactive grid cards to mark students Present (Green) or Absent (Red) with immediate database updates.
* **Secure Submission Vault:** Teachers only see assignment submissions linked to the specific subjects they are assigned to teach.
* **Grading Engine:** A streamlined interface to input marks and evaluate student performance.

### 👨‍🎓 Student Portal
* **Automated Profile Generation:** Custom Signup forms seamlessly hash passwords and generate linked `StudentProfile` instances (Roll No, Batch Year) in a single transaction.
* **Assignment Uploads:** Secure file handling for uploading PDF coursework directly to the server's protected `/media/` directory.
* **Performance Tracking:** Real-time visibility into personal attendance records and graded assignments.

### 🎨 Premium UI/UX Core
* **View Transition Theme Toggle:** A custom-built, JavaScript-powered Dark/Light mode toggle that uses `clip-path` math to create a stunning "expanding circle" ripple effect across the entire DOM.
* **Glassmorphism Design:** Modern, semi-transparent frosted glass cards over premium slate and navy gradients.
* **Persistent State:** Uses `localStorage` and synchronous `<head>` initialization to prevent theme flashing on page reload.

---

## 🏗 Project Architecture

<details>
<summary><b>Click to expand the Database Blueprint 🗄️</b></summary>

1. **Authentication:** * `Custom User Model` containing `is_student` and `is_teacher` booleans.
   * Linked via `OneToOneField` to `TeacherProfile` and `StudentProfile`.
2. **Academics:**
   * `Subject` model linked to a specific `TeacherProfile` (`ForeignKey`).
   * `Assignment` model linked to a `Subject`.
3. **Tracking:**
   * `Submission` model capturing the `Student`, the `Assignment`, and the uploaded PDF file.
   * `Attendance` model linking a `Student`, a Date, and a Status.
</details>

<details>
<summary><b>Click to expand Security Protocols 🔒</b></summary>

* **Environment Variables:** `SECRET_KEY` and `DEBUG` status are stripped from the codebase and managed via `python-dotenv`.
* **Queryset Filtering:** `Submission.objects.filter(assignment__subject__teacher=current_teacher)` ensures absolute data privacy between professors.
* **Route Protection:** `@login_required` decorators combined with role-checking redirects prevent URL-guessing access.
</details>

---

## 📂 Interactive Folder Tree

The project strictly adheres to modular separation of concerns, utilizing isolated static files and namespaced template subdirectories.

```text
📁 University_Management_System/
├── 📁 core/                         # Main Django Application
│   ├── 📁 migrations/               # Database schemas
│   ├── 📁 static/                   # Segregated CSS and JS
│   │   ├── 📁 css/
|   |   |   ├── 📄 login-signup.css  # Login & Signup UI styles
│   │   │   ├── 📄 theme.css         # CSS Variables & View Transition logic
│   │   │   ├── 📄 student.css       # Student UI styles
│   │   │   └── 📄 teacher.css       # Teacher UI styles
│   │   └── 📁 js/ 
│   │       ├── 📄 theme-init.js     # Anti-flash local storage check
│   │       └── 📄 theme.js          # Ripple animation math & listeners
│   ├── 📁 templates/
│   │   └── 📁 core/                 # Namespaced templates
│   │       ├── 📄 base.html         # Master layout & Navbar
│   │       ├── 📄 login.html
│   │       ├── 📄 signup.html
│   │       ├── 📁 student/          # Isolated student views
│   │       └── 📁 teacher/          # Isolated teacher views
|   ├── 📄 admin.py                  # Admin side table structure (enter with you username & pass)
|   ├── 📄 apps.py                   # App setup
│   ├── 📄 forms.py                  # Custom UserCreation & Profile forms
│   ├── 📄 models.py                 # SQLite Table architectures
│   ├── 📄 urls.py                   # App-level routing
│   └── 📄 views.py                  # Backend logic & context processing
│
├── 📁 media/                        # User Uploads (Git-Ignored)
│   └── 📁 submissions/              # Student PDFs
│
├── 📁 university_sys/               # Django Project Settings
|   ├── 📄 asgi.py
│   ├── 📄 settings.py               # Configured with python-dotenv
|   ├── 📄 urls.py                   # Root URL routing
│   └── 📄 wsgi.py
│
├── 📄 .env.example                  # Template for local environment setup
├── 📄 .gitignore                    # Hides DB, Cache, Media, and Secrets
├── 📄 manage.py                     # CLI entry point
└── 📄 README.md                     # You are here!
```

## ⚙️ Installation & Setup
Want to run this project locally? Follow these steps:

### 1. Clone the repository

```
git clone [https://github.com/yourusername/UniManage.git](https://github.com/yourusername/UniManage.git)
cd UniManage
```

### 2. Set up the Environment

Create a .env file in the root directory and copy the format from .env.example:

```
SECRET_KEY=your_super_secret_django_key_here
DEBUG=True
```

### 3. Install Dependencies
(Assuming you have Python installed)

```
pip install django
pip install python-dotenv
```

### 4. Run Migrations & Create Superuser
Initialize the SQLite database and create your admin account:

```
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 5. Boot the Server

```
python manage.py runserver
``` 

Visit http://127.0.0.1:8000 to see the app live!

## 📈 Data Science Roadmap (Future Scope)
This application was architected specifically to act as the data-collection foundation for future Machine Learning and Analytics integrations:

- [ ] Predictive "At-Risk" Engine: Integrate scikit-learn (Random Forest) to analyze attendance and grade arrays to flag failing students early.

- [ ] Live Dashboards: Replace static tables with interactive Plotly or Apache ECharts graphs for subject-wide performance distributions.

- [ ] Automated PDF Analyzer: Utilize PyPDF2 to read uploaded student assignments and run Cosine Similarity algorithms to detect plagiarism across the cohort.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Since this project is actively evolving towards a data-heavy architecture, any pull requests regarding Machine Learning model integration, database optimization, or data visualization are highly appreciated.

1. **Fork** the Project
2. **Create** your Feature Branch (`git checkout -b feature/AmazingDataFeature`)
3. **Commit** your Changes (`git commit -m 'Add some AmazingDataFeature'`)
4. **Push** to the Branch (`git push origin feature/AmazingDataFeature`)
5. **Open** a Pull Request

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 📬 Contact & Connect

**Aaryan Kalia** Software Engineering & Data Analytics Enthusiast

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Aar2284)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:aaryankalia165@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](#) 

**Project Link:** [https://github.com/Aar2284/University_Management_Sys](https://github.com/Aar2284/University_Management_Sys)

---

## 🙏 Acknowledgments

* [Django Documentation](https://docs.djangoproject.com/) for the incredibly robust backend framework.
* [View Transitions API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transitions_API) for powering the experimental, seamless dark-mode ripple effects.
* [Python-Dotenv](https://saurabh-kumar.com/python-dotenv/) for keeping environment variables and secrets locked down.
