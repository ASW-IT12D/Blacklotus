from rest_framework import serializers
from .models import Issue,Activity

class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'

class ActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Activity
        fields = '__all__'