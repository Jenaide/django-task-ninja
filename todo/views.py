from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.views import View
from django.shortcuts import redirect
from django.db import transaction


from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .form import PositionForm
from .models import Task

class LoginView(LoginView):
    template_name = 'login.html'
    fields = '__all__'
    redirect_authentication = True

    def get_success_url(self):
        return reverse_lazy('tasks')
    

class RegisterView(FormView):
    template_name = 'register.html'
    form_class = UserCreationForm
    redirect_authentication_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterView, self).form_valid(form)
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterView, self).get(*args, **kwargs)
        

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'task_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['tasks'] = tasks
        context['count'] = context['tasks'].filter(complete=False).count()

        search_field = self.request.GET.get('search-field') or ''
        if search_field:
            context['tasks'] = context['tasks'].filter(title__icontains=search_field)

        context['search_field'] = search_field

        return context
    
class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'task.html'


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'task_form.html'
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreateView, self).form_valid(form)
    
class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = 'task_form.html'
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'task_confirm_delete.html'
    context_object_name = 'tasks'
    success_url = reverse_lazy('tasks')

    def get_queryset(self):
        owner = self.request.user
        return self.model.objects.filter(user=owner)
    
class TasksReorder(View):
    def post(self, request):
        form = PositionForm(request.POST)

        if form.is_valid():
            position_list = form.cleaned_data["position"].split(",")

            with transaction.atomic():
                self.request.user.set_task_order(position_list)

        return redirect(reverse_lazy('tasks'))