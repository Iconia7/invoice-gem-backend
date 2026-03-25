from django.urls import path
from .views import BackupView, BackupListView

urlpatterns = [
    path('', BackupView.as_view(), name='backup-latest'),
    path('list/', BackupListView.as_view(), name='backup-list'),
]
