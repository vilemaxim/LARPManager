export const skillSystem = {
    // Core functionality for loading existing skills
    loadExistingSkills() {
        const existingSkillsElement = document.getElementById('existing-skills');
        if (!existingSkillsElement) {
            console.log('No existing skills element found');
            return;
        }

        console.log('Found existing skills element');
        try {
            const existingSkills = JSON.parse(existingSkillsElement.textContent);
            console.log('Parsed existing skills:', existingSkills);
            
            // Map of frequency types to select IDs
            const frequencyMap = {
                passive: '#passive_skills',
                encounter: '#per_encounter_skills',
                bell: '#per_bell_skills',
                day: '#per_day_skills',
                weekend: '#per_weekend_skills'
            };

            // Process all frequency types
            Object.entries(frequencyMap).forEach(([type, selectId]) => {
                if (existingSkills[type] && existingSkills[type].length > 0) {
                    const select = document.querySelector(selectId);
                    if (select) {
                        existingSkills[type].forEach(skill => {
                            console.log(`Loading ${type} skill:`, skill);
                            this.addExistingSkill(skill, select);
                        });
                    }
                }
            });

        } catch (e) {
            console.error('Error parsing existing skills:', e);
            console.log('Raw content:', existingSkillsElement.textContent);
        }
    },

    // Common skills functionality
    loadCommonSkills() {
        fetch('/characters/get_common_skills/')
            .then(response => response.json())
            .then(data => {
                this.createSkillList(data.common_skills, 'common-skills-list', 'common');
            })
            .catch(error => {
                console.error('Error loading common skills:', error);
                document.getElementById('common-skills-list').innerHTML = 
                    '<p>Error loading skills. Please try again.</p>';
            });
    },

    // Race skills functionality
    loadRaceSkills(raceId) {
        if (!raceId) {
            document.getElementById('race-skills-list').innerHTML = 
                '<p>No race selected. Please select a race to see available skills.</p>';
            return;
        }

        fetch(`/characters/get_race_skills/?race=${encodeURIComponent(raceId)}`)
            .then(response => response.json())
            .then(data => {
                console.log('Received race skills data:', data);
                if (data && data.race_skills) {
                    this.createSkillList(data.race_skills, 'race-skills-list', 'race');
                } else {
                    console.error('Unexpected data structure:', data);
                    document.getElementById('race-skills-list').innerHTML = 
                        '<p>Error: Unexpected data format received.</p>';
                }
            })
            .catch(error => {
                console.error('Error loading race skills:', error);
                document.getElementById('race-skills-list').innerHTML = 
                    '<p>Error loading skills. Please try again.</p>';
            });
    },

    // Shared display functionality
    displaySkillList(skills, container, type) {
        container.innerHTML = '';

        if (skills.length === 0) {
            container.innerHTML = `<p>No ${type} skills available.</p>`;
            return;
        }

        const skillList = document.createElement('ul');
        skillList.classList.add('list-group');

        skills.forEach(skill => {
            const skillItem = document.createElement('li');
            skillItem.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-start');

            skillItem.innerHTML = `
                <div>
                    <div class="fw-bold">${skill.name}</div>
                    <small>Description: ${skill.description || 'No description available'}</small><br>
                    <small>Build: ${skill.build}</small><br>
                    <small>Frequency: ${skill.frequency}</small>
                    ${skill.max_time_can_buy ? `<br><small>How many times you can buy: ${skill.max_time_can_buy}</small>` : ''}
                </div>
                <button 
                    class="btn btn-primary btn-sm select-${type}-skill-button" 
                    data-skill-id="${skill.id}" 
                    data-skill-name="${skill.name}"
                    data-skill-description="${skill.description || ''}"
                    data-skill-frequency="${skill.frequency}" 
                    data-skill-build="${skill.build}"
                    ${skill.max_time_can_buy ? `data-skill-max-time-can-buy="${skill.max_time_can_buy}"` : ''}>
                    Select Skill
                </button>
            `;

            skillList.appendChild(skillItem);
        });

        container.appendChild(skillList);
    },

    // Skill addition functionality
    addSkill(skill, selectId, isCommonSkill = false) {
        console.log('Adding skill:', skill);
        
        // Get the select element
        const select = document.querySelector(selectId);
        if (!select) {
            console.error(`Select element not found for ID: ${selectId}`);
            return;
        }

        // Clear placeholder text if it exists
        const placeholder = select.querySelector('option[value="placeholder"]');
        if (placeholder) {
            placeholder.remove();
        }

        // Get or create the wrapper div
        let wrapper = select.previousElementSibling;
        if (!wrapper || !wrapper.classList.contains('form-select')) {
            wrapper = document.createElement('div');
            wrapper.classList.add('form-select');
            select.parentElement.insertBefore(wrapper, select);
        }

        // Create the skill container div
        const skillContainer = document.createElement('div');
        skillContainer.classList.add('skill-entry');
        skillContainer.style.display = 'flex';
        skillContainer.style.alignItems = 'center';
        skillContainer.style.marginBottom = '5px';
        skillContainer.style.padding = '5px';

        // Create the skill name span
        const skillName = document.createElement('span');
        skillName.textContent = skill.name;
        skillName.style.marginRight = '10px';

        // Create the skill controls
        const skillControls = document.createElement('span');
        skillControls.classList.add('skill-controls');
        
        // Initialize level
        const initialLevel = 1;
        
        if (skill.max_time_can_buy && skill.max_time_can_buy > 1) {
            skillControls.innerHTML = `
                Level: <span class="skill-level">${initialLevel}</span>/${skill.max_time_can_buy}
                <button type="button" class="btn btn-sm btn-success buy-skill" data-skill-id="${skill.id}"
                    ${initialLevel >= skill.max_time_can_buy ? 'disabled' : ''}>
                    +
                </button>
                <button type="button" class="btn btn-sm btn-danger remove-skill" data-skill-id="${skill.id}">
                    -
                </button>
            `;
        } else {
            skillControls.innerHTML = `
                <button type="button" class="btn btn-sm btn-danger remove-skill" data-skill-id="${skill.id}">
                    -
                </button>
            `;
        }

        // Assemble the skill container
        skillContainer.appendChild(skillName);
        skillContainer.appendChild(skillControls);
        wrapper.appendChild(skillContainer);

        // Create and add the hidden option
        const option = document.createElement('option');
        option.value = skill.id;
        option.textContent = skill.name;
        option.dataset.build = skill.build;
        option.dataset.frequency = skill.frequency;
        option.dataset.level = initialLevel.toString();
        if (skill.affinity) {
            option.dataset.affinityId = skill.affinity;
        }
        option.selected = true;
        select.appendChild(option);

        // Hide the select
        select.style.display = 'none';

        // Trigger build update with a slight delay to ensure DOM is updated
        setTimeout(() => {
            document.dispatchEvent(new CustomEvent('skillAdded', {
                detail: { 
                    skillId: skill.id, 
                    build: skill.build,
                    level: initialLevel 
                }
            }));
        }, 10);
    },

    // Update the addCommonSkill method
    addCommonSkill(skill) {
        console.log('Adding common skill with full details:', {
            skill,
            frequency: skill.frequency,
            type: typeof skill.frequency
        });
        
        if (!skill || !skill.frequency) {
            console.error('Invalid skill object:', skill);
            return;
        }

        // Map frequency to select ID
        const frequencyToSelectId = {
            'Passive': '#passive_skills',
            'passive': '#passive_skills',
            'Encounter': '#per_encounter_skills',
            'encounter': '#per_encounter_skills',
            'Bell': '#per_bell_skills',
            'bell': '#per_bell_skills',
            'Day': '#per_day_skills',
            'day': '#per_day_skills',
            'Weekend': '#per_weekend_skills',
            'weekend': '#per_weekend_skills'
        };

        const selectId = frequencyToSelectId[skill.frequency.trim()];
        console.log('Looking for select with ID:', selectId);

        if (!selectId) {
            console.error('Unknown frequency:', skill.frequency);
            console.log('Available frequencies:', Object.keys(frequencyToSelectId));
            return;
        }

        this.addSkill(skill, selectId);
    },

    // Update other methods that call addSkill
    addAffinitySkill(skill) {
        console.log('Adding affinity skill:', skill);
        const frequencyToSelectId = {
            'Passive': '#passive_skills',
            'Encounter': '#per_encounter_skills',
            'Bell': '#per_bell_skills',
            'Day': '#per_day_skills',
            'Weekend': '#per_weekend_skills'
        };
        const selectId = frequencyToSelectId[skill.frequency];
        if (selectId) {
            this.addSkill(skill, selectId, false);
        } else {
            console.error('Unknown frequency:', skill.frequency);
        }
    },

    // Helper functions
    getTargetSelectId(frequency) {
        const frequencyMap = {
            "Encounter": "#per_encounter_skills",
            "Bell": "#per_bell_skills",
            "Daily": "#per_day_skills",
            "Weekend": "#per_weekend_skills",
            "Passive & At Will": "#passive_skills",
            "Passive": "#passive_skills",
            "At Will": "#passive_skills",
            "N/A": "#passive_skills"
        };

        const targetSelectId = frequencyMap[frequency];
        if (!targetSelectId) {
            console.error(`Unknown frequency: ${frequency}`);
            return null;
        }
        return targetSelectId;
    },

    createSkillOption(skill, targetSelect) {
        const newOption = document.createElement('option');
        newOption.value = skill.id;
        newOption.textContent = `${skill.name} (Build: ${skill.build}${skill.max_time_can_buy ? ', Level: 1' : ''})`;
        newOption.dataset.build = skill.build;
        newOption.dataset.description = skill.description || "No description available";
        newOption.dataset.frequency = skill.frequency;
        if (skill.max_time_can_buy) {
            newOption.dataset.max_time_can_buy = skill.max_time_can_buy;
            newOption.dataset.level = 1;
        }
        newOption.selected = true;
        targetSelect.appendChild(newOption);
        targetSelect.style.display = 'none';
    },

    createSkillDisplay(skill, wrapper) {
        const skillContainer = document.createElement('div');
        skillContainer.classList.add('d-flex', 'align-items-center', 'gap-2', 'mb-2', 'w-100');
        skillContainer.dataset.skillId = skill.id;

        const hasLevels = skill.max_time_can_buy && skill.max_time_can_buy > 1;

        skillContainer.innerHTML = `
            <div class="skill-display flex-grow-1">${skill.name} (Build: ${skill.build})</div>
            <div class="skill-controls d-inline-flex align-items-center gap-2">
                ${hasLevels ? `
                    <button type="button" class="btn btn-sm btn-success buy-skill" 
                        data-skill-id="${skill.id}"
                        data-container-id="${skill.id}">
                        &#43;
                    </button>
                ` : ''}
                <button type="button" class="btn btn-sm btn-danger remove-skill" 
                    data-skill-id="${skill.id}"
                    data-container-id="${skill.id}">
                    −
                </button>
                ${hasLevels ? `<span class="ms-2">Level: <span class="skill-level">1</span>/${skill.max_time_can_buy}</span>` : ''}
            </div>
        `;

        wrapper.appendChild(skillContainer);
    },

    closeSkillModal(type, affinityName = null) {
        let modalId;
        switch (type) {
            case 'common':
                modalId = 'addCommonSkillModal';
                break;
            case 'race':
                modalId = 'addRaceSkillModal';
                break;
            case 'affinity':
                modalId = `add${affinityName}SkillModal`;
                break;
            default:
                return;
        }
        
        const modal = document.querySelector(`#${modalId}`);
        const bootstrapModal = bootstrap.Modal.getInstance(modal);
        if (bootstrapModal) bootstrapModal.hide();
    },

    // Initialize event listeners
    initializeSkillListeners() {
        // Common skills modal listener
        const commonSkillModal = document.querySelector('#addCommonSkillModal');
        if (commonSkillModal) {
            commonSkillModal.addEventListener('show.bs.modal', () => this.loadCommonSkills());
        }

        // Race skills modal listener
        const raceSkillModal = document.querySelector('#addRaceSkillModal');
        if (raceSkillModal) {
            raceSkillModal.addEventListener('show.bs.modal', () => {
                const raceId = document.querySelector('#id_race').value;
                if (!raceId) {
                    document.querySelector('#race-skills-list').innerHTML = 
                        '<p>No race selected. Please select a race to see available skills.</p>';
                } else {
                    this.loadRaceSkills(raceId);
                }
            });
        }

        // Listen for skill button clicks
        document.addEventListener('click', (event) => {
            // Handle skill removal and level changes
            if (event.target.classList.contains('remove-skill')) {
                this.handleSkillRemoval(event.target);
            } else if (event.target.classList.contains('buy-skill')) {
                this.handleSkillLevelChange(event.target);
            }

            // Handle affinity skill button clicks
            if (event.target.classList.contains('affinity-skill-button')) {
                event.preventDefault();
                const modalId = event.target.dataset.bsTarget;
                const modal = document.querySelector(modalId);
                
                if (modal) {
                    const bsModal = new bootstrap.Modal(modal, {
                        backdrop: true,
                        keyboard: true,
                        focus: true
                    });
                    bsModal.show();
                } else {
                    console.error('Modal not found:', modalId);
                }
            }
        });

        // Handle modal skill selection
        document.addEventListener('click', (event) => {
            if (event.target.classList.contains('select-skill-button')) {
                const skillData = {
                    id: event.target.dataset.skillId,
                    name: event.target.dataset.skillName,
                    description: event.target.dataset.skillDescription,
                    frequency: event.target.dataset.skillFrequency,
                    build: parseInt(event.target.dataset.skillBuild),
                    max_time_can_buy: parseInt(event.target.dataset.skillMaxTimeCanBuy) || 1
                };

                if (event.target.dataset.skillType === 'affinity') {
                    skillData.affinity = event.target.dataset.affinityId;
                }

                console.log(`Selected ${event.target.dataset.skillType} skill:`, skillData);
                
                // Add the skill
                const selectId = this.getSelectIdForFrequency(skillData.frequency);
                if (selectId) {
                    this.addSkill(skillData, selectId);
                }

                // Close the modal
                const modal = event.target.closest('.modal');
                if (modal) {
                    const bsModal = bootstrap.Modal.getInstance(modal);
                    if (bsModal) {
                        bsModal.hide();
                    }
                }
            }
        });

        // Load existing skills on initialization
        this.loadExistingSkills();
    },

    extractSkillData(button) {
        return {
            id: button.dataset.skillId,
            name: button.dataset.skillName,
            description: button.dataset.skillDescription,
            frequency: button.dataset.skillFrequency,
            build: parseInt(button.dataset.skillBuild),
            max_time_can_buy: parseInt(button.dataset.skillMaxTimeBuy) || 1
        };
    },

    handleSkillRemoval(button) {
        const skillId = button.dataset.skillId;
        console.log('Handling skill removal for ID:', skillId);

        // Find the wrapper and select elements
        const wrapper = button.closest('.form-select');
        if (!wrapper) {
            console.error('Could not find wrapper for skill');
            return;
        }

        const select = wrapper.nextElementSibling;
        if (!select) {
            console.error('Could not find select element for skill');
            return;
        }

        const skillEntry = button.closest('.skill-entry');
        const levelSpan = skillEntry?.querySelector('.skill-level');
        
        // If this is a leveled skill and level > 1, decrease level instead of removing
        if (levelSpan) {
            const currentLevel = parseInt(levelSpan.textContent);
            if (currentLevel > 1) {
                console.log(`Decreasing level from ${currentLevel} to ${currentLevel - 1}`);
                levelSpan.textContent = currentLevel - 1;
                
                // Enable the buy button if it was disabled
                const buyButton = skillEntry.querySelector('.buy-skill');
                if (buyButton) {
                    buyButton.disabled = false;
                }

                // Update the option's level
                const option = select.querySelector(`option[value="${skillId}"]`);
                if (option) {
                    option.dataset.level = (currentLevel - 1).toString();
                }

                // Trigger build update
                document.dispatchEvent(new CustomEvent('skillLevelChanged'));
                return;
            }
        }

        // If level is 1 or no level exists, remove the skill entirely
        const option = select.querySelector(`option[value="${skillId}"]`);
        if (option) {
            option.remove();
        }

        // Remove just the skill entry, not the entire wrapper
        if (skillEntry) {
            skillEntry.remove();
        }

        // If this was the last skill, add back the placeholder and show the select
        if (select.options.length === 0) {
            const placeholder = document.createElement('option');
            placeholder.value = 'placeholder';
            placeholder.textContent = 'No skills added yet';
            select.appendChild(placeholder);

            // Remove the empty wrapper if it exists
            if (wrapper) {
                wrapper.remove();
            }

            // Make sure the select is visible
            select.style.display = 'block';
            select.classList.add('form-select');
        }

        // Trigger build update
        document.dispatchEvent(new CustomEvent('skillRemoved', {
            detail: { skillId }
        }));
    },

    handleSkillLevelChange(button) {
        const skillId = button.dataset.skillId;
        const isIncrease = button.classList.contains('buy-skill');
        const skillEntry = button.closest('.skill-entry');
        const levelSpan = skillEntry.querySelector('.skill-level');
        const currentLevel = parseInt(levelSpan.textContent);
        const maxLevel = parseInt(skillEntry.textContent.split('/')[1]);

        if (isIncrease && currentLevel < maxLevel) {
            levelSpan.textContent = currentLevel + 1;
            if (currentLevel + 1 >= maxLevel) {
                button.disabled = true;
            }
        } else if (!isIncrease && currentLevel > 1) {
            levelSpan.textContent = currentLevel - 1;
            skillEntry.querySelector('.buy-skill').disabled = false;
        }

        // Update the option's level attribute
        const wrapper = button.closest('.form-select');
        const select = wrapper.nextElementSibling;
        const option = select.querySelector(`option[value="${skillId}"]`);
        if (option) {
            option.dataset.level = levelSpan.textContent;
        }

        // Trigger build update
        document.dispatchEvent(new CustomEvent('skillLevelChanged'));
    },

    // Add existing skill functionality
    addExistingSkill(skill, select) {
        console.log('Adding existing skill:', skill);
        
        // Clear placeholder text if it exists
        const placeholder = select.querySelector('option[value="placeholder"]');
        if (placeholder) {
            placeholder.remove();
        }

        // Create the skill container div
        const skillContainer = document.createElement('div');
        skillContainer.classList.add('skill-entry');
        skillContainer.style.display = 'flex';
        skillContainer.style.alignItems = 'center';
        skillContainer.style.marginBottom = '5px';
        skillContainer.style.padding = '5px';

        // Create the skill name span
        const skillName = document.createElement('span');
        skillName.textContent = skill.name;
        skillName.style.marginRight = '10px';

        // Create the skill controls
        const skillControls = document.createElement('span');
        skillControls.classList.add('skill-controls');
        
        // Initialize level
        const initialLevel = parseInt(skill.level) || 1;
        
        if (skill.max_time_can_buy && skill.max_time_can_buy > 1) {
            skillControls.innerHTML = `
                Level: <span class="skill-level">${initialLevel}</span>/${skill.max_time_can_buy}
                <button type="button" class="btn btn-sm btn-success buy-skill" data-skill-id="${skill.id}"
                    ${initialLevel >= skill.max_time_can_buy ? 'disabled' : ''}>
                    +
                </button>
                <button type="button" class="btn btn-sm btn-danger remove-skill" data-skill-id="${skill.id}">
                    -
                </button>
            `;
        } else {
            skillControls.innerHTML = `
                <button type="button" class="btn btn-sm btn-danger remove-skill" data-skill-id="${skill.id}">
                    -
                </button>
            `;
        }

        // Assemble the skill container
        skillContainer.appendChild(skillName);
        skillContainer.appendChild(skillControls);

        // Create a wrapper div that looks like a select box
        const wrapper = document.createElement('div');
        wrapper.classList.add('form-select');
        wrapper.style.minHeight = select.offsetHeight + 'px';
        wrapper.style.height = 'auto';
        wrapper.style.display = 'block';
        wrapper.style.padding = '0.375rem 0.75rem';
        wrapper.appendChild(skillContainer);

        // Store the skill data in a hidden select option
        const option = document.createElement('option');
        option.value = skill.id;
        option.textContent = skill.name;
        option.dataset.build = skill.build;
        option.dataset.frequency = skill.frequency;
        option.dataset.level = initialLevel.toString();
        if (skill.affinity) {
            option.dataset.affinityId = skill.affinity;
        }
        option.selected = true;
        select.appendChild(option);

        // Hide the select and insert the wrapper before it
        select.style.display = 'none';
        select.parentElement.insertBefore(wrapper, select);

        // Trigger build update
        document.dispatchEvent(new CustomEvent('skillAdded', {
            detail: { 
                skillId: skill.id, 
                build: skill.build,
                level: initialLevel 
            }
        }));
    },

    addRaceSkill(skill) {
        console.log('Adding race skill with full details:', {
            skill,
            frequency: skill.frequency,
            type: typeof skill.frequency
        });
        
        if (!skill || !skill.frequency) {
            console.error('Invalid skill object:', skill);
            return;
        }

        // Map frequency to select ID
        const frequencyToSelectId = {
            'Passive': '#passive_skills',
            'passive': '#passive_skills',
            'Encounter': '#per_encounter_skills',
            'encounter': '#per_encounter_skills',
            'Bell': '#per_bell_skills',
            'bell': '#per_bell_skills',
            'Day': '#per_day_skills',
            'day': '#per_day_skills',
            'Weekend': '#per_weekend_skills',
            'weekend': '#per_weekend_skills'
        };

        const selectId = frequencyToSelectId[skill.frequency.trim()];
        console.log('Looking for select with ID:', selectId);

        if (!selectId) {
            console.error('Unknown frequency:', skill.frequency);
            console.log('Available frequencies:', Object.keys(frequencyToSelectId));
            return;
        }

        this.addSkill(skill, selectId);
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

    createSkillList(skills, containerId, type = 'common') {
        console.log('Creating skill list:', { skills, containerId, type });
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container not found: ${containerId}`);
            return;
        }

        if (!skills || skills.length === 0) {
            container.innerHTML = '<p>No skills available.</p>';
            return;
        }

        const skillButtons = skills.map(skill => `
            <button type="button" 
                class="btn btn-outline-primary mb-2 w-100 text-start select-skill-button"
                data-skill-id="${skill.id}"
                data-skill-name="${skill.name}"
                data-skill-description="${skill.description}"
                data-skill-frequency="${skill.frequency}"
                data-skill-build="${skill.build}"
                data-skill-max-time-can-buy="${skill.max_time_can_buy || 1}"
                data-skill-type="${type}"
                ${type === 'affinity' ? `data-affinity-id="${skill.affinity_id}"` : ''}>
                <strong>${skill.name}</strong><br>
                <small>${skill.description}</small><br>
                <small>Build: ${skill.build} | Frequency: ${skill.frequency}</small>
            </button>
        `).join('');

        container.innerHTML = skillButtons;
    }
}; 