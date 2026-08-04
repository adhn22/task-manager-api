from datetime import date, timedelta

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from tasks.models import Task


class TaskModelTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass1234')

    def test_create_task(self):
        task = Task.objects.create(
            title='Test Task', user=self.user
        )
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.status, Task.Status.PENDING)
        self.assertEqual(task.priority, Task.Priority.MEDIUM)
        self.assertIsNone(task.due_date)

    def test_task_str(self):
        task = Task.objects.create(title='My Task', user=self.user)
        self.assertEqual(str(task), 'My Task')


class TaskCRUDTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass1234')
        self.other_user = User.objects.create_user(username='other', password='pass1234')
        self.client.force_authenticate(user=self.user)
        self.list_url = '/api/tasks/'
        self.task = Task.objects.create(
            title='Existing Task',
            description='Description here',
            priority=Task.Priority.HIGH,
            user=self.user,
        )
        self.detail_url = f'/api/tasks/{self.task.id}/'

    def test_list_tasks(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_create_task(self):
        data = {
            'title': 'New Task',
            'description': 'New description',
            'priority': Task.Priority.LOW,
            'due_date': (date.today() + timedelta(days=7)).isoformat(),
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(Task.objects.get(id=response.data['id']).user, self.user)

    def test_retrieve_task(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Existing Task')

    def test_update_task(self):
        data = {'title': 'Updated Task', 'status': Task.Status.IN_PROGRESS}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')

    def test_partial_update_task(self):
        data = {'status': Task.Status.COMPLETED}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.COMPLETED)

    def test_delete_task(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    def test_create_task_missing_title(self):
        response = self.client.post(self.list_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TaskPermissionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass1234')
        self.other_user = User.objects.create_user(username='other', password='pass1234')
        self.other_task = Task.objects.create(
            title='Other Task', user=self.other_user
        )

    def test_cannot_list_other_users_tasks(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_cannot_retrieve_other_users_task(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/tasks/{self.other_task.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_update_other_users_task(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f'/api/tasks/{self.other_task.id}/',
            {'title': 'Hacked'}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_delete_other_users_task(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/tasks/{self.other_task.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TaskValidationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass1234')
        self.client.force_authenticate(user=self.user)

    def test_cannot_set_past_due_date(self):
        data = {
            'title': 'Task with past date',
            'due_date': (date.today() - timedelta(days=1)).isoformat(),
        }
        response = self.client.post('/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_set_future_due_date(self):
        data = {
            'title': 'Task with future date',
            'due_date': (date.today() + timedelta(days=7)).isoformat(),
        }
        response = self.client.post('/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_edit_completed_task(self):
        task = Task.objects.create(
            title='Completed Task',
            status=Task.Status.COMPLETED,
            user=self.user,
        )
        response = self.client.patch(
            f'/api/tasks/{task.id}/',
            {'title': 'Try to edit'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TaskFilterTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass1234')
        self.client.force_authenticate(user=self.user)

        Task.objects.create(title='Pending Low', status=Task.Status.PENDING, priority=Task.Priority.LOW, user=self.user)
        Task.objects.create(title='Pending High', status=Task.Status.PENDING, priority=Task.Priority.HIGH, user=self.user)
        Task.objects.create(title='Completed', status=Task.Status.COMPLETED, priority=Task.Priority.MEDIUM, user=self.user)

    def test_filter_by_status(self):
        response = self.client.get('/api/tasks/', {'status': 'pending'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_filter_by_priority(self):
        response = self.client.get('/api/tasks/', {'priority': 'high'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_combined_filters(self):
        response = self.client.get('/api/tasks/', {'status': 'pending', 'priority': 'low'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
