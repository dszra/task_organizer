from django.shortcuts import render, redirect
from .models import Task, Project, Comment, Subtask, Category
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse
import json
from .forms import TaskForm, CommentForm, SubtaskForm
from django.forms import modelformset_factory
from django.template.loader import render_to_string
from django.db.models import Count
from django.utils import timezone
from django.contrib.auth.decorators import login_required


# Create your views here.

@login_required
def main_view(request):
    """View to display active tasks ordered by their 'order' field.
    Retrieves all tasks that are not marked as done, orders them by the 'order' field, and renders them in the 'act_tasks.html' template.
    
    Returns:
        HttpResponse: A rendered HTML page displaying the active tasks.
    """
    tasks = Task.objects.all().order_by('order').filter(user=request.user)
    comments = Comment.objects.all().order_by('created_at').annotate(comment_count=Count('task_id'))
    subtasks = Subtask.objects.all().order_by('id')
    today = timezone.now().date()
    today_warning1 = today + timezone.timedelta(days=1)
    today_warning2 = today + timezone.timedelta(days=3)

    com_form = CommentForm()
    form = TaskForm()
    sub_form = SubtaskForm()

    return render(request, "main.html", {"tasks": tasks, "form": form, "comments": comments, "com_form": com_form, "subtasks": subtasks, "sub_form": sub_form, "today": today, "today_warning1": today_warning1, "today_warning2": today_warning2})

