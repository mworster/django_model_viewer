from django.db import models
import uuid

class SampleModel(models.Model):
    # Primary Key (UUID-based)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Character Fields
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('archived', 'Archived')
    ], default='pending')

    # Integer Field
    priority = models.IntegerField(default=0)

    # Date Fields
    created_at = models.DateTimeField(auto_now_add=True)  # set on create
    updated_at = models.DateTimeField(auto_now=True)      # update on save
    due_date = models.DateField(null=True, blank=True)    # optional

    def __str__(self):
        return f"{self.name} ({self.status})"
