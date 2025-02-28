export const buildSystem = {
    isUpdating: false, // Add flag to prevent recursive updates

    updateUnspentBuild() {
        // Prevent recursive updates
        if (this.isUpdating) {
            return;
        }
        this.isUpdating = true;

        let totalSpentBuild = 0;
        console.log('--- Updating Unspent Build ---');

        // Get required elements
        const essenceInput = document.querySelector('input[name="essence"]');
        const totalBuildElement = document.getElementById('total_build');
        const unspentBuildElement = document.getElementById('unspent_build');

        if (!totalBuildElement || !unspentBuildElement) {
            console.error('Required build elements not found');
            this.isUpdating = false;
            return;
        }

        // Get total build from the element
        const totalBuild = parseInt(totalBuildElement.textContent) || 0;
        console.log('Total Build Available:', totalBuild);

        // Calculate Essence costs
        if (essenceInput) {
            const essenceValue = parseInt(essenceInput.value || '0', 10);
            const baseEssence = 5;
            const essenceCostPerPoint = parseInt(essenceInput.getAttribute('essence-cost-per-point'), 10) || 0;

            if (essenceValue > baseEssence) {
                const extraEssence = essenceValue - baseEssence;
                const essenceCost = extraEssence * essenceCostPerPoint;
                totalSpentBuild += essenceCost;
                console.log(`Essence cost: ${essenceCost} (${extraEssence} extra points)`);
            }
        }

        // Calculate skill costs for all selected skills
        const skillContainers = [
            'passive-skills-container',
            'encounter-skills-container',
            'bell-skills-container',
            'day-skills-container',
            'weekend-skills-container'
        ];

        skillContainers.forEach(containerId => {
            const container = document.getElementById(containerId);
            if (container) {
                const skillElements = container.querySelectorAll('.skill-item');
                skillElements.forEach(skillElement => {
                    const buildCost = parseInt(skillElement.dataset.buildCost) || 0;
                    const level = parseInt(skillElement.dataset.level) || 1;
                    const totalCost = buildCost * level;
                    
                    if (totalCost > 0) {
                        totalSpentBuild += totalCost;
                        console.log(`Skill cost for ${skillElement.textContent}: ${totalCost} (${buildCost} x ${level})`);
                    }
                });
            }
        });

        // Calculate final values
        const unspentBuild = Math.max(0, totalBuild - totalSpentBuild);

        // Update display
        unspentBuildElement.textContent = unspentBuild;

        console.log('Final Calculations:', {
            totalBuild,
            totalSpentBuild,
            unspentBuild
        });

        // Reset the update flag
        this.isUpdating = false;

        // Dispatch event for other systems
        const customEvent = new CustomEvent('buildUpdated', {
            detail: { totalBuild, unspentBuild }
        });
        document.dispatchEvent(customEvent);
    },

    // Initialize event listeners
    initializeBuildListeners() {
        console.log('Initializing build listeners');

        // Listen for direct skill interactions
        document.addEventListener('click', (event) => {
            if (event.target.matches('.buy-skill, .remove-skill')) {
                setTimeout(() => this.updateUnspentBuild(), 100);
            }
        });

        // Listen for various system events
        const events = [
            'essenceUpdated',
            'raceUpdated',
            'skillLevelChanged',
            'skillAdded',
            'skillRemoved',
            'affinityChanged'  // Add listener for affinity changes
        ];

        events.forEach(eventName => {
            document.addEventListener(eventName, () => {
                setTimeout(() => this.updateUnspentBuild(), 100);
            });
        });

        // Initial calculation (with a slight delay to ensure DOM is ready)
        setTimeout(() => this.updateUnspentBuild(), 100);
    }
}; 