from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

def is_tavern_keeper(user):
    """Check if the user is a Tavern Keeper."""
    return user.groups.filter(name="Tavern Keeper").exists()

