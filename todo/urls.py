from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (TaskListView, TaskDetailView, 
                    TaskCreateView, TaskUpdateView, DeleteView, 
                    LoginView, RegisterView, TasksReorder)

urlpatterns = [

    # Login and registeration urls
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),

    path('', TaskListView.as_view(), name='tasks'),
    path('task/<int:pk>/', TaskDetailView.as_view(), name='task'),
    path('task-create/', TaskCreateView.as_view(), name='task-create'),
    path('task-update/<int:pk>/', TaskUpdateView.as_view(), name='task-update'),
    path('task-delete/<int:pk>/', DeleteView.as_view(), name='task-delete'),
    path('task-reorder/', TasksReorder.as_view(), name='task-reorder'),
]
