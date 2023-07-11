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

""" sets up a login view that uses a specific HTML template for rendering, 
 includes all fields from the login form, redirects the user after successful authentication, 
 and determines the URL to redirect to after login by using the 'tasks' view"""
class LoginView(LoginView):
    template_name = 'login.html'
    fields = '__all__'
    redirect_authentication = True

    def get_success_url(self):
        # redirects the user back to the tasks page
        return reverse_lazy('tasks')
    

"""sets up a registration view that uses a specific HTML template for rendering, 
 uses the UserCreationForm for user registration, redirects the user after successful registration, 
 logs in the user upon successful registration, and checks if the user is already authenticated before showing the registration form. 
 If the user is already authenticated, they will be redirected to the 'tasks' page"""
class RegisterView(FormView):
    template_name = 'register.html'
    form_class = UserCreationForm
    redirect_authentication_user = True
    success_url = reverse_lazy('tasks')

    # condition checks is the form is valid and saves the user in the database
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterView, self).form_valid(form)
    
    # get method, which is executed when an HTTP GET request is made to the registration view.
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterView, self).get(*args, **kwargs)
        

""" sets up a task list view that requires the user to be logged in. 
It retrieves a list of tasks from the Task model and filters them based on the logged-in user. 
It also provides additional context data such as the count of incomplete tasks and a search functionality that filters tasks based on a search field value. 
The resulting data and context are passed to the 'task_list.html' template for rendering """
class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'task_list.html'

    # method that is responsible for adding additional context data to be passed to the template.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # retrieve the base context data using the super() method
        tasks = context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['tasks'] = tasks
        context['count'] = context['tasks'].filter(complete=False).count()

        search_field = self.request.GET.get('search-field') or ''
        if search_field: # filters it through the base title
            context['tasks'] = context['tasks'].filter(title__icontains=search_field)# icontains search field makes the search case insensitive

        context['search_field'] = search_field

        # returns all the data from the context dictionary
        return context
    

""" sets up a task detail view that requires the user to be logged in. 
It retrieves the details of a specific task from the Task model and makes it available in the template context as tasks. 
The task.html template is used to render the task details on the web page """
class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'task.html'



""" sets up a task creation view that requires the user to be logged in. 
It provides a form with fields for title, description, and completion status. 
After the user submits the form, the task is created and associated with the currently logged-in user. 
Upon successful task creation, the user is redirected to the 'tasks' page """
class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'task_form.html'
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    # condition checks is the form is valid
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreateView, self).form_valid(form)
    

""" sets up a task update view that requires the user to be logged in. 
It provides a form with fields for title, description, and completion status, pre-filled with the existing task data. 
After the user submits the form to update the task, they are redirected to the 'tasks' page upon successful update """
class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = 'task_form.html'
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')


""" sets up a task deletion view that requires the user to be logged in. 
When a user confirms the deletion of a task, a confirmation page is displayed before the task is deleted. 
After the deletion is successful, the user is redirected to the 'tasks' page """
class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'task_confirm_delete.html'
    context_object_name = 'tasks'
    success_url = reverse_lazy('tasks')

    def get_queryset(self):
        owner = self.request.user
        return self.model.objects.filter(user=owner)
    

""" sets up a view that handles the reordering of tasks. 
When a user submits a form containing positions for the tasks, the positions are extracted from the form data. 
Then, a transaction is initiated to update the user's task order in the database based on the positions provided. 
After the reordering is done, the user is redirected to the 'tasks' page """
class TasksReorder(View):
    def post(self, request):
        form = PositionForm(request.POST)

        # condition checks is the form is valid
        if form.is_valid():
            position_list = form.cleaned_data["position"].split(",")

            with transaction.atomic():
                self.request.user.set_task_order(position_list)

        return redirect(reverse_lazy('tasks'))