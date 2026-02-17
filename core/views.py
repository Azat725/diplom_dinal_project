from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Quiz, Lecture, Question, AnswerOption, Submission, StudentAnswer
from .forms import QuizForm, QuestionForm, LectureForm, AnswerOptionForm, CorrectTextAnswerForm

# 1. Вход в систему
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

# 2. Выход
def user_logout(request):
    logout(request)
    return redirect('login')

# 3. Главная страница (доступна только авторизованным)
@login_required(login_url='login')
def index(request):
    # Получаем все тесты и лекции
    quizzes = Quiz.objects.all().order_by('-created_at')
    lectures = Lecture.objects.all().order_by('-created_at')
    
    context = {
        'quizzes': quizzes,
        'lectures': lectures
    }
    return render(request, 'core/index.html', context)

@login_required(login_url='login')
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    # Если студент отправил ответы (нажал кнопку)
    if request.method == 'POST':
        submission = Submission.objects.create(student=request.user, quiz=quiz)
        total_score = 0
        needs_grading = False # Флаг: нужно ли проверять вручную?

        for question in quiz.questions.all():
            # Получаем ответ из формы. Имя поля мы сделаем 'question_ID'
            field_name = f'question_{question.id}'
            
            # Создаем объект ответа студента
            student_answer = StudentAnswer.objects.create(
                submission=submission,
                question=question
            )

            # --- Логика проверки по типам ---
            
            # 1. Один правильный ответ
            if question.question_type == 'SINGLE':
                selected_opt_id = request.POST.get(field_name)
                if selected_opt_id:
                    option = AnswerOption.objects.get(id=selected_opt_id)
                    student_answer.selected_options.add(option)
                    if option.is_correct:
                        student_answer.score = question.score
                        total_score += question.score

            # 2. Несколько правильных ответов
            elif question.question_type == 'MULTI':
                selected_ids = request.POST.getlist(field_name) # getlist для списка
                if selected_ids:
                    # Находим все выбранные опции
                    selected_opts = AnswerOption.objects.filter(id__in=selected_ids)
                    student_answer.selected_options.set(selected_opts)
                    
                    # Проверка: Выбраны ВСЕ правильные и НЕТ неправильных
                    correct_opts = question.options.filter(is_correct=True)
                    # Если количество совпадает и множества ID равны
                    if set(selected_opts) == set(correct_opts):
                         student_answer.score = question.score
                         total_score += question.score

            # 3. Текстовый ответ
            elif question.question_type == 'TEXT':
                text_response = request.POST.get(field_name, '').strip()
                student_answer.text_response = text_response
                # Ищем правильный ответ в базе (предполагаем, что он один)
                correct_answer_obj = question.correct_text.first() 
                if correct_answer_obj:
                    # Сравниваем в нижнем регистре (чтобы "Ответ" и "ответ" были равны)
                    if text_response.lower() == correct_answer_obj.text_answer.lower():
                        student_answer.score = question.score
                        total_score += question.score

            # 4. Загрузка картинки
            elif question.question_type == 'IMAGE_UPLOAD':
                image = request.FILES.get(field_name) # Берем из request.FILES!
                if image:
                    student_answer.image_response = image
                    needs_grading = True # Требуется проверка преподавателя

            student_answer.save()

        # Сохраняем общий результат
        submission.total_score = total_score
        # Если были вопросы с картинками, ставим флаг "Не проверено"
        submission.is_graded = not needs_grading 
        submission.save()

        return redirect('index') # Пока просто редирект на главную

    # Если просто открыли страницу (GET)
    return render(request, 'core/take_quiz.html', {'quiz': quiz})