# Tasks functions
# Task add
@require_POST
@login_required
def add_task(request):
    """View to add a new task based on the received JSON data.
    Expects a JSON payload with the task data, e.g.:
    {
        "title": "Task Title",
        "description": "Task Description",
        "project": "Project Name",
        "done": false
    }
    """
    try:
        data = json.loads(request.body)
        print(data)
        print(f"Received data for new task: {data}")
        title = data.get('title')
        description = data.get('description', '')
        done = data.get('done', False)
        project_name = data.get('project', None)
        project = Project.objects.get(id=project_name) if project_name else None
        category = data.get('category', None)
        own_end_date = data.get('own_end_date')
        user = request.user
        print(f"User: {user}")
        priority = data.get('priority')
        

        task = Task.objects.create(title=title, description=description, project=project, done=done, category=category, own_end_date=own_end_date, user=request.user, priority=priority)
        print(f"Created task with ID: {task.id}")
        html = render_to_string('task_item.html', {
            'task': task,
            'project': task.project,
            'comments': [],
            'subtasks': [],
            'comments_count': task.comments.count(),
            'subtask_count': task.subtasks.count(),
            'com_form': CommentForm(),
            'sub_form': SubtaskForm(),
            'form': TaskForm(),
            'categories': Category.choices,
            'own_end_date': own_end_date,
            'user': user,
            'priority': task.priority,
        })

        return JsonResponse({'status': 'success', 'html': html, 'task_id': task.id, 'user_id': request.user.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# Task order update
@require_POST
def update_order(request):
    """View to update the order of tasks based on the received JSON data.
    Expects a JSON payload with a list of task IDs in the new order, e.g.:
    {
        "order": [3, 1, 2]
    }
    """
    try:
        data = json.loads(request.body)
        new_order_ids = data.get('order', [])

        tasks_dict = {obj.id: obj for obj in Task.objects.filter(id__in=new_order_ids)}

        update_order = []
        for index, task_id in enumerate(new_order_ids, start=1):
            task = tasks_dict.get(int(task_id))
            if task:
                task.order = index
                update_order.append(task)
        Task.objects.bulk_update(update_order, ['order'])

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# Task status update
@require_POST
def update_task_status(request, task_id):
    """View to update the 'done' status of a task based on the received JSON data.
    Expects a JSON payload with the new status, e.g.:
    {
        "done": true
    }
    """
    try:
        data = json.loads(request.body)
        done_status = data.get('done')

        task = Task.objects.get(id=task_id)
        task.done = done_status
        task.save()
        
        html = render_to_string('task_item.html', {
            'task': task,
            'comments': Comment.objects.filter(task=task).order_by('created_at'),
            'subtasks': Subtask.objects.filter(task=task).order_by('id'),
            'comments_count': task.comments.count(),
            'subtask_count': task.subtasks.count(),
            'com_form': CommentForm(),
            'categories': Category.choices,
            'sub_form': SubtaskForm(),
            'form': TaskForm(),
            'own_end_date': task.own_end_date,
            'priority': task.priority,
        })
        

        return JsonResponse({'status': 'success', 'html': html, 'task_id': task_id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
# Task delete
@require_http_methods(["DELETE"])
def delete_task(request, task_id):
    """View to delete a task based on the received task ID.
    Expects a DELETE request with the task ID in the URL.
    """
    try:
        task = Task.objects.get(id=task_id)
        task.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
# Task edit
@require_http_methods(["PATCH"])
def edit_task(request, task_id):
    """View to edit a task based on the received JSON data.
    Expects a JSON payload with the updated task data, e.g.:
    {
        "title": "New Title",
        "description": "New Description",
        "done": true,
        "end_date": "2024-06-30",
        "project": "New Project"
    }
    """
    try:
        # 1. Pobierasz obiekt
        task = Task.objects.get(id=task_id)
        # 2. Ładujesz słownik z JSON-a
        data = json.loads(request.body)
        # 3. Przekazujesz słownik bezpośrednio do formularza z instancją obiektu!
        form = TaskForm(data, instance=task)
        
        if form.is_valid():
            form.save()

            html = render_to_string('task_item.html', {
                "task": task,
                "form": form,
                'comments': Comment.objects.filter(task=task).order_by('-created_at'),
                'subtasks': Subtask.objects.filter(task=task)
            })

            return JsonResponse({'status': 'success', 'html': html, 'task_id': task_id})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# Comment functionality
# Comment add
@require_POST
def add_comment(request):
    """View to add a comment to a task based on the received JSON data.
    Expects a JSON payload with the comment text and task ID, e.g.:
    {
        "text": "This is a comment.",
        "task_id": 1
    }
    """
    try:
        data = json.loads(request.body)
        text = data.get('text')
        task_id = data.get('task.id')
        print(f"Adding comment to task ID: {task_id} with text: {text}")

        task = Task.objects.get(id=task_id)
        comment = Comment.objects.create(text=text, task=task)
        html = render_to_string('comment_view.html', {
            'comment': comment
        })

        return JsonResponse({'status': 'success', 'html': html, 'task.id': task_id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# Subtask functionality
# Subtask done
@require_POST
def subtask_done(request, subtask_id):
    """View to update the 'done' status of a subtask based on the received JSON data.
    Expects a JSON payload with the new status, e.g.:
    {
        "done": true
    }
    """
    try:
        data = json.loads(request.body)
        done_status = data.get('done')

        subtask = Subtask.objects.get(id=subtask_id)
        subtask.done = done_status
        subtask.save()

        html = render_to_string('subtask_view.html', {
                'subtask': subtask,
                'task': subtask.task
            })
        
        return JsonResponse({'status': 'success', "subtask_end_date": subtask.end_date, 'html': html, 'subtask.id': subtask_id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# Subtask add
@require_POST
def add_subtask(request):
    """View to add a subtask to a task based on the received JSON data.
    Expects a JSON payload with the subtask title and parent task ID, e.g.:
    {
        "title": "Subtask Title",
        "task_id": 1
    }
    """
    try:
        print("Received request to add subtask")
        data = json.loads(request.body)
        title = data.get('title')
        description = data.get('description', '')
        task_id = data.get('task.id')
        print(f"Adding subtask with title: {title} to parent task ID: {task_id}")
        task = Task.objects.get(id=task_id)
        print(f"Found parent task with ID: {task_id} for subtask")
        subtask = Subtask.objects.create(title=title, description=description, task=task)
        print(f"Created subtask with ID: {subtask.id} for parent task ID: {task_id}")
        html = render_to_string('subtask_view.html', {
            'task': task,
            'subtask': subtask
        })
        print(f"Rendered HTML for new subtask: {html}")

        return JsonResponse({'status': 'success', 'html': html, 'task.id': task_id, 'subtask.id': subtask.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# Subtask delete
@require_http_methods(["DELETE"])
def delete_subtask(request, subtask_id):
    """View to delete a subtask based on the received subtask ID.
    Expects a DELETE request with the subtask ID in the URL.
    """
    try:
        subtask = Subtask.objects.get(id=subtask_id)
        subtask.delete()
        return JsonResponse({'status': 'success', "task.id": subtask.task_id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)