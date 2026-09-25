from rest_framework.serializers import ModelSerializer
from .models import Notification
class NotificationSerializer(ModelSerializer):
    class Meta: model = Notification; fields = "__all__"; read_only_fields = ("date_creation",)
