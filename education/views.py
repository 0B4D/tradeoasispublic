from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from .models import Lesson
from .forms import LessonForm

def education(request):
    lessons = Lesson.objects.all()
    print(lessons[0].thumbnail.url)
    return render(request, 'education.html', {'lessons': lessons})

def compound_interest(request):
    return render(request, 'compound_interest.html')

def snp500(request):
    return render(request, 'snp500.html')

def tradeoasis(request):
    return render(request, 'tradeoasis.html')

@user_passes_test(lambda u: u.is_superuser)
def create_lesson(request):
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('education:education')
    else:
        form = LessonForm()
    return render(request, 'create_lesson.html', {'form': form})

def lesson_detail(request, slug):
    lesson = get_object_or_404(Lesson, slug=slug)
    return render(request, 'lesson_detail.html', {'lesson': lesson})

@user_passes_test(lambda u: u.is_superuser)
def delete_lesson(request, slug):
    lesson = get_object_or_404(Lesson, slug=slug)

    lesson.delete()
    messages.success(request, "Lekcija uspješno obrisana.")
    return redirect('education:education')