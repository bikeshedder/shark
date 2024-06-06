from rest_framework import serializers

from .. import models


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = "__all__"


class TaskTimeEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TaskTimeEntry
        fields = "__all__"
