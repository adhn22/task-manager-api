from datetime import date

from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'description',
            'status',
            'priority',
            'due_date',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_due_date(self, value):
        if value and value < date.today():
            raise serializers.ValidationError('Due date cannot be in the past.')
        return value

    def validate(self, attrs):
        instance = self.instance
        if instance and instance.status == Task.Status.COMPLETED:
            raise serializers.ValidationError(
                'A completed task cannot be edited.'
            )
        return attrs
