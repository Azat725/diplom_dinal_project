from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField

# 1. Пользователи
class User(AbstractUser):
    is_student = models.BooleanField(default=False, verbose_name="Студент")
    is_teacher = models.BooleanField(default=False, verbose_name="Преподаватель")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

# 2. Лекции
class Lecture(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название лекции")
    content = RichTextField(verbose_name="Текст лекции")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Лекция"
        verbose_name_plural = "Лекции"

# 3. Тесты
class Quiz(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название теста")
    description = models.TextField(blank=True, verbose_name="Описание")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"

# 4. Вопросы
class Question(models.Model):
    TYPE_CHOICES = [
        ('SINGLE', 'Один правильный ответ'),
        ('MULTI', 'Несколько правильных ответов'),
        ('TEXT', 'Ввод слова/числа'),
        ('IMAGE_UPLOAD', 'Ответ картинкой (фото решения)'),
    ]

    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE, verbose_name="Тест")
    text = models.TextField(verbose_name="Текст вопроса")
    image = models.ImageField(upload_to='questions/', blank=True, null=True, verbose_name="Картинка к вопросу")
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='SINGLE', verbose_name="Тип вопроса")
    score = models.IntegerField(default=1, verbose_name="Баллы")

    def __str__(self):
        return self.text[:50]

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

# 5. Варианты ответов (для тестов с выбором)
class AnswerOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE, verbose_name="Вопрос")
    text = models.CharField(max_length=200, verbose_name="Текст ответа")
    is_correct = models.BooleanField(default=False, verbose_name="Правильный?")

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Вариант ответа"
        verbose_name_plural = "Варианты ответов"

# 6. Правильный текстовый ответ (для автопроверки слов)
class CorrectTextAnswer(models.Model):
    question = models.ForeignKey(Question, related_name='correct_text', on_delete=models.CASCADE, verbose_name="Вопрос")
    text_answer = models.CharField(max_length=200, verbose_name="Правильный ответ (слово/число)")

    def __str__(self):
        return self.text_answer
    
    class Meta:
        verbose_name = "Правильный ответ (текст)"
        verbose_name_plural = "Правильные ответы (текст)"

# 7. Результат (Попытка студента)
class Submission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Студент")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, verbose_name="Тест")
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата прохождения")
    total_score = models.FloatField(default=0, verbose_name="Общий балл")
    is_graded = models.BooleanField(default=False, verbose_name="Проверено преподавателем")

    def __str__(self):
        return f"{self.student} - {self.quiz}"

    class Meta:
        verbose_name = "Результат теста"
        verbose_name_plural = "Результаты тестов"

# 8. Ответы студента на конкретные вопросы
class StudentAnswer(models.Model):
    submission = models.ForeignKey(Submission, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    # Поля для хранения ответов
    selected_options = models.ManyToManyField(AnswerOption, blank=True)
    text_response = models.CharField(max_length=200, blank=True, null=True)
    image_response = models.ImageField(upload_to='student_answers/', blank=True, null=True)
    
    score = models.FloatField(default=0)
    
    def __str__(self):
        return f"Ответ на: {self.question}"