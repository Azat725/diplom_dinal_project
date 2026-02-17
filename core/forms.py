from django import forms
from .models import Quiz, Question, Lecture, AnswerOption, CorrectTextAnswer

# Базовый миксин для стилизации (чтобы не писать widget для каждого поля)
class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class LectureForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['title', 'content']

class QuizForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description']

class QuestionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'image', 'question_type', 'score']

# Форма для вариантов ответа
class AnswerOptionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = AnswerOption
        fields = ['text', 'is_correct']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Checkbox (галочка) в бутстрапе имеет другой класс
        self.fields['is_correct'].widget.attrs.update({'class': 'form-check-input'})

# Форма для правильного текстового ответа
class CorrectTextAnswerForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = CorrectTextAnswer
        fields = ['text_answer']