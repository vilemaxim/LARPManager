export const raceSystem = {
    handleRaceChange(event) {
        const raceSelect = event.target;
        const selectedOption = raceSelect.options[raceSelect.selectedIndex];
        const raceId = selectedOption.value;
        
        console.log('Loading race starting affinity for ID:', raceId);
        
        // Fetch race data
        fetch(`/characters/get_race_data/${raceId}/`)
            .then(response => response.json())
            .then(data => {
                // Reset all affinities' racial status
                document.querySelectorAll('.affinity-input').forEach(input => {
                    input.dataset.raceAffinity = 'false';
                    input.min = 0;
                    input.classList.remove('starting-affinity');
                });

                // Set new racial affinity
                if (data.starting_affinity_id) {
                    const affinityInput = document.getElementById(`affinity_${data.starting_affinity_id}`);
                    if (affinityInput) {
                        affinityInput.dataset.raceAffinity = 'true';
                        affinityInput.value = data.starting_affinity_tier;
                        affinityInput.min = data.starting_affinity_tier;
                        affinityInput.classList.add('starting-affinity');
                    }
                }

                // Notify other systems of the race change
                document.dispatchEvent(new CustomEvent('raceUpdated', { 
                    detail: { 
                        raceId,
                        startingAffinityId: data.starting_affinity_id,
                        startingAffinityTier: data.starting_affinity_tier
                    }
                }));
            })
            .catch(error => {
                console.error('Error loading race data:', error);
            });
    },

    initializeRaceListeners() {
        const raceSelect = document.querySelector('select[name="race"]');
        if (raceSelect) {
            raceSelect.addEventListener('change', (event) => this.handleRaceChange(event));
        }
    }
}; 