from rest_framework import viewsets, routers, serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


router = routers.DefaultRouter()
router.register('api/users', UserViewSet)
urlpatterns = router.urls
