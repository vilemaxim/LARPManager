from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps 
from django.contrib.auth.models import User
from events.models import Location

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    home_chapter = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=255, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

def home_groups(sender):
    if sender.name == "home":  # Ensures it only runs for this app
        Group.objects.get_or_create(name="Event Administrator")
        Group.objects.get_or_create(name="Tavern Keeper")
        Group.objects.get_or_create(name="Tavern Staff")

def characters_groups(sender):
    if sender.name == "characters":
        rules_marshal_group,_= Group.objects.get_or_create(name="Rules Marshal")
        Character = apps.get_model('characters', 'Characters') 
        content_type = ContentType.objects.get_for_model(Character)
        approval_permission, created = Permission.objects.get_or_create(
            codename='can_approve_character',
            name='Can approve characters',
            content_type=content_type,
        )
        rules_marshal_group.permissions.add(approval_permission)

def tavern(sender):
   if sender.name == "tavern":  # Only create roles for Tavern app
        # Create Tavern Keeper role
        tavern_keeper, _ = Group.objects.get_or_create(name="Tavern Keeper")
        tavern_keeper_permissions = [
            "view_tavernregistration",
        ]
        for perm in tavern_keeper_permissions:
            permission = Permission.objects.filter(codename=perm).first()
            if permission:
                tavern_keeper.permissions.add(permission)

        # Create Tavern Staff role
        Group.objects.get_or_create(name="Tavern Staff")


@receiver(post_migrate)
def setup_roles(sender, **kwargs):
    """Ensure roles exist after migrations."""
    home_groups(sender)
    characters_groups(sender)
    tavern(sender)

