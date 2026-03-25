from rest_framework import serializers
from .models import DeviceBackup

class DeviceBackupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceBackup
        fields = ['id', 'backup_data', 'created_at', 'description']
        read_only_fields = ['id', 'created_at']
