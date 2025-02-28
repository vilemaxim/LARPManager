import { skillSystem } from './skillSystem.js';

export const affinitySystem = {
    // Core functionality
    updateAffinityPoints() {
        const totalAffinityDisplay = document.getElementById('total_slotted_cores');
        const startingPointsElement = document.getElementById('starting_character_points');
        
        console.log('Starting points element:', startingPointsElement);
        const startingCharacterPoints = parseInt(startingPointsElement?.dataset.value || '0');
        
        // Calculate minimum affinity points (starting points - 40)
        const totalAffinity = Math.max(0, startingCharacterPoints - 40);
        
        console.log('Calculation details:', {
            startingCharacterPoints,
            totalAffinity,
            formula: `${startingCharacterPoints} - 40 = ${totalAffinity}`
        });
        
        // Update the total display
        if (totalAffinityDisplay) {
            totalAffinityDisplay.textContent = totalAffinity;
            // Update unspent points after total is updated
            this.updateUnspentAffinityPoints();
        } else {
            console.error('Total affinity display element not found');
        }
    },

    applyRaceStartingAffinity(data) {
        const startingAffinityInput = document.querySelector(`#affinity_${data.starting_affinity_id}`);
        if (startingAffinityInput) {
            const startingTier = parseInt(data.starting_affinity_tier, 10);
            startingAffinityInput.value = startingTier;
            startingAffinityInput.min = startingTier;
            startingAffinityInput.classList.add('starting-affinity');
        }
    },

    validateAffinityPoints(input) {
        const currentValue = parseInt(input.value) || 0;
        const minValue = parseInt(input.min) || 0;
        
        // Ensure value isn't below minimum (for starting affinities)
        if (currentValue < minValue) {
            input.value = minValue;
            return;
        }

        // Get total and unspent affinity points
        const totalAffinityDisplay = document.getElementById('total_slotted_cores');
        const totalAffinity = parseInt(totalAffinityDisplay.textContent) || 0;
        
        // Calculate total spent across all affinities
        let totalSpent = 0;
        document.querySelectorAll('.affinity-level').forEach(affinityInput => {
            if (affinityInput !== input) {
                totalSpent += parseInt(affinityInput.value) || 0;
            }
        });
        
        // Check if current value would exceed total available
        if (totalSpent + currentValue > totalAffinity) {
            input.value = totalAffinity - totalSpent;
            console.log(`Adjusted affinity value to ${input.value} due to point limit`);
        }
    },

    createAffinityButtons() {
        console.log('Creating affinity buttons');
        const buttonContainer = document.getElementById('affinity-skill-buttons');
        if (!buttonContainer) {
            console.error('Affinity button container not found');
            return;
        }

        // Clear existing buttons
        buttonContainer.innerHTML = '';

        // Create buttons for each affinity
        document.querySelectorAll('.affinity-input').forEach(input => {
            const affinityId = input.id.replace('affinity_', '');
            const affinityName = input.previousElementSibling.textContent;
            
            // Create the button
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'btn btn-secondary';
            button.dataset.affinityId = affinityId;
            button.setAttribute('data-bs-toggle', 'modal');
            button.setAttribute('data-bs-target', `#addAffinitySkillModal${affinityId}`);
            button.textContent = `${affinityName} Skills`;
            button.disabled = true;

            // Create the modal
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.id = `addAffinitySkillModal${affinityId}`;
            modal.setAttribute('tabindex', '-1');
            modal.setAttribute('aria-labelledby', `addAffinitySkillModal${affinityId}Label`);
            modal.setAttribute('aria-hidden', 'true');
            
            modal.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title" id="addAffinitySkillModal${affinityId}Label">Add ${affinityName} Skill</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div id="affinity-${affinityId}-skills-list">
                                <p>Loading skills...</p>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            `;

            // Add button and modal to the page
            buttonContainer.appendChild(button);
            document.body.appendChild(modal);

            // Add event listener for modal show
            modal.addEventListener('show.bs.modal', () => {
                this.loadAffinitySkills(affinityId);
            });
            
            console.log(`Created button and modal for ${affinityName} (ID: ${affinityId})`);
        });
    },

    loadAffinitySkills(affinityId) {
        console.log(`Loading skills for affinity ID: ${affinityId}`);
        const skillsList = document.getElementById(`affinity-${affinityId}-skills-list`);
        
        // Get the affinity name from the input element
        const affinityInput = document.getElementById(`affinity_${affinityId}`);
        const affinityName = affinityInput.previousElementSibling.textContent;
        
        fetch(`/characters/get_affinity_skills/?affinity=${encodeURIComponent(affinityName)}`)
            .then(response => response.json())
            .then(data => {
                // Use the imported skillSystem instead of window.skillSystem
                skillSystem.createSkillList(
                    data.affinity_skills, 
                    `affinity-${affinityId}-skills-list`, 
                    'affinity'
                );
            })
            .catch(error => {
                console.error('Error loading affinity skills:', error);
                skillsList.innerHTML = '<p>Error loading skills. Please try again.</p>';
            });
    },

    updateAffinityButtons() {
        console.log('Updating affinity buttons');
        // Get all affinity inputs
        const affinityInputs = document.querySelectorAll('.affinity-input');
        
        affinityInputs.forEach(input => {
            const affinityId = input.id.replace('affinity_', '');
            const affinityLevel = parseInt(input.value) || 0;
            const button = document.querySelector(`button[data-affinity-id="${affinityId}"]`);
            
            if (button) {
                if (affinityLevel > 0) {
                    button.style.display = ''; // Show button
                    button.disabled = false;
                    console.log(`Enabling and showing button for affinity ${affinityId} with level ${affinityLevel}`);
                } else {
                    button.style.display = 'none'; // Hide button
                    button.disabled = true;
                    console.log(`Disabling and hiding button for affinity ${affinityId} with level ${affinityLevel}`);
                }
            } else {
                console.log(`No button found for affinity ${affinityId}`);
            }
        });
    },

    handleAffinityChange(input) {
        console.log('Affinity changed:', input.id, 'value:', input.value);
        this.updateAffinityButtons();
        this.updateAffinityPoints();
    },

    // Initialize event listeners
    initializeAffinityListeners() {
        console.log('Initializing affinity system');
        this.createAffinityButtons();
        this.updateAffinityButtons();
        this.updateAffinityPoints();
        
        // Add event listeners for affinity inputs
        document.querySelectorAll('.affinity-input').forEach(input => {
            input.dataset.previousLevel = input.value;
            
            input.addEventListener('change', (e) => {
                this.updateAffinityInput(e.target);
            });
            
            input.addEventListener('input', (e) => {
                this.updateAffinityInput(e.target);
            });
        });

        // Listen for race changes
        document.querySelector('select[name="race"]')?.addEventListener('change', () => {
            this.handleRaceChange();
        });

        // Initial calculation of unspent points
        this.updateUnspentAffinityPoints();
    },

    handleRaceChange() {
        console.log('Starting race change handling');
        
        // Get all affinity inputs
        const affinityInputs = document.querySelectorAll('.affinity-input');
        
        // Find the new racial affinity
        const newRacialAffinity = Array.from(affinityInputs).find(input => 
            input.dataset.raceAffinity === 'true'
        );
        
        if (!newRacialAffinity) {
            console.error('No racial affinity found after race change');
            return;
        }
        
        // Calculate total spent with new racial affinity
        let totalSpent = 0;
        affinityInputs.forEach(input => {
            const level = parseInt(input.value) || 0;
            const costMultiplier = parseFloat(input.dataset.costMultiplier);
            const isRacial = input === newRacialAffinity;
            
            if (level > 0) {
                const cost = this.calculateAffinityCost(level, costMultiplier, isRacial);
                totalSpent += cost;
                console.log('Affinity cost calculation:', {
                    affinity: input.id,
                    level,
                    isRacial,
                    cost,
                    runningTotal: totalSpent
                });
            }
        });

        // Update displays
        const totalAffinityDisplay = document.getElementById('total_slotted_cores');
        const unspentAffinityDisplay = document.getElementById('unspent_slotted_cores');
        
        if (totalAffinityDisplay && unspentAffinityDisplay) {
            const totalAffinity = parseInt(totalAffinityDisplay.textContent) || 0;
            unspentAffinityDisplay.textContent = totalAffinity - totalSpent;
        }

        this.updateAffinityButtons();
        
        // Notify build system of race-related affinity change
        document.dispatchEvent(new CustomEvent('affinityChanged'));
    },

    getSelectIdForFrequency(frequency) {
        const frequencyMap = {
            'Passive': '#passive_skills',
            'passive': '#passive_skills',
            'At Will': '#passive_skills',
            'at will': '#passive_skills',
            'Encounter': '#per_encounter_skills',
            'encounter': '#per_encounter_skills',
            'Bell': '#per_bell_skills',
            'bell': '#per_bell_skills',
            'Day': '#per_day_skills',
            'day': '#per_day_skills',
            'Weekend': '#per_weekend_skills',
            'weekend': '#per_weekend_skills'
        };

        const selectId = frequencyMap[frequency.trim()];
        if (!selectId) {
            console.error('Unknown frequency:', frequency);
        }
        return selectId;
    },

    calculateAffinityCost(level, costMultiplier, isRaceAffinity = false) {
        // If it's level 0, cost is 0
        if (level === 0) return 0;
        
        let totalCost = 0;
        // For race affinity, first level is free
        const startingLevel = isRaceAffinity ? 2 : 1;
        
        // Calculate cumulative cost for all levels
        for (let i = startingLevel; i <= level; i++) {
            totalCost += (i * costMultiplier);
        }
        
        console.log('Cost calculation:', {
            level,
            isRaceAffinity,
            startingLevel,
            costMultiplier,
            totalCost,
            breakdown: `Summing costs from level ${startingLevel} to ${level}`
        });
        
        return totalCost;
    },

    canAffordAffinityLevel(level, costMultiplier, availablePoints) {
        const cost = this.calculateAffinityCost(level, costMultiplier);
        return {
            canAfford: cost <= availablePoints,
            cost: cost
        };
    },

    calculateTotalSpentAffinity() {
        let totalSpent = 0;
        document.querySelectorAll('.affinity-input').forEach(input => {
            const level = parseInt(input.value) || 0;
            const costMultiplier = parseFloat(input.dataset.costMultiplier);
            const isRaceAffinity = input.dataset.raceAffinity === 'true';
            
            console.log('Calculating cost for:', {
                inputId: input.id,
                level,
                costMultiplier,
                isRaceAffinity,
                currentTotal: totalSpent
            });
            
            if (level > 0) {
                const cost = this.calculateAffinityCost(level, costMultiplier, isRaceAffinity);
                totalSpent += cost;
                console.log(`Added cost ${cost} for level ${level}`);
            }
        });
        console.log('Total spent affinity:', totalSpent);
        return totalSpent;
    },

    updateUnspentAffinityPoints() {
        const totalAffinityDisplay = document.getElementById('total_slotted_cores');
        const unspentAffinityDisplay = document.getElementById('unspent_slotted_cores');
        
        const totalAffinity = parseInt(totalAffinityDisplay.textContent) || 0;
        const totalSpent = this.calculateTotalSpentAffinity();
        const unspentAffinity = totalAffinity - totalSpent;

        console.log('Affinity Points Calculation:', {
            totalAffinityText: totalAffinityDisplay.textContent,
            totalAffinity,
            totalSpent,
            unspentAffinity
        });

        if (unspentAffinityDisplay) {
            unspentAffinityDisplay.textContent = Math.max(0, unspentAffinity);
        }

        return unspentAffinity;
    },

    updateAffinityInput(input) {
        const affinityId = input.id.replace('affinity_', '');
        const costMultiplier = parseFloat(input.dataset.costMultiplier);
        const isRaceAffinity = input.dataset.raceAffinity === 'true';
        const newLevel = parseInt(input.value) || 0;
        const oldLevel = parseInt(input.dataset.previousLevel) || 0;
        
        // Basic validation
        if (newLevel > 6) {
            input.value = oldLevel;
            alert('Maximum affinity level is 6');
            return;
        }
        
        if (newLevel < 0 || (isRaceAffinity && newLevel < 1)) {
            input.value = isRaceAffinity ? 1 : 0;
            alert(isRaceAffinity ? 'Race affinity cannot be reduced below 1' : 'Minimum affinity level is 0');
            return;
        }

        // Calculate cost difference
        const newCost = this.calculateAffinityCost(newLevel, costMultiplier, isRaceAffinity);
        const oldCost = this.calculateAffinityCost(oldLevel, costMultiplier, isRaceAffinity);
        const costDifference = newCost - oldCost;
        
        // Calculate available points
        const totalPoints = parseInt(document.getElementById('total_slotted_cores').textContent) || 0;
        const currentInput = input.value;
        input.value = oldLevel;  // Temporarily restore old value
        const spentWithoutChange = this.calculateTotalSpentAffinity();
        input.value = currentInput;  // Restore new value
        const availablePoints = totalPoints - spentWithoutChange;
        
        console.log('Affinity change analysis:', {
            affinity: affinityId,
            oldLevel,
            newLevel,
            oldCost,
            newCost,
            costDifference,
            totalPoints,
            spentWithoutChange,
            availablePoints
        });

        // Check if affordable
        if (costDifference > availablePoints) {
            input.value = oldLevel;
            alert(`Not enough affinity points available. Need ${costDifference} points, but only have ${availablePoints} available.`);
            return;
        }

        // Update if affordable
        input.dataset.previousLevel = newLevel;
        this.updateUnspentAffinityPoints();
        this.updateAffinityButtons();

        // Notify build system of affinity change
        document.dispatchEvent(new CustomEvent('affinityChanged'));
    }
}; 