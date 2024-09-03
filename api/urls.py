from django.urls import path
from . import views

urlpatterns = [
    path('tasks/', views.read_tasks, name='read_tasks'),            # GET list of tasks
    path('tasks/<int:pk>/', views.read_task, name='read_task'),     # GET a single task
    path('tasks/create/', views.create_task, name='create_task'),   # POST create a task
    path('tasks/update/<int:pk>/', views.update_task, name='update_task'), # PUT update a task
    path('tasks/delete/<int:pk>/', views.delete_task, name='delete_task'), # DELETE delete a task
]
