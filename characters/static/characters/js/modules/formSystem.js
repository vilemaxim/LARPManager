export const formSystem = {
    // Core functionality
    submitCharacterForm(form) {
        console.log("Custom submit function called");
        
        // Add hidden inputs for affinity values
        const totalAffinity = document.getElementById('total_slotted_cores').textContent;
        const unspentAffinity = document.getElementById('unspent_slotted_cores').textContent;
        
        // Create and append hidden inputs
        const totalAffinityInput = document.createElement('input');
        totalAffinityInput.type = 'hidden';
        totalAffinityInput.name = 'total_affinity';
        totalAffinityInput.value = totalAffinity;
        form.appendChild(totalAffinityInput);
        
        const unspentAffinityInput = document.createElement('input');
        unspentAffinityInput.type = 'hidden';
        unspentAffinityInput.name = 'unspent_affinity';
        unspentAffinityInput.value = unspentAffinity;
        form.appendChild(unspentAffinityInput);
        
        // Validate form before submission
        if (!this.validateForm(form)) {
            return false;
        }

        // Log the final values
        const formData = new FormData(form);
        console.log('Form data before submission:');
        for (let [key, value] of formData.entries()) {
            console.log(`${key}: ${value}`);
        }
        
        return true;
    },

    validateForm(form) {
        // Check if a race is selected
        const raceSelect = form.querySelector('#id_race');
        if (!raceSelect || !raceSelect.value) {
            alert('Please select a race.');
            return false;
        }

        // Check if name is provided
        const nameInput = form.querySelector('input[name="name"]');
        if (!nameInput || !nameInput.value.trim()) {
            alert('Please enter a character name.');
            return false;
        }

        // Check if there are unspent build points
        const unspentBuild = parseInt(document.getElementById('unspent_build').textContent);
        if (unspentBuild < 0) {
            alert('You have overspent your build points. Please remove some skills.');
            return false;
        }

        // Check if there are unspent affinity points
        const unspentAffinity = parseInt(document.getElementById('unspent_slotted_cores').textContent);
        if (unspentAffinity < 0) {
            alert('You have overspent your affinity points. Please adjust your affinities.');
            return false;
        }

        return true;
    },

    // Initialize event listeners
    initializeFormListeners() {
        // Make the submit function available globally
        window.submitCharacterForm = (form) => this.submitCharacterForm(form);

        // Add any additional form-related listeners here
        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', (event) => {
                if (!this.submitCharacterForm(event.target)) {
                    event.preventDefault();
                }
            });
        }
    }
}; 