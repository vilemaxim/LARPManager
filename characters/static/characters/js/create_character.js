document.addEventListener('DOMContentLoaded', function () {
	// Read Only
	const totalBuildElement = document.querySelector('#total_build');
	const unspentBuildElement = document.getElementById('unspent_build');
	const cultivatorTierElement = document.querySelector('#cultivator_tier');

	let totalBuild = 0;
	let previousRaceId = null;

	function updateUnspentBuild() {
		let totalSpentBuild = 0;
		console.log('--- Updating Unspent Build ---');

		if (essenceInput) {
			const essenceValue = parseInt(essenceInput.value || '0', 10); 
			const baseEssence = 5; 
			const essenceCostPerPoint = parseInt(essenceInput.getAttribute('essence-cost-per-point'), 10) || 0; 

			if (essenceValue > baseEssence) {
				const extraEssence = essenceValue - baseEssence; // Calculate extra Essence
				const essenceCost = extraEssence * essenceCostPerPoint; // Calculate cost for extra Essence
				totalSpentBuild += essenceCost; // Add to total build spent
			}
		}


		const totalBuild = parseInt(totalBuildElement.dataset.totalBuild, 10);
		const unspentBuild = Math.max(0, totalBuild - totalSpentBuild);

		console.log(`Total Build: ${totalBuild}`);
		console.log(`Total Spent Build: ${totalSpentBuild}`);
		console.log(`Unspent Build: ${unspentBuild}`);

		unspentBuildElement.textContent = unspentBuild;
    }

	/*********
	 * event *
	 ********/

	const eventDropdown = document.getElementById("id_starting_event");
	if (eventDropdown) {
		eventDropdown.addEventListener('change', function () {
			const eventId = eventDropdown.value;

			if (eventId) {
				fetch(`/characters/get_event_details/?event_id=${eventId}`)
					.then(response => {
						if (!response.ok) {
							throw new Error(`HTTP error! Status: ${response.status}`);
						}
						return response.json();
					})
					.then(data => {
						totalBuild = data.total_points || 0;
						totalBuildElement.textContent = totalBuild;
						totalBuildElement.dataset.totalBuild = totalBuild;
						cultivatorTierElement.textContent = data.cultivator_tier || "N/A";

						updateUnspentBuild();
					})
					.catch(error => {
						console.error('Error fetching event details:', error);
						totalBuild = 0;
						totalBuildElement.textContent = '0';
						unspentBuildElement.textContent = '0';
						cultivatorTierElement.textContent = "N/A";
					});
			} else {
				totalBuild = 0;
				totalBuildElement.textContent = '0';
				unspentBuildElement.textContent = '0';
				cultivatorTierElement.textContent = "N/A";
			}
		});
	} else {
		console.error("eventDropdown NOT found! Check if the element exists.");
	}

	/********
	 * Race *
	 ********/
	const raceDropdown = document.querySelector('select[name="race"]');
	if (raceDropdown) {
		raceDropdown.addEventListener('change', function () {
			const raceId = raceDropdown.value;

			if (raceId) {
				fetch(`/characters/get_race_starting_affinity/?race_id=${raceId}`, {
					headers: { 'X-Requested-With': 'XMLHttpRequest' }
				})
				.then(response => {
					if (!response.ok) {
						throw new Error(`HTTP error! Status: ${response.status}`);
					}
					return response.json();
				})
				.then(data => {
					// If a previous race exists, clear its starting affinity
					if (previousRaceId) {
						clearPreviousRaceAffinity(previousRaceId);
					}

					// Apply the new race's starting affinity
					applyRaceStartingAffinity(data);

					// Update the `previousRaceId` to the current race
					previousRaceId = raceId;
				})
				.catch(error => {
					console.error('Error fetching race starting affinity:', error);
				});
			} else {
				// If no race is selected, clear everything
				clearAffinityInputs();
				updateAffinityButtons();
				previousRaceId = null; // Reset the previous race ID
			}
		});
	}

	/***********
	 * Essence *
	 ***********/

	// TODO Not sure what is happening here. For some reason, if I remove even console.log, this event will not trigger updateUnspentBuild
    // Attach an event listener for the 'input' event
	const essenceInput = document.getElementById("essence");
    essenceInput.addEventListener('input', function (event) {
        const essenceValue = event.target.value;
        console.log('Essence value changed:', essenceValue);
		updateUnspentBuild()
    });


	/************
	 * Affinity *
	 ************/
	const affinityInputs = document.querySelectorAll('.affinity-input'); 
	const affinitySkillButtonsContainer = document.querySelector('#affinity-skill-buttons');

	affinityInputs.forEach(input => {
		input.addEventListener('input', updateAffinityButtons);
	});

	function updateAffinityButtons() {
		console.log(`updateAffinityButtons Called`); 
		// Clear the existing buttons
		affinitySkillButtonsContainer.innerHTML = '';

		// Loop through each affinity input field
		affinityInputs.forEach(input => {
			const affinityName = input.closest('.col-md-2').querySelector('label').textContent.trim(); // Get affinity name
			const affinityValue = parseInt(input.value || '0', 10); // Get the current affinity value
			
			console.log(`Affinity: ${affinityName}, Value: ${affinityValue}`); // Debugging: log affinity names and values
			
			if (affinityValue > 0) {
				// Create a new button for the affinity

				const button = document.createElement('button');
				button.type = 'button';
				button.classList.add('btn', 'btn-secondary', 'me-2'); // Styling classes
				button.textContent = `Add ${affinityName} Skill`;
				button.dataset.affinity = affinityName; // Add data-affinity attribute for reference

				// Add click event listener to open the modal for the specific affinity
				button.addEventListener('click', function () {
					openAffinitySkillModal(affinityName);
				});

				// Add the button to the container
				affinitySkillButtonsContainer.appendChild(button);
			}
		});
	}

	function applyRaceStartingAffinity(data) {
		// Find the input for the starting affinity
		const startingAffinityInput = document.querySelector(`#affinity_${data.starting_affinity_id}`);
		if (startingAffinityInput) {
			// Update the value and min based on the starting affinity tier
			const startingTier = parseInt(data.starting_affinity_tier, 10);
			startingAffinityInput.value = startingTier;
			startingAffinityInput.min = startingTier;

			// Highlight the field to indicate it is preset
			startingAffinityInput.classList.add('starting-affinity');
		}
		updateAffinityButtons();
	}

	/*******************
	 * Skills - Common *
	 *******************/
	// Load common skills when the modal is shown
	const commonSkillModal = document.querySelector('#addCommonSkillModal');
	commonSkillModal.addEventListener('show.bs.modal', function() {
		console.log("Loading common skills...");
		loadCommonSkills();
	});

	const commonSkillsList = document.querySelector('#common-skills-list');

	// Load common skills into the modal
	function loadCommonSkills() {
		fetch('/characters/get_common_skills/', {
			headers: { 'X-Requested-With': 'XMLHttpRequest' }
		})
		.then(response => {
			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
			}
			return response.json();
		})
		.then(data => {
			const skills = data.common_skills;
			commonSkillsList.innerHTML = '';

			if (skills.length === 0) {
				commonSkillsList.innerHTML = '<p>No common skills available.</p>';
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
					</div>
					<button 
						class="btn btn-primary btn-sm select-skill-button" 
						data-skill-id="${skill.id}" 
						data-skill-name="${skill.name}"
						data-skill-description="${skill.description}"
						data-skill-frequency="${skill.frequency}" 
						data-skill-build="${skill.build}">
						Select Skill
					</button>
				`;

				skillList.appendChild(skillItem);
			});

			commonSkillsList.appendChild(skillList);
		})
		.catch(error => {
			console.error('Error fetching common skills:', error);
			commonSkillsList.innerHTML = '<p>Error loading common skills. Please try again later.</p>';
		});
	}

	// Add common skill to the appropriate section
	function addCommonSkill(skill) {
		const unspentBuild = parseInt(unspentBuildElement.textContent, 10);
		let targetSelectId;

		switch (skill.frequency) {
			case "Per Encounter":
				targetSelectId = "#per_encounter_skills";
				break;
			case "Per Bell":
				targetSelectId = "#per_bell_skills";
				break;
			case "Per Day":
				targetSelectId = "#per_day_skills";
				break;
			case "Per Weekend":
				targetSelectId = "#per_weekend_skills";
				break;
			case "Passive & At Will":
			case "Passive":
				targetSelectId = "#passive_skills";
				break;
			default:
				console.error(`Unknown frequency: ${skill.frequency}`);
				return;
		}

		const targetSelect = document.querySelector(targetSelectId);
		const placeholderOption = targetSelect.querySelector('option[value="placeholder"]');

		if (placeholderOption) {
			placeholderOption.remove();
		}

		const skillExists = Array.from(targetSelect.options).some(
			option => option.value === skill.id.toString()
		);

		if (!skillExists && unspentBuild >= skill.build) {
			const newOption = document.createElement('option');
			newOption.value = skill.id; // Use skill ID as the value
			newOption.textContent = `${skill.name} (Build: ${skill.build})`; // Display Skill Name and Build Points
			newOption.dataset.affinity = skill.affinity || "N/A";
			newOption.dataset.build = skill.build || "N/A";
			newOption.dataset.description = skill.description || "No description available"; // Set correct description
			newOption.dataset.frequency = skill.frequency || "N/A";
			newOption.dataset.maxTimeCanBuy = skill.max_time_can_buy || 1; // Use actual max_time_can_buy value
			newOption.dataset.level = 1; // Default level when first added
			targetSelect.appendChild(newOption);

			unspentBuildElement.textContent = unspentBuild - skill.build;

			// Close the modal
			const modal = document.querySelector('#addCommonSkillModal');
			const bootstrapModal = bootstrap.Modal.getInstance(modal);
			if (bootstrapModal) bootstrapModal.hide();
		} else if (!skillExists) {
			alert(`Not enough unspent build points to add "${skill.name}".`);
		}
	}

	// Event delegation for common skills
	commonSkillsList.addEventListener('click', function (event) {
		const button = event.target.closest('.select-skill-button');
		if (!button) return;

		const skillId = button.getAttribute('data-skill-id');
		const skillName = button.getAttribute('data-skill-name');
		const skillFrequency = button.getAttribute('data-skill-frequency');
		const skillBuild = parseInt(button.getAttribute('data-skill-build'), 10);

		addCommonSkill({ id: skillId, name: skillName, frequency: skillFrequency, build: skillBuild });
	});

	/*******************
	 * Skills - Racial *
	 *******************/
	const raceSkillModal = document.querySelector('#addRaceSkillModal');
	raceSkillModal.addEventListener('show.bs.modal', function () {
		const raceId = raceDropdown.value;
		if (!raceId) {
			raceSkillsList.innerHTML = '<p>No race selected. Please select a race to see available skills.</p>';
		} else {
			console.log("Loading racial skills...");
			loadRaceSkills(raceId);
		}
	});

	const raceSkillsList = document.querySelector('#race-skills-list');

	function loadRaceSkills(raceId) {
		fetch(`/characters/get_race_skills/?race_id=${raceId}`, {
			headers: { 'X-Requested-With': 'XMLHttpRequest' }
		})
		.then(response => {
			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
			}
			return response.json();
		})
		.then(data => {
			const skills = data.race_skills;
			raceSkillsList.innerHTML = '';

			if (skills.length === 0) {
				raceSkillsList.innerHTML = '<p>No skills available for the selected race.</p>';
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
					</div>
					<button 
						class="btn btn-primary btn-sm select-race-skill-button" 
						data-skill-id="${skill.id}" 
						data-skill-name="${skill.name}"
						data-skill-description="${skill.description}"
						data-skill-frequency="${skill.frequency}" 
						data-skill-build="${skill.build}">
						Select Skill
					</button>
				`;

				skillList.appendChild(skillItem);
			});

			raceSkillsList.appendChild(skillList);
		})
		.catch(error => {
			console.error('Error fetching race skills:', error);
			raceSkillsList.innerHTML = '<p>Error loading race skills. Please try again later.</p>';
		});
	}

	// Add race skill to the appropriate section
	function addRaceSkill(skill) {
		const unspentBuild = parseInt(unspentBuildElement.textContent, 10);
		let targetSelectId;

		switch (skill.frequency) {
			case "Encounter":
				targetSelectId = "#per_encounter_skills";
				break;
			case "Bell":
				targetSelectId = "#per_bell_skills";
				break;
			case "Daily":
				targetSelectId = "#per_day_skills";
				break;
			case "Weekend":
				targetSelectId = "#per_weekend_skills";
				break;
			case "Passive & At Will":
			case "Passive":
			case "N/A":
				targetSelectId = "#passive_skills";
				break;
			default:
				console.error(`Unknown frequency: ${skill.frequency}`);
				return;
		}

		const targetSelect = document.querySelector(targetSelectId);
		const placeholderOption = targetSelect.querySelector('option[value="placeholder"]');

		if (placeholderOption) {
			placeholderOption.remove();
		}

		const skillExists = Array.from(targetSelect.options).some(
			option => option.value === skill.id.toString()
		);

		if (!skillExists && unspentBuild >= skill.build) {
			const newOption = document.createElement('option');
			newOption.value = skill.id;
			newOption.textContent = `${skill.name} (Build: ${skill.build})`;
			newOption.dataset.affinity = skill.affinity || "N/A";
			newOption.dataset.build = skill.build || "N/A";
			newOption.dataset.description = skill.description || "N/A";
			newOption.dataset.frequency = skill.frequency || "N/A";
			newOption.dataset.maxTimeCanBuy = skill.max_time_can_buy || 1;
			newOption.dataset.level = 1; // Default level when first added
			targetSelect.appendChild(newOption);

			unspentBuildElement.textContent = unspentBuild - skill.build;

			// Close the modal
			const modal = document.querySelector('#addRaceSkillModal');
			const bootstrapModal = bootstrap.Modal.getInstance(modal);
			if (bootstrapModal) bootstrapModal.hide();
		} else if (!skillExists) {
			alert(`Not enough unspent build points to add "${skill.name}".`);
		}
	}

	// Event delegation for race skills
	raceSkillsList.addEventListener('click', function (event) {
		const button = event.target.closest('.select-race-skill-button');
		if (!button) return;

		const skillId = button.getAttribute('data-skill-id');
		const skillName = button.getAttribute('data-skill-name');
		const skillFrequency = button.getAttribute('data-skill-frequency');
		const skillBuild = parseInt(button.getAttribute('data-skill-build'), 10);

		addRaceSkill({ id: skillId, name: skillName, frequency: skillFrequency, build: skillBuild });
	});

	/*********************
	 * Skills - Affinity *
	 *********************/
	const skillAffinityElement = document.getElementById('skill_affinity');

	function updateAffinityButtons() {
		// Clear the existing buttons
		affinitySkillButtonsContainer.innerHTML = '';

		// Loop through each affinity input field
		affinityInputs.forEach(input => {
			const affinityName = input.closest('.col-md-2').querySelector('label').textContent.trim(); // Get affinity name
			const affinityValue = parseInt(input.value || '0', 10); // Get the current affinity value
			
			console.log(`Affinity: ${affinityName}, Value: ${affinityValue}`); // Debugging: log affinity names and values
			
			if (affinityValue > 0) {
				// Create a new button for the affinity
				const button = document.createElement('button');
				button.type = 'button';
				button.classList.add('btn', 'btn-secondary', 'me-2'); // Styling classes
				button.textContent = `Add ${affinityName} Skill`;
				button.dataset.affinity = affinityName; // Add data-affinity attribute for reference

				// Add click event listener to open the modal for the specific affinity
				button.addEventListener('click', function () {
					openAffinitySkillModal(affinityName);
				});

				// Add the button to the container
				affinitySkillButtonsContainer.appendChild(button);
			}
		});
	}

	// Open a modal for the selected affinity skill.
	function openAffinitySkillModal(affinityName) {
		// Check if a modal already exists for this affinity
		let modal = document.querySelector(`#add${affinityName}SkillModal`);

		if (!modal) {
			// If not, create the modal dynamically
			modal = document.createElement('div');
			modal.id = `add${affinityName}SkillModal`;
			modal.classList.add('modal', 'fade');
			modal.setAttribute('tabindex', '-1');
			modal.setAttribute('aria-labelledby', `add${affinityName}SkillModalLabel`);
			modal.setAttribute('aria-hidden', 'true');

			modal.innerHTML = `
				<div class="modal-dialog modal-lg">
					<div class="modal-content">
						<div class="modal-header">
							<h5 class="modal-title" id="add${affinityName}SkillModalLabel">Add ${affinityName} Skill</h5>
							<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
						</div>
						<div class="modal-body">
							<div id="${affinityName.toLowerCase()}-skills-list">
								<p>Loading ${affinityName} skills...</p>
							</div>
						</div>
						<div class="modal-footer">
							<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
						</div>
					</div>
				</div>
			`;

			// Append the modal to the body
			document.body.appendChild(modal);

			// Load the affinity skills dynamically
			loadAffinitySkills(affinityName);
		}

		// Show the modal using Bootstrap's API
		const bootstrapModal = new bootstrap.Modal(modal);
		bootstrapModal.show();
	}

	// Fetch and display skills for a specific affinity.
	function loadAffinitySkills(affinityName) {
		const skillsList = document.querySelector(`#${affinityName.toLowerCase()}-skills-list`);

		fetch(`/characters/get_affinity_skills/?affinity=${affinityName}`, {
			headers: {
				'X-Requested-With': 'XMLHttpRequest'
			}
		})
			.then(response => {
				if (!response.ok) {
					throw new Error(`HTTP error! Status: ${response.status}`);
				}
				return response.json();
			})
			.then(data => {
				const skills = data.affinity_skills;
				const affinityId = data.affinity_id;

				// Clear existing content
				skillsList.innerHTML = '';

				if (skills.length === 0) {
					skillsList.innerHTML = `<p>No skills available for ${affinityName}.</p>`;
					return;
				}

				// Create a list of skills
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
						</div>
						<button 
							class="btn btn-primary btn-sm select-affinity-skill-button" 
							data-skill-id="${skill.id}" 
							data-skill-name="${skill.name}"
							data-skill-description="${skill.description}
							data-skill-build="${skill.build}" 
							data-skill-frequency="${skill.frequency}">
							Select Skill
						</button>
					`;

					// Add event listener to the "Select Skill" button
					skillItem.querySelector('.select-affinity-skill-button').addEventListener('click', function () {
						addAffinitySkill({
							id: skill.id,
							name: skill.name,
							description: skill.description,
							build: skill.build,
							frequency: skill.frequency,
							maxTimeCanBuy: skill.max_time_can_buy,
							affinity: affinityName,
							affinityId: data.affinity_id
						});
					});

					skillList.appendChild(skillItem);
				});

				skillsList.appendChild(skillList);
			})
			.catch(error => {
				console.error(`Error fetching ${affinityName} skills:`, error);
				skillsList.innerHTML = `<p>Error loading ${affinityName} skills. Please try again later.</p>`;
			});
	}

	// Add an affinity skill to the character.
	function addAffinitySkill(skill) {
		const affinityId = skill.affinityId;
		const unspentBuildElement = document.querySelector('#unspent_build');
		let unspentBuild = parseInt(unspentBuildElement.textContent, 10);

		let targetSelectId;
		switch (skill.frequency) {
			case "Encounter":
				targetSelectId = "#per_encounter_skills";
				break;
			case "Bell":
				targetSelectId = "#per_bell_skills";
				break;
			case "Daily":
				targetSelectId = "#per_day_skills";
				break;
			case "Weekend":
				targetSelectId = "#per_weekend_skills";
				break;
			case "Passive & At Will":
			case "Passive":
			case "At Will":
			case "N/A":
				targetSelectId = "#passive_skills";
				break;
			default:
				console.error(`Unknown frequency: ${skill.frequency}`);
				return; // Exit if frequency is not recognized
		}

		const targetSelect = document.querySelector(targetSelectId);

		// Remove the placeholder text if it exists
		const placeholderOption = targetSelect.querySelector('option[value="placeholder"]');
		if (placeholderOption) {
			placeholderOption.remove();
		}

		// Check if the skill is already added
		const skillExists = Array.from(targetSelect.options).some(
			option => option.value === skill.id.toString()
		);

		if (!skillExists) {
			// Check if there are enough unspent build points to add the skill
			if (unspentBuild >= skill.build) {
				// Add the new skill as an option
				const newOption = document.createElement('option');
				newOption.value = skill.id; // Use skill ID as the value
				newOption.textContent = `${skill.name} (Build: ${skill.build})`; // Display Skill Name and Build Points
				newOption.dataset.affinity = skill.affinity || "N/A";
				newOption.dataset.build = skill.build || "N/A";
				newOption.dataset.description = skill.description || "No description available"; 
				newOption.dataset.frequency = skill.frequency || "N/A";
				newOption.dataset.maxTimeCanBuy = skill.max_time_can_buy || 1; // Fix max_time_can_buy
				newOption.dataset.level = 1; // Default level
				targetSelect.appendChild(newOption);

				// Subtract the build cost of the skill from the unspent build
				unspentBuild -= skill.build;
				unspentBuildElement.textContent = unspentBuild;

				// Close the modal
				const modalId = `add${skill.affinity}SkillModal`;
				const modal = document.querySelector(`#${modalId}`);
				const bootstrapModal = bootstrap.Modal.getInstance(modal);
				if (bootstrapModal) bootstrapModal.hide();
			} else {
				// Alert the user if they don't have enough unspent build points
				alert(`Not enough unspent build points to add "${skill.name}". You need ${skill.build} build points.`);
			}
		}
	}

	function removeAffinitySkills(affinityId) {
		console.log(`Removing skills for affinity ID: ${affinityId}`); // Debugging

		// Define the dropdowns where skills might exist
		const skillSelects = [
			'#passive_skills',
			'#per_encounter_skills',
			'#per_bell_skills',
			'#per_day_skills',
			'#per_weekend_skills',
		];

		skillSelects.forEach(selectId => {
			const selectElement = document.querySelector(selectId);
			const optionsToRemove = [];

			// Identify all options related to the given affinity ID
			Array.from(selectElement.options).forEach(option => {
				if (option.dataset.affinityId === affinityId) {
					optionsToRemove.push(option);
				}
			});

			// Remove identified options
			optionsToRemove.forEach(option => {
				console.log(`Removing skill: ${option.textContent}`); // Debugging
				selectElement.removeChild(option);
			});
		});
		updateUnspentBuild();
	}
	updateUnspentBuild()
	updateAffinityButtons();
});
