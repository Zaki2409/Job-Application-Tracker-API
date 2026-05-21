from rest_framework import serializers
from .models import JobApplication

class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = '__all__'  # includes all fields: id, company, role, status, applied_date, notes
        # or you can list them explicitly: fields = ['id', 'company', 'role', 'status', 'applied_date', 'notes']