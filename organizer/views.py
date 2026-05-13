from django.shortcuts import render, redirect
from .models import Task, Project
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json
from .forms import TaskForm
from django.forms import modelformset_factory
from django.template.loader import render_to_string

# Create your views here.


def main_view(request):
    """View to display active tasks ordered by their 'order' field.
    Retrieves all tasks that are not marked as done, orders them by the 'order' field, and renders them in the 'act_tasks.html' template.
    
    Returns:
        HttpResponse: A rendered HTML page displaying the active tasks.
    """
    TaskFormSet = modelformset_factory(Task, form=TaskForm, extra=0)
    tasks = Task.objects.all().order_by('order')

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            html = render_to_string('task_item.html', {
                'task_id': task.id,
                'task_title': task.title,
                'task_description': task.description,
                'is_done': task.done
            })
            return JsonResponse({'status': 'success', 'html': html, 'task_id': task.id})

            
    else:

        form = TaskForm()


    return render(request, "main.html", {"tasks": tasks, "form": form})



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
            'task_end_date': task.end_date
        })

        return JsonResponse({'status': 'success', 'html': html, 'task_id': task.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
