from django.shortcuts import render, redirect
from .models import Task, Project, Comment
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse
import json
from .forms import TaskForm, CommentForm
from django.forms import modelformset_factory
from django.template.loader import render_to_string
from django.db.models import Count

# Create your views here.


def main_view(request):
    """View to display active tasks ordered by their 'order' field.
    Retrieves all tasks that are not marked as done, orders them by the 'order' field, and renders them in the 'act_tasks.html' template.
    
    Returns:
        HttpResponse: A rendered HTML page displaying the active tasks.
    """
    tasks = Task.objects.all().order_by('order')
    comments = Comment.objects.all().order_by('created_at').annotate(comment_count=Count('task_id'))

    if request.method == 'POST':
        form = TaskForm(request.POST)
        com_form = CommentForm(request.POST)
        if form.is_valid():
            task = form.save()
            html = render_to_string('task_item.html', {
                'task_id': task.id,
                'task_title': task.title,
                'task_description': task.description,
                'task_project': task.project,
                'is_done': task.done,
                'task_comments': comments
            })
            return JsonResponse({'status': 'success', 'html': html, 'task_id': task.id})
        if com_form.is_valid():
            print("Comment form is valid")
            comment = com_form.save(commit=False)
            task_id = request.POST.get('task_id')
            print(f"Received comment for task ID: {task_id}")
            comment.task_id = task_id
            comment.save()
            html = render_to_string('task_item.html', {
                'task_id': comment.task.id,
                'task_title': comment.task.title,
                'task_description': comment.task.description,
                'is_done': comment.task.done,
                'task_end_date': comment.task.end_date,
                'task_project': comment.task.project,
                'task_comments': Comment.objects.filter(task=comment.task).order_by('-created_at'),
                'task_order': comment.task.order
            })
            return JsonResponse({'status': 'success', 'html': html, 'task_id': comment.task.id})

            
    else:
        com_form = CommentForm()
        form = TaskForm()

    return render(request, "main.html", {"tasks": tasks, "form": form, "comments": comments, "com_form": com_form})


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
            'task_id': task.id,
            'task_title': task.title,
            'task_description': task.description,
            'is_done': task.done,
            'task_end_date': task.end_date,
            'task_comments': Comment.objects.filter(task=task).order_by('created_at')
        })

        return JsonResponse({'status': 'success', 'html': html, 'task_id': task.id})
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
        data = json.loads(request.body)
        task = Task.objects.get(id=task_id)

        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.done = data.get('done', task.done)
        end_date_str = data.get('end_date')
        
        if end_date_str:
            task.end_date = end_date_str
        project_name = data.get('project')
        if project_name:
            project, created = Project.objects.get_or_create(name=project_name)
            task.project = project

        task.save()

        html = render_to_string('task_item.html', {
            'task_id': task.id,
            'task_title': task.title,
            'task_description': task.description,
            'is_done': task.done,
            'task_end_date': task.end_date,
            'task_project': task.project,
            'task_comments': Comment.objects.filter(task=task).order_by('-created_at'),
            'task_order': task.order
        })

        return JsonResponse({'status': 'success', 'html': html, 'task_id': task.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
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
        task_id = data.get('task_id')
        print(f"Adding comment to task ID: {task_id} with text: {text}")

        task = Task.objects.get(id=task_id)
        comment = Comment.objects.create(text=text, task=task)
        html = render_to_string('task_item.html', {
            'task_id': task.id,
            'task_comments': Comment.objects.filter(task=task).order_by('-created_at'),
        })

        return JsonResponse({'status': 'success', 'html': html, 'task_id': task.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
