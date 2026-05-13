from django.test import TestCase
from .models import Project, Task
from django.urls import reverse

# Create your tests here.

class ProjectModelTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(name="Test Project")

    def test_project_creation(self):
        self.assertEqual(self.project.name, "Test Project")
        self.assertEqual(str(self.project), "Test Project")

class MainPageModelTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(name="Test Project")
        self.task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            project=self.project,
            order=1
        )

    def test_task_creation(self):
        self.assertEqual(self.task.title, "Test Task")
        self.assertEqual(self.task.description, "Test Description")
        self.assertEqual(self.task.project, self.project)

    def test_task_str(self):
        self.assertEqual(str(self.task), "Test Task")

class MainPageViewTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(name="Test Project")
        self.task1 = Task.objects.create(
            title="Active Task",
            description="Active Task Description",
            project=self.project,
            order=1,
            done=False
        )
        self.task2 = Task.objects.create(
            title="Completed Task",
            description="Completed Task Description",
            project=self.project,
            order=0,
            done=True
        )

    def test_active_tasks_view(self):
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Active Task")
        self.assertContains(response, "Completed Task")