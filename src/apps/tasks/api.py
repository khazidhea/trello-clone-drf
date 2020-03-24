from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework_extensions.routers import ExtendedSimpleRouter

from src.apps.users.models import User
from .models import Task, Approval
from .services import TaskService


class ApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Approval
        fields = ['approver', 'is_approved']


class ApproverSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class ApproverViewSet(
    NestedViewSetMixin,
    RetrieveModelMixin,
    ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = ApproverSerializer
    queryset = User.objects.all()

    def _get_task_and_user(self, user_id):
        task_id = self.get_parents_query_dict()['tasks_for_approval']
        task = Task.objects.get(id=task_id)
        user = User.objects.get(id=user_id)
        return task, user

    def create(self, request, *args, **kwargs):
        task, user = self._get_task_and_user(request.data['id'])
        task.approvers.add(user)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        task, user = self._get_task_and_user(self.kwargs['pk'])
        task.approvers.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        task = self.get_object()
        approval = TaskService(task).approve(request.user.id)
        return Response(
            ApprovalSerializer(approval).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        TaskService(task).complete(request.user.id)
        return Response(
            self.get_serializer(task).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def changes(self, request, pk=None):
        task = self.get_object()
        TaskService(task).request_changes(request.user.id)
        return Response(
            self.get_serializer(task).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        task = self.get_object()
        TaskService(task).close(request.user.id)
        return Response(
            self.get_serializer(task).data,
            status=status.HTTP_200_OK
        )


router = ExtendedSimpleRouter()
router.register(
    'api/tasks',
    TaskViewSet
).register(
    'approvers',
    ApproverViewSet,
    basename='tasks-approvers',
    parents_query_lookups=['tasks_for_approval']
)

urlpatterns = router.urls
