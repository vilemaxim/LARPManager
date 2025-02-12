from django.db import models
from django.contrib.auth.models import User

class Location(models.Model):
    name = models.CharField(max_length=200, unique=True)
    address = models.TextField()

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='events')
    starting_character_points = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    is_active = models.BooleanField(default=True)
    attending_build = models.PositiveIntegerField(default=4)
    traveling_attending_build = models.PositiveIntegerField(default=2)
    max_monster_cores = models.PositiveIntegerField(default=4)
    checkin_start = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

class EventRegistration(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Approval"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    has_paid = models.BooleanField(default=False)
    approval_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_registrations")
    rejection_reason = models.TextField(blank=True, null=True)
    tavern_option = models.BooleanField(default=False, help_text="Does the user plan to pay for food at the tavern?")
    checked_in = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.user.username} registered for {self.event.name} ({self.approval_status})"
