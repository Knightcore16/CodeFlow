from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Prefetch, Count, Avg, Q
from django.http import JsonResponse
from .models import Course, Module, Quiz, Question, QuizAttempt, QuestionResponse
from .models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


# Create your views here.
def index(request):
    username = request.user.username
    return render(request, "index.html", {'username':username})


def resources(request):
    username = request.user.username

    return render(request, "resources.html", {'username' : username})


def leaderboard(request):
    username = request.user.username

    return render(request, "leaderboard.html",{'username' : username})

@login_required
def courses(request):
    """
    Display list of all courses with progress for the current user
    """
    courses = Course.objects.annotate(
        total_modules=Count('modules'),
        total_quizzes=Count('modules__quizzes'),
        completed_quizzes=Count(
        'modules__quizzes__attempts',
        filter=Q(modules__quizzes__attempts__user=request.user) & Q(modules__quizzes__attempts__completed=True)
    )
    )
    
    for course in courses:
        course.progress = (
            (course.completed_quizzes / course.total_quizzes * 100)
            if course.total_quizzes > 0 else 0
        )
        
    course.total_modules = course.total_modules

    
    context = {
        'courses': courses,
        'page_title': 'Available Courses'
    }
    return render(request, 'courses.html', context)

@login_required
def lessons(request, course_slug):
    
    """
    Display course details with modules and quizzes
    """
    course = get_object_or_404(Course, slug=course_slug)
    
    course_module_count = Module.objects.filter(course=course).count()

    
    modules = Module.objects.filter(course=course).prefetch_related(
        Prefetch(
            'quizzes',
            queryset=Quiz.objects.annotate(
                has_attempt=Count(
                    'attempts',
                    filter=Q(attempts__user=request.user) & Q(attempts__completed=True)
                )
            )
        )
    ).order_by('order')
    
    progress = course.get_progress(request.user)
    
    context = {
        'course': course,
        'courses_modules' : course_module_count,
        'modules': modules,
        'progress': progress,
        'page_title': course.title
    }
    return render(request, 'lessons.html', context)



def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Invalid Username or Password")
            return redirect("/login")

        login(request, user)
        return redirect("/")
    return render(request, "login.html")


def register_user(request):

    def process_full_name(full_name):
        parts = full_name.strip().split()
        first_name = parts[0] if parts else ""
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

        return first_name, last_name

    if request.method == "POST":
        full_name = request.POST.get("full-name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.info(request, "Username already taken!")
            return redirect("/register/")

        if User.objects.filter(email=email).exists():
            messages.info(request, "Email already taken!")
            return redirect("/register/")

        first_name, last_name = process_full_name(full_name)
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password  
        )
        user.save()

        messages.info(request, "Account created Successfully!")
        return redirect("/login")

    return render(request, "register.html")


def logout_user(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("/")