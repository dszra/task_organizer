from django.shortcuts import render, redirect
from .models import Task, Project, Comment, Subtask
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse
import json
from .forms import TaskForm, CommentForm, SubtaskForm
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
    subtasks = Subtask.objects.all().order_by('id')


    if request.method == 'POST':
        form = TaskForm(request.POST)
        com_form = CommentForm(request.POST)
        sub_form = SubtaskForm(request.POST)

        if 'add-task' in request.POST and form.is_valid():
            task = form.save()
            html = render_to_string('task_item.html', {
                'task_id': task.id,
                'task_title': task.title,
                'task_description': task.description,
                'task_project': task.project,
                'is_done': task.done,
                'task_comments': comments,
                'subtask_count': task.subtasks.count(),
                'task_subtasks': subtasks
            })
            return JsonResponse({'status': 'success', 'html': html, 'task_id': task.id})
        if 'add-comment' in request.POST and com_form.is_valid():
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
        
        if 'add-subtask' in request.POST and sub_form.is_valid():
            subtask = sub_form.save(commit=False)
            task_id = request.POST.get('task_id')
            print(f"Received subtask for task ID: {task_id}")
            subtask.parent_task_id = task_id
            subtask.save()
            return redirect('/')

            
    else:
        com_form = CommentForm()
        form = TaskForm()
        sub_form = SubtaskForm()

    return render(request, "main.html", {"tasks": tasks, "form": form, "comments": comments, "com_form": com_form, "subtasks": subtasks, "sub_form": sub_form})


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
            'task_comments': Comment.objects.filter(task=task).order_by('created_at'),
            'task_subtasks': Subtask.objects.filter(parent_task=task).order_by('id'),
            'task_order': task.order,
            'task_project': task.project,
            'comments_count': task.comments.count(),
            'subtask_count': task.subtasks.count(),
            'task_com_form': CommentForm()
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
            'task_order': task.order,
            'task_subtasks': Subtask.objects.filter(task=task)
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
        

        return JsonResponse({'status': 'success', "subtask_end_date": subtask.end_date})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
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
        task_id = data.get('task_id')
        print(f"Adding subtask with title: {title} to parent task ID: {task_id}")
        task = Task.objects.get(id=task_id)
        print(f"Found parent task with ID: {task_id} for subtask")
        subtask = Subtask.objects.create(title=title, description=description, task=task)
        print(f"Created subtask with ID: {subtask.id} for parent task ID: {task_id}")
        html = render_to_string('task_item.html', {
            'task_id': task.id,
            'task_subtasks': Subtask.objects.filter(task=task).order_by('id'),
        })

        return JsonResponse({'status': 'success', 'html': html, 'task_id': task_id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
@require_http_methods(["DELETE"])
def delete_subtask(request, subtask_id):
    """View to delete a subtask based on the received subtask ID.
    Expects a DELETE request with the subtask ID in the URL.
    """
    try:
        subtask = Subtask.objects.get(id=subtask_id)
        subtask.delete()
        return JsonResponse({'status': 'success', "task_id": subtask.task.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)