from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.db import transaction, connection, models
from .models import Characters, ExtraEssences, CultivatorTier, CharactersAffinities, CharacterAffinitySkill
from events.models import Event
from .forms import CharacterCreationForm
from cultivator_rules.models import Affinity, CommonSkill, RaceSkill, CultivatorTier, AffinitySkill, Essence, Race
import json
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas


@login_required
def create_or_edit_character_view(request, character_id=None):
    with transaction.atomic():
        character = None
        existing_affinities = {}
        
        if character_id:
            character = get_object_or_404(Characters, id=character_id, user=request.user)

        if request.method == 'POST':
            # Debug logging
            print("Raw POST data:", request.POST)
            print("All POST keys:", list(request.POST.keys()))
            print("Skill levels:", [k for k in request.POST.keys() if k.startswith('skill_level_')])
            
            form = CharacterCreationForm(request.POST, instance=character)

            if form.is_valid():
                character = form.save(commit=False)
                character.user = request.user
                character.save()

                # Get Starting Event and Calculate Starting Build
                if character.starting_event:
                    starting_event = character.starting_event
                    character.starting_build = starting_event.starting_character_points
                    character.total_build = starting_event.starting_character_points
                else:
                    character.starting_build = 0

                # Set Cultivator Tier
                cultivator_tier = CultivatorTier.objects.filter(
                    build_low__lte=character.starting_build,
                    build_high__gte=character.starting_build
                ).first()
                character.cultivator_tier = cultivator_tier
    

                # Save Essence
                essence_value = int(request.POST.get('essence', 5))
                base_essence = 5
                extra_essence = max(0, essence_value - base_essence)

                essence_record, created = ExtraEssences.objects.get_or_create(
                    character=character,
                    cultivator_tier=cultivator_tier,
                    defaults={'extra_essence': extra_essence}
                )

                if not created:
                    essence_record.extra_essence = extra_essence
                    essence_record.save()

                # Calculate Armor (Set to 0 for now, modify logic later if needed)
                character.armor = 0

                # Calculate Unspent Affinity (Modify this logic when needed)
                character.unspent_affinity = 0

                # Calculate Unspent Affinity
                total_spent_affinity = 0

                # Step 1: Clear out any existing affinities to prevent duplicates
                #character.affinity_levels.all().delete()  # 🔥 Removes old affinities

                for affinity in Affinity.objects.all():
                    affinity_level = int(request.POST.get(f"affinity_{affinity.id}", 0))
                
                    # Ensure race's starting affinity cannot be lowered
                    if character.race and character.race.starting_affinity == affinity:
                        affinity_level = max(affinity_level, character.race.starting_affinity_tier)

                    # 🛠 DEBUG LOGGING

                    if affinity_level > 0:
                        # Step 2: Create or Update the Affinity Record
                        char_aff, created = CharactersAffinities.objects.update_or_create(
                            character=character,
                            affinity=affinity,
                            defaults={'level': affinity_level, 'cultivator_tier': cultivator_tier}
                        )

                        # Step 3: Explicitly Add to ManyToManyField
                        character.affinities.add(affinity)  

                    
                        total_spent_affinity += affinity_level  # Track total spent affinity points

                # Default affinity pool (Can be modified as per game rules)
                max_affinity_points = 5  # Default amount of affinity points players start with
                character.unspent_affinity = max(0, max_affinity_points - total_spent_affinity)

                # Step 4: Explicitly Save the Character to Ensure the Changes Persist
                character.save()
 
                # Add this debug print
                print("Received skills:", {
                    'common_skills': request.POST.getlist('common_skills'),
                    'race_skills': request.POST.getlist('race_skills'),
                    'affinity_skills': request.POST.getlist('affinity_skills')
                })

                # Debug print the POST data
                print("POST data:", request.POST)

                # Get all affinity skills from the POST data
                affinity_skill_ids = request.POST.getlist('affinity_skills')
                print(f"Found affinity skills: {affinity_skill_ids}")

                # Get existing skills
                existing_skills = {
                    cas.affinity_skill_id: cas 
                    for cas in character.character_affinity_skills.all()
                }

                # Update or create skills
                for skill_id in affinity_skill_ids:
                    if skill_id != 'placeholder':
                        level = int(request.POST.get(f'skill_level_{skill_id}', 1))
                        print(f"Processing skill {skill_id} with level {level}")
                        
                        try:
                            if skill_id in existing_skills:
                                # Update existing skill
                                cas = existing_skills[skill_id]
                                cas.level = level
                                cas.save()
                                print(f"Updated skill {cas.affinity_skill.name} to level {level}")
                                del existing_skills[skill_id]
                            else:
                                # Create new skill
                                skill = AffinitySkill.objects.get(id=skill_id)
                                CharacterAffinitySkill.objects.create(
                                    character=character,
                                    affinity_skill=skill,
                                    level=level,
                                    cultivator_tier=character.cultivator_tier
                                )
                                print(f"Created skill {skill.name} with level {level}")
                        except AffinitySkill.DoesNotExist:
                            print(f"Could not find affinity skill with ID {skill_id}")

                # Delete any remaining old skills
                for cas in existing_skills.values():
                    print(f"Deleting removed skill {cas.affinity_skill.name}")
                    cas.delete()

                # Verify final state
                saved_skills = character.character_affinity_skills.all()
                print("Saved skills:", [(s.affinity_skill.name, s.level) for s in saved_skills])

                # Handle common and race skills
                character.common_skills.set(CommonSkill.objects.filter(id__in=request.POST.getlist('common_skills')))
                character.race_skills.set(RaceSkill.objects.filter(id__in=request.POST.getlist('race_skills')))

                
                character.save()
                
                # Add debug logging
                if character:
                    print("Loading skills for character:", character.id)
                    for char_skill in character.character_affinity_skills.all():
                        print(f"Found skill: {char_skill.affinity_skill.name} (Level: {char_skill.level})")

                existing_skills = {
                    'passive': [],
                    'encounter': [],
                    'bell': [],
                    'day': [],
                    'weekend': []
                }

                if character:
                    print(f"Loading skills for character {character.id}")
                    # Load affinity skills with levels using the through model
                    for char_skill in character.character_affinity_skills.select_related('affinity_skill').all():
                        skill = char_skill.affinity_skill
                        print(f"Found skill: {skill.name} (Level: {char_skill.level})")
                        print(f"Skill frequency: '{skill.frequency}'")  # Debug the frequency value
                        
                        skill_data = {
                            'id': skill.id,
                            'name': skill.name,
                            'build': skill.build,
                            'frequency': str(skill.frequency),  # Convert to string
                            'level': char_skill.level,
                            'max_time_can_buy': skill.max_time_can_buy,
                            'description': skill.description,
                            'affinity': skill.affinity.name if skill.affinity else 'N/A'
                        }
                        
                        # Add to appropriate frequency list with more flexible matching
                        frequency = str(skill.frequency).lower()
                        print(f"Normalized frequency: '{frequency}'")  # Debug the normalized frequency
                        
                        if any(f in frequency for f in ['passive', 'at will', 'n/a']):
                            print("Adding to passive list")
                            existing_skills['passive'].append(skill_data)
                        elif 'encounter' in frequency:
                            print("Adding to encounter list")
                            existing_skills['encounter'].append(skill_data)
                        elif 'bell' in frequency:
                            print("Adding to bell list")
                            existing_skills['bell'].append(skill_data)
                        elif 'daily' in frequency or 'day' in frequency:
                            print("Adding to day list")
                            existing_skills['day'].append(skill_data)
                        elif 'weekend' in frequency:
                            print("Adding to weekend list")
                            existing_skills['weekend'].append(skill_data)
                        else:
                            print(f"WARNING: Skill {skill.name} has unknown frequency: {frequency}")
                            # Default to passive if frequency is unknown
                            existing_skills['passive'].append(skill_data)

                    print("Existing skills data:", existing_skills)

                character_affinities = {}
                if character:
                    character_affinities = {a.affinity.id: a.level for a in character.affinity_levels.all()}

                existing_essence = ExtraEssences.objects.filter(
                    character=character, 
                    cultivator_tier=character.cultivator_tier
                ).first()

                # Fetch total slotted cores
                total_slotted_cores = 0
                unspent_slotted_cores = 0

                if character:
                    total_slotted_cores = character.slotted_affinities.aggregate(
                        models.Sum('slotted_affinity_total')
                    )['slotted_affinity_total__sum'] or 0

                    unspent_slotted_cores = total_slotted_cores

                return render(request, 'characters/create_character.html', {
                    'form': form,
                    'character': character,
                    'username': request.user.username,
                    'affinities': Affinity.objects.order_by("name"),
                    'essence_limits': Essence.objects.first(),
                    'existing_essence': 5 + (existing_essence.extra_essence) if existing_essence else 5,
                    'max_essence': 5 + (Essence.objects.first().max_extra_essence_per_tier if Essence.objects.exists() else 0),
                    'character_affinities': character_affinities,
                    'total_slotted_cores': total_slotted_cores,
                    'unspent_slotted_cores': unspent_slotted_cores,
                    'existing_skills': existing_skills,
                    'starting_character_points': character.starting_event.starting_character_points if character and character.starting_event else 0,
                })
            else:
                print("❌ Form is invalid:", form.errors)
        else:
            form = CharacterCreationForm(instance=character)
            
            # Prepare existing skills data
            existing_skills = {
                'passive': [],
                'encounter': [],
                'bell': [],
                'day': [],
                'weekend': []
            }

            if character:
                print(f"Loading skills for character {character.id}")
                # Load affinity skills with levels using the through model
                for char_skill in character.character_affinity_skills.select_related('affinity_skill').all():
                    skill = char_skill.affinity_skill
                    print(f"Found skill: {skill.name} (Level: {char_skill.level})")
                    print(f"Skill frequency: '{skill.frequency}'")  # Debug the frequency value
                    
                    skill_data = {
                        'id': skill.id,
                        'name': skill.name,
                        'build': skill.build,
                        'frequency': str(skill.frequency),  # Convert to string
                        'level': char_skill.level,
                        'max_time_can_buy': skill.max_time_can_buy,
                        'description': skill.description,
                        'affinity': skill.affinity.name if skill.affinity else 'N/A'
                    }
                    
                    # Add to appropriate frequency list with more flexible matching
                    frequency = str(skill.frequency).lower()
                    print(f"Normalized frequency: '{frequency}'")  # Debug the normalized frequency
                    
                    if any(f in frequency for f in ['passive', 'at will', 'n/a']):
                        print("Adding to passive list")
                        existing_skills['passive'].append(skill_data)
                    elif 'encounter' in frequency:
                        print("Adding to encounter list")
                        existing_skills['encounter'].append(skill_data)
                    elif 'bell' in frequency:
                        print("Adding to bell list")
                        existing_skills['bell'].append(skill_data)
                    elif 'daily' in frequency or 'day' in frequency:
                        print("Adding to day list")
                        existing_skills['day'].append(skill_data)
                    elif 'weekend' in frequency:
                        print("Adding to weekend list")
                        existing_skills['weekend'].append(skill_data)
                    else:
                        print(f"WARNING: Skill {skill.name} has unknown frequency: {frequency}")
                        # Default to passive if frequency is unknown
                        existing_skills['passive'].append(skill_data)

                print("Existing skills data:", existing_skills)

            character_affinities = {}
            if character:
                character_affinities = {a.affinity.id: a.level for a in character.affinity_levels.all()}

            existing_essence = ExtraEssences.objects.filter(
                character=character, 
                cultivator_tier=character.cultivator_tier
            ).first()

            # Fetch total slotted cores
            total_slotted_cores = 0
            unspent_slotted_cores = 0

            if character:
                total_slotted_cores = character.slotted_affinities.aggregate(
                    models.Sum('slotted_affinity_total')
                )['slotted_affinity_total__sum'] or 0

                unspent_slotted_cores = total_slotted_cores

            return render(request, 'characters/create_character.html', {
                'form': form,
                'character': character,
                'username': request.user.username,
                'affinities': Affinity.objects.order_by("name"),
                'essence_limits': Essence.objects.first(),
                'existing_essence': 5 + (existing_essence.extra_essence) if existing_essence else 5,
                'max_essence': 5 + (Essence.objects.first().max_extra_essence_per_tier if Essence.objects.exists() else 0),
                'character_affinities': character_affinities,
                'total_slotted_cores': total_slotted_cores,
                'unspent_slotted_cores': unspent_slotted_cores,
                'existing_skills': existing_skills,
                'starting_character_points': character.starting_event.starting_character_points if character and character.starting_event else 0,
            })

