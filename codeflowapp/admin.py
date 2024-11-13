from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(QuestionResponse)
admin.site.register(QuizAttempt)
admin.site.register(Category)
admin.site.register(Resource)
admin.site.register(ResourceDownload)
admin.site.register(ResourceRating)
