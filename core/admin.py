from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Lecture, Quiz, Question, AnswerOption, CorrectTextAnswer, Submission, StudentAnswer

# --- Пользователи ---
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Роли', {'fields': ('is_student', 'is_teacher')}),
    )
    list_display = ('username', 'is_student', 'is_teacher')

# --- Тесты и Вопросы ---
class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 1

class CorrectTextAnswerInline(admin.TabularInline):
    model = CorrectTextAnswer
    extra = 1

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0

class QuizAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('title', 'author', 'created_at')

class QuestionAdmin(admin.ModelAdmin):
    # Теперь здесь можно добавлять и варианты ответов, и правильный текстовый ответ
    inlines = [AnswerOptionInline, CorrectTextAnswerInline]
    list_display = ('text', 'quiz', 'question_type', 'score')
    list_filter = ('quiz',)

# --- Результаты ---
class StudentAnswerInline(admin.StackedInline):
    model = StudentAnswer
    extra = 0
    # Делаем поля только для чтения, чтобы админ случайно не изменил ответ студента
    readonly_fields = ('question', 'selected_options', 'text_response', 'image_response') 

class SubmissionAdmin(admin.ModelAdmin):
    inlines = [StudentAnswerInline]
    list_display = ('student', 'quiz', 'total_score', 'is_graded', 'completed_at')
    list_filter = ('is_graded', 'quiz')

# Регистрация всех моделей
admin.site.register(User, CustomUserAdmin)
admin.site.register(Lecture)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Submission, SubmissionAdmin)