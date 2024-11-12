from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.CharField(max_length=100)  # e.g., "4 weeks", "2 months"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    icon_class = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)  

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    
    def get_progress(self, user):
        """Calculate user's progress for this course"""
        total_quizzes = Quiz.objects.filter(module__course=self).count()
        if total_quizzes == 0:
            return 0
        completed_quizzes = QuizAttempt.objects.filter(
            quiz__module__course=self,
            user=user,
            completed=True
        ).count()
        return (completed_quizzes / total_quizzes) * 100

class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['course', 'order']  
    
    def __str__(self):
        return f"{self.course.title} - Module {self.order}: {self.title}"

class Quiz(models.Model):
    module = models.ForeignKey(Module, related_name='quizzes', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['module', 'order']
        verbose_name_plural = 'quizzes'
    
    def __str__(self):
        return f"{self.module.title} - Quiz {self.order}: {self.title}"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    options = models.JSONField()  
    explanation = models.TextField(blank=True)  
    order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['quiz', 'order']
    
    def __str__(self):
        return f"Question {self.order} in {self.quiz.title}"

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, related_name='quiz_attempts', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, related_name='attempts', on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username}'s attempt at {self.quiz.title}"

class QuestionResponse(models.Model):
    attempt = models.ForeignKey(QuizAttempt, related_name='responses', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='responses', on_delete=models.CASCADE)
    selected_option = models.JSONField() 
    is_correct = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['question__order']
    
    def __str__(self):
        return f"Response to {self.question} by {self.attempt.user.username}"
    