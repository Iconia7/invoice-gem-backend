from django.db import models
from licenses.models import ProLicense

class DeviceBackup(models.Model):
    license = models.ForeignKey(ProLicense, on_delete=models.CASCADE, related_name='backups')
    backup_data = models.JSONField(default=dict, help_text="Full export of the Flutter SQLite database as JSON")
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Backup for {self.license.device_id} at {self.created_at}"
