import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Prefetch, Count, Avg, Q, F
from django.http import JsonResponse
from .models import Course, Module, Quiz, Question, QuizAttempt, QuestionResponse, Resource, Category, ResourceRating, ResourceDownload
from .models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout


# Create your views here.
def index(request):
    username = request.user.username
    return render(request, "index.html", {'username':username})


def resources_list(request):
    categories = Category.objects.all()
    resources = Resource.objects.all().order_by('-created_at')
    
    # Filter by category
    category = request.GET.get('category')
    if category and category != 'all':
        resources = resources.filter(category__slug=category)
    
    # Filter by difficulty
    difficulty = request.GET.get('difficulty')
    if difficulty:
        resources = resources.filter(difficulty=difficulty)
    
    # Search functionality
    query = request.GET.get('search')
    if query:
        resources = resources.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
    
    context = {
        'categories': categories,
        'resources': resources,
    }
    return render(request, 'resources.html', context)


def resource_detail(request, slug):
    # Get the resource and increment view counter
    resource = get_object_or_404(Resource, slug=slug)
    Resource.objects.filter(pk=resource.pk).update(views=F('views') + 1)
    
    # Get user's rating if they're logged in
    user_rating = None
    if request.user.is_authenticated:
        user_rating = ResourceRating.objects.filter(
            resource=resource,
            user=request.user
        ).first()
    
    # Get related resources
    related_resources = Resource.objects.filter(
        category=resource.category
    ).exclude(
        id=resource.id
    )[:3]
    
    context = {
        'resource': resource,
        'user_rating': user_rating,
        'related_resources': related_resources,
    }
    return render(request, 'resource_detail.html', context)


@login_required
def download_resource(request, slug):
    resource = get_object_or_404(Resource, slug=slug)
    
    if not resource.is_downloadable:
        return JsonResponse({'error': 'Resource is not downloadable'}, status=400)
    
    # Record the download
    ResourceDownload.objects.create(
        resource=resource,
        user=request.user
    )
    
    return JsonResponse({
        'download_url': resource.file.url,
        'filename': resource.file.name
    })


@login_required
def rate_resource(request, slug):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    # Parse the incoming JSON data
    try:
        data = json.loads(request.body)
        rating = int(data.get('rating', 0))
        comment = data.get('comment', '')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)

    # Check for valid rating
    if not 1 <= rating <= 5:
        return JsonResponse({'error': 'Invalid rating'}, status=400)
    
    # Retrieve the resource object
    resource = get_object_or_404(Resource, slug=slug)
    
    # Create or update the ResourceRating entry
    ResourceRating.objects.update_or_create(
        resource=resource,
        user=request.user,
        defaults={'rating': rating, 'comment': comment}
    )
    
    # Update the resource's average rating
    avg_rating = ResourceRating.objects.filter(resource=resource).aggregate(Avg('rating'))
    resource.rating = avg_rating['rating__avg']
    resource.save()
    
    return JsonResponse({'success': True})


def leaderboard(request):
    username = request.user.username

    return render(request, "leaderboard.html",{'username' : username})


@login_required
def courses(request):
    """
    Display list of all courses with progress for the current user and handle search & category filtering.
    """
    search_query = request.GET.get('search', '')  # Get the search query from the GET parameters
    category_filter = request.GET.get('category', 'all')

    # If a category filter is applied, get the filtered category
    if category_filter != 'all':
        courses = Course.objects.filter(category=category_filter).annotate(
            total_modules=Count('modules'),
            total_quizzes=Count('modules__quizzes'),
            completed_quizzes=Count(
                'modules__quizzes__attempts',
                filter=Q(modules__quizzes__attempts__user=request.user) & Q(modules__quizzes__attempts__completed=True)
            )
        )
    else:
        courses = Course.objects.annotate(
            total_modules=Count('modules'),
            total_quizzes=Count('modules__quizzes'),
            completed_quizzes=Count(
                'modules__quizzes__attempts',
                filter=Q(modules__quizzes__attempts__user=request.user) & Q(modules__quizzes__attempts__completed=True)
            )
        )

    # Apply search filter if a search query is provided
    # if search_query:
    #     courses = courses.filter(
    #         Q(title__icontains=search_query) |  # Adjust this field to match your model's name field
    #         Q(description__icontains=search_query)  # Add other fields you want to search on
    #     )
    
    query = request.GET.get('search')
    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
    

    categories = Course.objects.values('category').distinct()

    # Calculate progress for each course
    for course in courses:
        course.progress = (
            (course.completed_quizzes / course.total_quizzes * 100)
            if course.total_quizzes > 0 else 0
        )
    
    # course.total_modules = course.total_modules


    # Pass courses and the search query to the context
    context = {
        'courses': courses,
        'page_title': 'Available Courses',
        'search_query': search_query,  # So that the search term persists in the form
        'categories': categories,  # Pass the categories for filter buttons

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


@login_required
def quiz_start(request, quiz_id):
    """
    Start a new quiz attempt or continue existing incomplete attempt
    """
    quiz = get_object_or_404(Quiz.objects.select_related('module__course'), id=quiz_id)
    
    # Check for existing incomplete attempt
    attempt = QuizAttempt.objects.filter(
        user=request.user,
        quiz=quiz,
        completed=False
    ).first()
    
    if not attempt:
        # Create new attempt
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz
        )
    
    return redirect('quiz_question', attempt_id=attempt.id)


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