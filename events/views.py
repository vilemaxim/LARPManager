from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, EventRegistration
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import Group
from django.utils.timezone import now
from django.contrib import messages
from characters.models import Characters

def is_event_admin(user):
    """Check if the user is an Event Administrator."""
    return user.groups.filter(name="Event Administrator").exists()

def event_list(request):
    events = Event.objects.filter(is_active=True).order_by('start_date')
    return render(request, 'events/event_list.html', {'events': events})

@login_required
def event_detail(request, event_id):
    """Show event details and check if the user is registered."""
    event = get_object_or_404(Event, id=event_id)
    registration = None
    registration_status = None
    if request.user.is_authenticated:
        registration = EventRegistration.objects.filter(event=event, user=request.user).first()
        registration_status = registration.approval_status if registration else "Not Registered"

    pending_registrations = EventRegistration.objects.filter(event=event, approval_status="pending")
    approved_not_checked_in = EventRegistration.objects.filter(event=event, approval_status="approved", checked_in=False)
    attendees = EventRegistration.objects.filter(event=event, approval_status="approved", checked_in=True)


    return render(request, 'events/event_detail.html', {
        'event': event,
        'registered': bool(registration),
        'registration': registration,
        'registration_status': registration_status,
        "pending_registrations": pending_registrations,
        "approved_not_checked_in": approved_not_checked_in,
        "attendees": attendees
    })

@login_required
def register_event(request, event_id):
    """Register a user for an event and allow them to select the Tavern Option."""
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == "POST":
        # Get the value of the Tavern Option checkbox
        tavern_option = request.POST.get('tavern_option') == 'on'

        # Create or update the registration
        EventRegistration.objects.update_or_create(
            event=event,
            user=request.user,
            defaults={'tavern_option': tavern_option}
        )
        
        return HttpResponseRedirect(reverse('events:event_detail', args=[event.id]))

    return HttpResponseRedirect(reverse('events:event_list'))

@login_required
@user_passes_test(is_event_admin)
def event_approval_list(request):
    """View for Event Administrators to manage event registrations."""

    if not request.user.groups.filter(name="Event Administrator").exists():
        return redirect("events:event_list")  # Redirect if user is not an admin

    pending_registrations = EventRegistration.objects.filter(approval_status="pending")
    approved_registrations = EventRegistration.objects.filter(approval_status="approved")
    rejected_registrations = EventRegistration.objects.filter(approval_status="rejected")

    return render(request, "events/event_approval_list.html", {
        "pending_registrations": pending_registrations,
        "approved_registrations": approved_registrations,
        "rejected_registrations": rejected_registrations,
    })


def generate_character_number():
    """Generate the next available unique Character Number."""
    last_character = Characters.objects.order_by('-character_number').first()
    return (last_character.character_number + 1) if last_character else 1000 

@login_required
@user_passes_test(is_event_admin)
def event_approval_view(request, registration_id):
    """Approve or reject an event registration."""
    
    registration = get_object_or_404(EventRegistration, id=registration_id)
    character = Characters.objects.filter(user=registration.user).first()  # Get the user's character

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "approve":
            input_character_number = request.POST.get("character_number", "").strip()

            # Validate the input character number (if provided)
            if input_character_number:
                if Characters.objects.filter(character_number=input_character_number).exists():
                    messages.error(request, "Character number already exists. Please choose a different one.")
                    return redirect('event_approval_view', registration_id=registration.id)
                character.character_number = int(input_character_number)
            else:
                if character.character_number is None:  # If not assigned, auto-generate
                    character.character_number = generate_character_number()

            # Save the updates
            character.save()

            registration.approval_status = "approved"
            registration.approved_by = request.user
            registration.rejection_reason = None
            messages.success(request, "Registration approved successfully!")
        elif action == "reject":
            registration.approval_status = "rejected"
            registration.rejection_reason = request.POST.get("rejection_reason", "")
            messages.success(request, "Registration rejected successfully!")
        registration.save()
        return redirect('events:event_approval_list')

    return render(request, 'events/event_approval_view.html', {
        'registration': registration,
         'character': character
    })

@login_required
def start_checkin(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Ensure user is an Event Administrator
    if not is_event_admin(request.user):
        return redirect('event:event_detail', event_id=event.id)

    # Set checkin_start time if it hasn't started
    if not event.checkin_start:
        event.checkin_start = now()
        event.save()

    return redirect('events:event_detail', event_id=event.id)

@login_required
def check_in(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Get the user's event registration
    registration = get_object_or_404(EventRegistration, event=event, user=request.user, approval_status="approved", checked_in=False)
    
    # Get the user's active character
    character = Characters.objects.filter(user=request.user).first() 

    if character:
        # Increase character build by the event's attending_build
        character.unspent_build += event.attending_build
        character.save()

        # Mark the user as checked in
        registration.checked_in = True
        registration.save()

        # Redirect them to edit character screen
        return redirect("characters:edit_character", character_id=character.id)

    return redirect("events:event_detail", event_id=event.id)