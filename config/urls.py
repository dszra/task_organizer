"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from organizer import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.main_view, name='main'),
    path('update_order/', views.update_order, name='update_order'),
    path('update_task_status/<int:task_id>/', views.update_task_status, name='update_task_status'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('edit_task/<int:task_id>/', views.edit_task, name='edit_task'),
    path('add_comment/', views.add_comment, name='add_comment'),
    path('update_subtask_status/<int:subtask_id>/', views.subtask_done, name='update_subtask_status'),
    path('add_subtask/', views.add_subtask, name='add_subtask'),
    path('delete_subtask/<int:subtask_id>/', views.delete_subtask, name='delete_subtask'),
]
