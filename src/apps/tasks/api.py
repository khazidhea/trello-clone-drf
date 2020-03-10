from rest_framework import viewsets, routers, serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()


router = routers.DefaultRouter()
router.register('api/tasks', TaskViewSet)
urlpatterns = router.urls