@login_required
def character_list_view(request):
    """Display all characters belonging to the logged-in user."""
    characters = Characters.objects.filter(user=request.user).order_by("-created_at")

    return render(request, 'characters/character_view.html', {
        'characters': characters,
    })

def is_rules_marshal(user):
    """Check if the user is a Rules Marshal."""
    return user.groups.filter(name='Rules Marshal').exists()

@login_required
def character_approval_list(request):
    # Ensure only rules marshals can access
    if not is_rules_marshal(request.user):
        return redirect('characters:character_list')

    # Fetch characters based on approval status
    pending_characters = Characters.objects.filter(approval_status="pending")
    approved_characters = Characters.objects.filter(approval_status="approved")

    # # Debugging output
    # print("✅ Pending characters:", pending_characters)
    # print("✅ Approved characters:", approved_characters)

    return render(request, 'characters/approval_list.html', {
        'pending_characters': pending_characters,
        'approved_characters': approved_characters,
    })

@login_required
def character_approval_view(request, character_id):
    """View a character and approve or reject it."""
    if not is_rules_marshal(request.user):
        return redirect('characters:character_list')

    character = get_object_or_404(Characters, id=character_id)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "approve":
            character.approval_status = "approved"
            character.approval_date = now()
            character.approved_by = request.user
            character.rejection_note = None
        elif action == "reject":
            character.approval_status = "rejected"
            character.rejection_note = request.POST.get("rejection_note", "")
        character.save()
        return redirect('characters:approval_list')

    return render(request, 'characters/approval_view.html', {'character': character})