def lecture_detail(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    return render(request, 'core/lecture_detail.html', {'lecture': lecture})

@login_required(login_url='login')
def student_results(request):
    # Получаем все попытки текущего пользователя, новые сверху
    submissions = Submission.objects.filter(student=request.user).order_by('-completed_at')
    
    return render(request, 'core/results.html', {'submissions': submissions})

def teacher_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_teacher:
            return redirect('index') # Если не учитель - кидаем на главную
        return view_func(request, *args, **kwargs)
    return wrapper

# 1. ГЛАВНАЯ СТРАНИЦА ПРЕПОДАВАТЕЛЯ
@teacher_required
def teacher_dashboard(request):
    # Показываем только ТО, что создал ЭТОТ учитель
    quizzes = Quiz.objects.filter(author=request.user)
    lectures = Lecture.objects.filter(author=request.user)
    
    # Считаем непроверенные работы (где is_graded=False) по тестам этого учителя
    ungraded_count = Submission.objects.filter(quiz__author=request.user, is_graded=False).count()
    
    context = {
        'quizzes': quizzes,
        'lectures': lectures,
        'ungraded_count': ungraded_count
    }
    return render(request, 'core/teacher/dashboard.html', context)

# 2. СОЗДАНИЕ ЛЕКЦИИ
@teacher_required
def create_lecture(request):
    if request.method == 'POST':
        form = LectureForm(request.POST)
        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.author = request.user
            lecture.save()
            return redirect('teacher_dashboard')
    else:
        form = LectureForm()
    return render(request, 'core/teacher/item_form.html', {'form': form, 'title': 'Создать лекцию'})

# 3. СОЗДАНИЕ ТЕСТА
@teacher_required
def create_quiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.author = request.user
            quiz.save()
            # После создания теста кидаем на страницу управления вопросами
            return redirect('manage_quiz', quiz_id=quiz.id)
    else:
        form = QuizForm()
    return render(request, 'core/teacher/item_form.html', {'form': form, 'title': 'Создать тест'})

# 4. УПРАВЛЕНИЕ ВОПРОСАМИ В ТЕСТЕ
@teacher_required
def manage_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, author=request.user)
    return render(request, 'core/teacher/manage_quiz.html', {'quiz': quiz})

# 5. ДОБАВЛЕНИЕ ВОПРОСА (Упрощенная версия)
@teacher_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, author=request.user)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        # Тут мы пока упростим: создаем вопрос, а ответы придется добавлять отдельно
        # Или, для MVP, считаем что учитель создаст вопрос, а потом через админку добавит варианты
        # (Чтобы сделать полноценный конструктор с JS на одной странице - это очень много кода)
        
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            
            # Если это текстовый вопрос, пробуем найти правильный ответ в POST
            if question.question_type == 'TEXT':
                correct_text = request.POST.get('correct_text_answer')
                if correct_text:
                    CorrectTextAnswer.objects.create(question=question, text_answer=correct_text)
            
            # Если это выбор, ищем варианты
            # (Для полноценной реализации тут нужен JS Dynamic Formsets, 
            # но пока сделаем редирект обратно)
            return redirect('manage_quiz', quiz_id=quiz.id)
    else:
        form = QuestionForm()
    
    return render(request, 'core/teacher/add_question.html', {'form': form, 'quiz': quiz})

# 6. СПИСОК НА ПРОВЕРКУ
@teacher_required
def grading_list(request):
    submissions = Submission.objects.filter(quiz__author=request.user, is_graded=False).order_by('completed_at')
    return render(request, 'core/teacher/grading_list.html', {'submissions': submissions})

# 7. ПРОЦЕСС ПРОВЕРКИ
@teacher_required
def grade_submission(request, submission_id):
    sub = get_object_or_404(Submission, id=submission_id)
    
    # Проверка безопасности: учитель может проверять только свои тесты
    if sub.quiz.author != request.user:
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        # Собираем баллы
        total = 0
        for answer in sub.answers.all():
            # Учитель вводит баллы для каждого вопроса вручную или оставляет старые
            score_key = f'score_{answer.id}'
            new_score = request.POST.get(score_key)
            if new_score:
                answer.score = float(new_score)
                answer.save()
            total += answer.score
        
        sub.total_score = total
        sub.is_graded = True
        sub.save()
        return redirect('grading_list')

    return render(request, 'core/teacher/grade_submission.html', {'submission': sub})