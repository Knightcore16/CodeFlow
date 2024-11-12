from django.contrib import admin
from .models import Course, Module, Quiz, Question, QuestionResponse, QuizAttempt
# Register your models here.

admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(QuestionResponse)
admin.site.register(QuizAttempt)