def get_common_skills(request):
    """Fetch all available common skills."""
    # Check if it's an AJAX request
    if request.method == "GET":
        common_skills = CommonSkill.objects.all()
        data = [
            {
                'id': skill.id,
                'name': skill.name,
                'description': skill.description,
                'frequency': skill.frequency.name if skill.frequency else "N/A",
                'duration': skill.duration.name if skill.duration else "N/A",
                'build': skill.build,
            }
            for skill in common_skills
        ]
        return JsonResponse({'common_skills': data}, safe=False)

    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)

def get_race_skills(request):
    if request.method == 'GET':
        race_id = request.GET.get('race')
        if not race_id:
            return JsonResponse({"error": "No race specified"}, status=400)

        try:
            race = Race.objects.get(id=race_id)
            race_skills = RaceSkill.objects.filter(race=race)
            
            data = {
                "race_skills": [
                    {
                        'id': skill.id,
                        'name': skill.name,
                        'description': skill.description,
                        'build': skill.build,
                        'frequency': skill.frequency.name if skill.frequency else "N/A",
                        'max_time_can_buy': 1,  # Default to 1 for race skills
                    }
                    for skill in race_skills
                ]
            }
            return JsonResponse(data)
            
        except Race.DoesNotExist:
            return JsonResponse({"error": "Race not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

def get_race_starting_affinity(request):
    """
    Fetch the starting affinity and tier for a selected race.
    """
    if request.method == 'GET':
        race_id = request.GET.get('race_id')
        if not race_id:
            return JsonResponse({'error': 'Race ID is required'}, status=400)

        # Fetch the race and its starting affinity
        race = get_object_or_404(Race, id=race_id)
        data = {
            'starting_affinity_id': race.starting_affinity.id,
            'starting_affinity_name': race.starting_affinity.name,
            'starting_affinity_tier': race.starting_affinity_tier,
        }

        return JsonResponse(data)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def get_event_details(request):
    """Fetch event details including Starting Points and Cultivator Tier."""
    if request.method == "GET":
        event_id = request.GET.get('event_id')  # Get the event ID

        if not event_id:
            return JsonResponse({'error': 'Event ID is required'}, status=400)

        try:
            event = Event.objects.get(id=event_id)
            starting_points = event.starting_character_points
            cultivator_tier = CultivatorTier.objects.filter(
                build_low__lte=starting_points,
                build_high__gte=starting_points
            ).first()

            return JsonResponse({
                'starting_points': starting_points,
                'cultivator_tier': cultivator_tier.name if cultivator_tier else "N/A"
            })
        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def get_affinity_skills(request):
    if request.method == 'GET':
        # Get the affinity name from the request
        affinity_name = request.GET.get('affinity')

        # Fetch the related Affinity object based on the name
        affinity = get_object_or_404(Affinity, name=affinity_name)

        # Filter AffinitySkill by the related Affinity object
        affinity_skills = AffinitySkill.objects.filter(affinity=affinity)
        data = [
            {
                'id': skill.id,
                'name': skill.name,
                'description': skill.description,
                'build': skill.build,
                'frequency': skill.frequency.name if skill.frequency else "N/A",
                'max_time_can_buy': skill.max_time_can_buy,
                'affinity_id': affinity.id,
            }
            for skill in affinity_skills
        ]


        # Return the skills as JSON
        return JsonResponse({"affinity_skills": data, "affinity_id": affinity.id}, safe=False)
    
    # If the request method is not GET, return an error response
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def add_skill(request):
    if request.method == "POST":
        try:
            # Parse the request body
            data = json.loads(request.body)
            skill_id = data.get('skill_id')
            skill_type = data.get('skill_type')  # e.g., 'common', 'race', 'affinity'
            character_id = data.get('character_id')  # ID of the character being updated

            if not skill_id or not skill_type or not character_id:
                return JsonResponse({"error": "Invalid request. Missing required parameters."}, status=400)

            # Get the character
            from .models import Characters, CharacterCommonSkill, CharacterRacialSkill, CharacterAffinitySkill
            character = Characters.objects.get(id=character_id)

            # Handle different skill types
            if skill_type == 'common':
                from cultivator_rules.models import CommonSkill
                skill = CommonSkill.objects.get(id=skill_id)
                CharacterCommonSkill.objects.create(character=character, common_skill=skill)
            elif skill_type == 'race':
                from cultivator_rules.models import RaceSkill
                skill = RaceSkill.objects.get(id=skill_id)
                CharacterRacialSkill.objects.create(character=character, racial_skill=skill)
            elif skill_type == 'affinity':
                from cultivator_rules.models import AffinitySkill
                skill = AffinitySkill.objects.get(id=skill_id)
                CharacterAffinitySkill.objects.create(character=character, affinity_skill=skill)
            else:
                return JsonResponse({"error": "Invalid skill type."}, status=400)

            # Return success response
            return JsonResponse({"success": True, "message": f"{skill.name} added to character."})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=400)

@login_required
def generate_character_sheet(request, character_id):
    """Generate a character sheet PDF."""
    character = get_object_or_404(Characters, id=character_id, user=request.user)

    # Create PDF Response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{character.name}_sheet.pdf"'

    # Create a PDF object
    pdf = canvas.Canvas(response, pagesize=landscape(letter))
    width, height = landscape(letter)


    # Set Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(250, height - 50, f"Character Sheet: {character.name}")

    pdf.line(160, height - 60, width - 50, height - 60)

    # Logo
    logo_path = "static/assets/images/logo.png"
    pdf.drawImage(logo_path, 50, height - 100, width=100, height=100, mask='auto')


    # Character Details
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, height - 100, f"Player: {character.user.username}")
    pdf.drawString(50, height - 120, f"Race: {character.race}")
    pdf.drawString(50, height - 140, f"Cultivator Tier: {character.cultivator_tier.name}")
    pdf.drawString(50, height - 160, f"Starting Build: {character.starting_build}")
    pdf.drawString(50, height - 180, f"Unspent Build: {character.unspent_build}")
    
    pdf.setFont("Helvetica", 16)
    total_essence = 5+ (character.extra_essences.aggregate(models.Sum('extra_essence'))['extra_essence__sum'] or 0)
    pdf.drawString(500, height - 100, f"Essence: {total_essence}")
    pdf.rect( 495, height - 120, 150, 50, stroke=1, fill=0)
    
    pdf.drawString(500, height - 155, f"Armor: {character.armor}")
    pdf.rect( 495, height - 170, 150, 50, stroke=1, fill=0)


    # Affinities
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, height - 240, "Affinities:")
    pdf.setFont("Helvetica", 12)
    y_position = height - 260

    for affinity in character.affinity_levels.all():
        pdf.drawString(70, y_position, f"{affinity.affinity.name}: Tier {affinity.level}")
        y_position -= 20

    # Skills
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y_position - 20, "Skills:")
    pdf.setFont("Helvetica", 12)
    y_position -= 40

    for skill in character.affinity_skills.all():
        pdf.drawString(70, y_position, f"{skill.affinity_skill.name} (Level {skill.level})")
        y_position -= 20

    for skill in character.common_skills.all():
        pdf.drawString(70, y_position, f"{skill.name}")
        y_position -= 20

    for skill in character.race_skills.all():
        pdf.drawString(70, y_position, f"{skill.name}")
        y_position -= 20

    # Finish and Save
    pdf.showPage()
    pdf.save()
    
    return response