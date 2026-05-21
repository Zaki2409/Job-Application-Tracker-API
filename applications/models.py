from django.db import models

# Create your models here.
class JobApplication(models.Model):
    # Status choices
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('interviewing', 'Interviewing'),
        ('rejected', 'Rejected'),
        ('offered', 'Offered'),
    ]

    # Fields
    company = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='applied'
    )
    applied_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    # Optional: human-readable representation in admin/console
    def __str__(self):
        return f"{self.role} at {self.company} ({self.status})"