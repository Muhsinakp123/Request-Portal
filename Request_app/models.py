from django.db import models
from django.contrib.auth.models import User
import uuid


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    

    ROLE_CHOICES = (
        ('employee', 'Employee'),
        ('technician', 'Technician'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user} ({self.role})"
    


class MaintenanceRequest(models.Model):
    # -------------------------------
    # CATEGORY CHOICES
    # -------------------------------
    CATEGORY_CHOICES = (
        ('ELECTRICAL', 'Electrical'),
        ('PLUMBING', 'Plumbing'),
        ('HVAC', 'HVAC'),
        ('IT', 'IT'),
        ('OTHER', 'Other'),
    )

    # -------------------------------
    # STATUS CHOICES (match template)
    # -------------------------------
    STATUS_PENDING = 'PENDING'
    STATUS_IN_PROCESS = 'IN_PROCESS'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_IN_PROCESS, 'In Process'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    )

    # -------------------------------
    # FIELDS
    # -------------------------------
    request_id = models.CharField(max_length=40, unique=True, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING  
    )

    created_by = models.ForeignKey(
        User,
        related_name='requests_created',
        on_delete=models.CASCADE
    )

    assigned_to = models.ForeignKey(
        User,
        related_name='requests_assigned',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    resolution_notes = models.TextField(blank=True, null=True)

    # -------------------------------
    # AUTO GENERATE UNIQUE REQUEST ID
    # -------------------------------
    def save(self, *args, **kwargs):
        if not self.request_id:
            self.request_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.request_id} - {self.title}"
