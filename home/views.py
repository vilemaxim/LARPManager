from django.shortcuts import render, redirect
from django.http import HttpResponse
from events.models import Location
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm


def index(request):

    # Page from the theme 
    return render(request, 'pages/index.html')

def orginal_index(request):
  return render(request, 'pages/orginal-index.html')

@login_required
def edit_profile(request):
    profile = request.user.profile  # Access the user's profile

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_view')  # Redirect to profile view after saving

    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'home/edit_profile.html', {'form': form})

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'home/profile.html', {'profile': request.user.profile})

