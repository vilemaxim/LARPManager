export const essenceSystem = {
    // Core functionality
    updateEssence() {
        const essenceInput = document.querySelector('input[name="essence"]');
        if (!essenceInput) return;

        const baseEssence = 5;
        const essenceValue = parseInt(essenceInput.value || '0', 10);
        const essenceCostPerPoint = parseInt(essenceInput.getAttribute('essence-cost-per-point'), 10) || 0;

        console.log('Updating Essence:', {
            baseEssence,
            currentValue: essenceValue,
            costPerPoint: essenceCostPerPoint
        });

        // Calculate build cost for extra essence
        let essenceBuildCost = 0;
        if (essenceValue > baseEssence) {
            const extraEssence = essenceValue - baseEssence;
            essenceBuildCost = extraEssence * essenceCostPerPoint;
            console.log(`Extra essence: ${extraEssence}, Total cost: ${essenceBuildCost}`);
        }

        // Dispatch event for build system to handle
        const customEvent = new CustomEvent('essenceUpdated', {
            detail: {
                essenceCost: essenceBuildCost,
                totalEssence: essenceValue
            }
        });
        document.dispatchEvent(customEvent);
    },

    validateEssence(input) {
        const value = parseInt(input.value) || 0;
        const min = parseInt(input.min) || 0;
        const max = parseInt(input.max) || 100;

        // Ensure value is within bounds
        if (value < min) {
            input.value = min;
        } else if (value > max) {
            input.value = max;
        }

        this.updateEssence();
    },

    // Initialize event listeners
    initializeEssenceListeners() {
        const essenceInput = document.querySelector('input[name="essence"]');
        if (essenceInput) {
            essenceInput.addEventListener('change', () => this.validateEssence(essenceInput));
            essenceInput.addEventListener('input', () => this.validateEssence(essenceInput));
            
            // Initial calculation
            this.updateEssence();
        }
    }
}; 