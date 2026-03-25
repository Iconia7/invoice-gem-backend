from rest_framework import views, status, response, permissions
from .models import DeviceBackup
from .serializers import DeviceBackupSerializer

class BackupView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Upload a new backup"""
        serializer = DeviceBackupSerializer(data=request.data)
        if serializer.is_valid():
            # Check if user has a license
            pro_license = getattr(request.user, 'pro_license', None)
            if not pro_license:
                return response.Response(
                    {"error": "Active Pro license required for cloud backups"},
                    status=status.HTTP_403_FOR_ACCESSIBLE
                )
            
            serializer.save(license=pro_license)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """Retrieve the latest backup"""
        pro_license = getattr(request.user, 'pro_license', None)
        if not pro_license:
            return response.Response(
                {"error": "Active Pro license required"},
                status=status.HTTP_403_FOR_ACCESSIBLE
            )
        
        backup = DeviceBackup.objects.filter(license=pro_license).first()
        if not backup:
            return response.Response({"error": "No backups found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = DeviceBackupSerializer(backup)
        return response.Response(serializer.data)

class BackupListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """List all backup metadata (no data)"""
        pro_license = getattr(request.user, 'pro_license', None)
        if not pro_license:
            return response.Response({"error": "Active Pro license required"}, status=403)
        
        backups = DeviceBackup.objects.filter(license=pro_license)
        # We might want a different serializer without the large backup_data field
        data = [{"id": b.id, "created_at": b.created_at, "description": b.description} for b in backups]
        return response.Response(data)
