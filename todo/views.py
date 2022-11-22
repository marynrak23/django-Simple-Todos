from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required



def home(request):
    return render(request, 'todo/home.html')


def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'This user already exists'})
        else:
            return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': 'Password didn`t match'})


@login_required()
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html', {'form': AuthenticationForm(), 'error': 'Username or password didn`t match'})
        else:
            login(request, user)
            return redirect('currenttodos')


@login_required()
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newTodo = form.save(commit=False)
            newTodo.user = request.user
            newTodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html', {'form': TodoForm(),'error': 'Too many symbols in title field'})


@login_required()
def currenttodos(request):
    Todos = Todo.objects.filter(user=request.user, dateCompleted__isnull=True)
    return render(request, 'todo/currenttodos.html', {'todos': Todos})


@login_required()
def completedtodos(request):
    Todos = Todo.objects.filter(user=request.user, dateCompleted__isnull=False).order_by('-dateCompleted')
    return render(request, 'todo/completedtodos.html', {'todos': Todos})


@login_required()
def viewtodo(request, todo_pk):
    valideAccess = False
    currentTodo = get_object_or_404(Todo, pk=todo_pk)
    for item in Todo.objects.filter(user=request.user):
        if item.id == todo_pk:
            valideAccess = True
    if not valideAccess:
        return render(request, 'todo/viewtodo.html', {'errorAccess': 'You trying access not allowed data'})
    if request.method == 'GET' and valideAccess:
        form = TodoForm(instance=currentTodo)
        return render(request, 'todo/viewtodo.html', {'todo': currentTodo, 'form': form})
    else:
        if request.method == 'POST':
            try:
                form = TodoForm(request.POST, instance=currentTodo)
                form.save()
                return redirect('currenttodos')
            except ValueError:
                return render(request, 'todo/viewtodo.html', {'todo':currentTodo,'form': form, 'error': 'Too many symbols in title field'})


@login_required()
def completetodo(request, todo_pk):
    currentTodo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        currentTodo.dateCompleted = timezone.now()
        currentTodo.save()
        return redirect('currenttodos')


@login_required()
def deletetodo(request, todo_pk):
    currentTodo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        currentTodo.delete()
        return redirect('currenttodos')