from django.db import models
from apps.core.models import BaseModel
from apps.agencies.models import AgencyAwareModel
from apps.users.models import User
from apps.projects.models import Project

class Task(AgencyAwareModel):
    """
    Görev Modeli.
    Projeye bağlı iş parçacıkları.
    """
    STATUS_CHOICES = (
        ('todo', 'Yapılacak'),
        ('in_progress', 'Devam Ediyor'),
        ('review', 'Kontrol'),
        ('done', 'Tamamlandı'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    
    assigned_to = models.ManyToManyField(User, blank=True, related_name='assigned_tasks')
    
    due_date = models.DateTimeField(null=True, blank=True)
    
    # Checklist (JSON olarak tutmak performanslıdır)
    # [{"item": "Lensi temizle", "done": true}, {"item": "Bataryayı şarj et", "done": false}]
    checklist = models.JSONField(default=list, blank=True) 
    
    time_estimate_minutes = models.IntegerField(default=0, help_text="Tahmini süre (dk)")
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')

    def __str__(self):
        return self.title
