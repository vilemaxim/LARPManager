// Import all modules
import { buildSystem } from './modules/buildSystem.js';
import { affinitySystem } from './modules/affinitySystem.js';
import { skillSystem } from './modules/skillSystem.js';
import { formSystem } from './modules/formSystem.js';
import { essenceSystem } from './modules/essenceSystem.js';
import { raceSystem } from './modules/raceSystem.js';
// import { formManager } from './modules/formManager.js';

// Initialize everything
document.addEventListener('DOMContentLoaded', () => {
    // Initialize all systems
    buildSystem.initializeBuildListeners();
    affinitySystem.initializeAffinityListeners();
    skillSystem.initializeSkillListeners();
    formSystem.initializeFormListeners();
    essenceSystem.initializeEssenceListeners();
    raceSystem.initializeRaceListeners();
});

// Make necessary functions globally available
window.submitCharacterForm = formSystem.submitCharacterForm;