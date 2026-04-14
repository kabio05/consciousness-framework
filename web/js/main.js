// ============================================
// Main JavaScript for Consciousness Framework
// ============================================

// Global variables to store data and chart instances
let assessmentData = null;
let charts = {
    radar: null,
    bar: null,
    timeline: null
};

// Color palette for charts - Updated to Blue Theme
const colorPalette = {
    primary: '#4A90E2',     // Changed from red to blue
    secondary: '#0f3460',
    accent: '#16213e',
    models: [
        'rgba(74, 144, 226, 0.8)',   // Blue (changed from red)
        'rgba(15, 52, 96, 0.8)',     // Blue
        'rgba(22, 33, 62, 0.8)',     // Dark Blue
        'rgba(255, 193, 7, 0.8)',    // Yellow
        'rgba(40, 167, 69, 0.8)',    // Green
        'rgba(108, 117, 125, 0.8)',  // Gray
        'rgba(255, 255, 255, 0.8)'   // White
    ]
};

const scoringMethodColors = {
    'keyword': '#FFB347',  // Orange
    'geval': '#77DD77',    // Green
    'hybrid': '#AEC6CF'    // Blue-gray
};

// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Initializing Consciousness Framework Dashboard...');
    
    try {
        // Load assessment data
        await loadAssessmentData();
        
        // Initialize UI components
        initializeControls();
        updateStatistics();
        
        // Set up event listeners
        setupEventListeners();
        
        // Create initial visualizations
        updateVisualizations();
        
        // Display latest assessment
        displayLatestAssessment();
        
        // Hide loading screen
        hideLoadingScreen();
        
    } catch (error) {
        console.error('❌ Initialization failed:', error);
        showError('Failed to load assessment data. Please check if data files exist.');
    }
});

// ============================================
// Data Loading
// ============================================

async function loadAssessmentData() {
    try {
        const response = await fetch('data/results.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        assessmentData = await response.json();
        console.log('✅ Loaded assessment data:', assessmentData);
        
        // Validate data structure
        if (!assessmentData.assessments || !Array.isArray(assessmentData.assessments)) {
            throw new Error('Invalid data structure');
        }
        
    } catch (error) {
        console.error('❌ Error loading data:', error);
        
        // Create empty data structure if file doesn't exist
        assessmentData = {
            assessments: [],
            available_traits: [],
            available_models: [],
            last_updated: null
        };
        
        // Show message that no data exists yet
        if (error.message.includes('404')) {
            showError('No assessment data found. Run an assessment first!');
        }
    }
}

// ============================================
// UI Initialization
// ============================================

function initializeControls() {
    // Initialize model selector
    const modelSelector = document.getElementById('modelSelector');
    
    if (assessmentData.available_models && assessmentData.available_models.length > 0) {
        assessmentData.available_models.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model.toUpperCase();
            modelSelector.appendChild(option);
        });
    }
    
    // Initialize trait checkboxes
    const traitContainer = document.getElementById('traitCheckboxes');
    
    if (assessmentData.available_traits && assessmentData.available_traits.length > 0) {
        assessmentData.available_traits.forEach(trait => {
            const label = document.createElement('label');
            label.className = 'trait-checkbox checked';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = trait;
            checkbox.checked = true;
            checkbox.id = `trait-${trait}`;
            
            const traitName = formatTraitName(trait);
            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(traitName));
            
            // Add change listener
            checkbox.addEventListener('change', (e) => {
                label.classList.toggle('checked', e.target.checked);
                updateVisualizations();
            });
            
            traitContainer.appendChild(label);
        });
    } else {
        traitContainer.innerHTML = '<p class="placeholder">No traits available yet.</p>';
    }
}

function updateStatistics() {
    // Update hero statistics with null checks
    const totalAssessments = document.getElementById('totalAssessments');
    if (totalAssessments) {
        totalAssessments.textContent = assessmentData.assessments ? assessmentData.assessments.length : 0;
    }
    
    const modelsTestd = document.getElementById('modelsTestd');
    if (modelsTestd) {
        modelsTestd.textContent = assessmentData.available_models ? assessmentData.available_models.length : 0;
    }
    
    const traitsAvailable = document.getElementById('traitsAvailable');
    if (traitsAvailable) {
        traitsAvailable.textContent = assessmentData.available_traits ? assessmentData.available_traits.length : 0;
    }
    
    // Update last updated time
    if (assessmentData.last_updated) {
        const date = new Date(assessmentData.last_updated);
        const lastUpdatedElement = document.getElementById('lastUpdated');
        if (lastUpdatedElement) {
            lastUpdatedElement.textContent = date.toLocaleString();
        }
    }
}

// ============================================
// Event Listeners
// ============================================

function setupEventListeners() {
    // Model selector change
    document.getElementById('modelSelector').addEventListener('change', updateVisualizations);
    
    // View mode buttons
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Update active state
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            
            // Switch view
            switchView(e.target.dataset.view);
        });
    });
}

// ============================================
// Visualization Updates
// ============================================

function updateVisualizations() {
    const selectedModel = document.getElementById('modelSelector').value;
    const selectedTraits = getSelectedTraits();
    
    if (assessmentData.assessments.length === 0) {
        showError('No assessment data available to visualize.');
        return;
    }
    
    // Get current view mode
    const activeView = document.querySelector('.view-btn.active').dataset.view;
    
    // Update the active visualization
    switch (activeView) {
        case 'radar':
            updateRadarChart(selectedModel, selectedTraits);
            break;
        case 'bar':
            updateBarChart(selectedModel, selectedTraits);
            break;
        case 'timeline':
            updateTimelineChart(selectedModel, selectedTraits);
            break;
        case 'heatmap':
            updateHeatmap(selectedModel, selectedTraits);
            break;
    }
}

function getSelectedTraits() {
    const checkboxes = document.querySelectorAll('#traitCheckboxes input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// ============================================
// Chart Functions
// ============================================

function updateRadarChart(selectedModel, selectedTraits) {
    const ctx = document.getElementById('radarChart').getContext('2d');
    
    // Destroy existing chart
    if (charts.radar) {
        charts.radar.destroy();
    }
    
    // Prepare datasets
    let datasets = [];
    
    if (selectedModel === 'all') {
        // Show all models using composite profiles
        const filteredAssessments = getFilteredAssessments();
        const modelsInFilteredData = [...new Set(filteredAssessments.map(a => a.model))];

        modelsInFilteredData.forEach((model, index) => {
            // Use composite profile if available, otherwise fall back to latest assessment
            if (assessmentData.composite_profile && assessmentData.composite_profile[model]) {
                const composite = assessmentData.composite_profile[model];
                const scores = selectedTraits.map(trait => composite.traits[trait] || 0);
                
                datasets.push({
                    label: model.toUpperCase() + ' (Composite)',
                    data: scores,
                    borderColor: colorPalette.models[index % colorPalette.models.length],
                    backgroundColor: colorPalette.models[index % colorPalette.models.length].replace('0.8', '0.2'),
                    pointBackgroundColor: colorPalette.models[index % colorPalette.models.length],
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: colorPalette.models[index % colorPalette.models.length],
                    borderWidth: 2,
                    pointRadius: 4
                });
            } else {
                // Fallback to latest assessment
                const latestAssessment = filteredAssessments.find(a => a.model === model);
                if (latestAssessment) {
                    datasets.push(createRadarDataset(latestAssessment, selectedTraits, index));
                }
            }
        });
    } else {
        // Show single model - use composite profile
        if (assessmentData.composite_profile && assessmentData.composite_profile[selectedModel]) {
            const composite = assessmentData.composite_profile[selectedModel];
            const scores = selectedTraits.map(trait => composite.traits[trait] || 0);
            
            datasets.push({
                label: selectedModel.toUpperCase() + ' (Composite)',
                data: scores,
                borderColor: colorPalette.models[0],
                backgroundColor: colorPalette.models[0].replace('0.8', '0.2'),
                pointBackgroundColor: colorPalette.models[0],
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: colorPalette.models[0],
                borderWidth: 2,
                pointRadius: 4
            });
            
            // Add indicators for which traits were updated when
            const lastUpdated = composite.last_updated || {};
            selectedTraits.forEach((trait, idx) => {
                if (lastUpdated[trait]) {
                    const date = new Date(lastUpdated[trait]);
                    const isRecent = (Date.now() - date.getTime()) < 3600000; // Within last hour
                    if (isRecent) {
                        // Could add visual indicator for recently updated traits
                        console.log(`Trait ${trait} was recently updated: ${date.toLocaleString()}`);
                    }
                }
            });
        } else {
            // Fallback to latest assessment
            const filteredAssessments = getFilteredAssessments();
            const assessment = filteredAssessments.find(a => a.model === selectedModel);
            if (assessment) {
                datasets.push(createRadarDataset(assessment, selectedTraits, 0));
            }
        }
    }
    
    // Create chart with COMPLETE configuration
    charts.radar = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: selectedTraits.map(formatTraitName),
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Consciousness Trait Scores',
                    color: '#4A90E2',
                    font: {
                        size: 18
                    }
                },
                legend: {
                    labels: {
                        color: '#eee'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            return `${context.dataset.label}: ${context.parsed.r.toFixed(3)}`;
                        }
                    }
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        stepSize: 0.2,
                        color: '#bbb',
                        backdropColor: 'transparent',
                        showLabelBackdrop: false
                    },
                    grid: {
                        color: 'rgba(42, 42, 62, 0.5)',
                        lineWidth: 1
                    },
                    angleLines: {
                        color: 'rgba(42, 42, 62, 0.5)',
                        lineWidth: 1
                    },
                    pointLabels: {
                        color: '#eee',
                        font: {
                            size: 12
                        }
                    }
                }
            },
            elements: {
                point: {
                    radius: 4,
                    hoverRadius: 6
                },
                line: {
                    borderWidth: 2
                }
            },
            interaction: {
                mode: 'point',
                intersect: false
            },
            onHover: (event, activeElements) => {
                if (activeElements.length > 0) {
                    const element = activeElements[0];
                    const datasetIndex = element.datasetIndex;
                    const index = element.index;
                    const dataset = datasets[datasetIndex];
                    const trait = selectedTraits[index];
                    const score = dataset.data[index];
                    
                    updateDetailsPanel(dataset.label, trait, score);
                }
            }
        }
    });
}

function createRadarDataset(assessment, traits, colorIndex) {
    const scores = traits.map(trait => assessment.traits[trait] || 0);
    const color = colorPalette.models[colorIndex % colorPalette.models.length];
    
    return {
        label: assessment.model.toUpperCase(),
        data: scores,
        borderColor: color,
        backgroundColor: color.replace('0.8', '0.2'), // More transparent background
        pointBackgroundColor: color,
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: color,
        borderWidth: 2,
        pointRadius: 4
    };
}

function updateBarChart(selectedModel, selectedTraits) {
    const ctx = document.getElementById('barChart').getContext('2d');
    
    // Destroy existing chart
    if (charts.bar) {
        charts.bar.destroy();
    }
    
    // Prepare data
    let labels = [];
    let datasets = [];
    
    if (selectedModel === 'all') {
        // Compare models
        labels = assessmentData.available_models.map(m => m.toUpperCase());
        
        selectedTraits.forEach((trait, traitIndex) => {
            const scores = assessmentData.available_models.map(model => {
                const assessment = assessmentData.assessments.find(a => a.model === model);
                return assessment ? (assessment.traits[trait] || 0) : 0;
            });
            
            datasets.push({
                label: formatTraitName(trait),
                data: scores,
                backgroundColor: colorPalette.models[traitIndex % colorPalette.models.length],
                borderColor: colorPalette.models[traitIndex % colorPalette.models.length],
                borderWidth: 1
            });
        });
    } else {
        // Show single model traits
        labels = selectedTraits.map(formatTraitName);
        const assessment = assessmentData.assessments.find(a => a.model === selectedModel);
        
        if (assessment) {
            const scores = selectedTraits.map(trait => assessment.traits[trait] || 0);
            datasets.push({
                label: assessment.model.toUpperCase(),
                data: scores,
                backgroundColor: colorPalette.models[0],
                borderColor: colorPalette.models[0],
                borderWidth: 1
            });
        }
    }
    
    // Create chart
    charts.bar = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: selectedModel === 'all' ? 'Model Comparison' : 'Trait Scores',
                    color: '#4A90E2', // Updated to blue
                    font: {
                        size: 18
                    }
                },
                legend: {
                    labels: {
                        color: '#eee'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        stepSize: 0.1,
                        color: '#bbb'
                    },
                    grid: {
                        color: '#2a2a3e'
                    }
                },
                x: {
                    ticks: {
                        color: '#eee'
                    },
                    grid: {
                        color: '#2a2a3e'
                    }
                }
            },
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    const element = elements[0];
                    const datasetIndex = element.datasetIndex;
                    const index = element.index;
                    
                    if (selectedModel === 'all') {
                        const model = assessmentData.available_models[index];
                        const trait = selectedTraits[datasetIndex];
                        const assessment = assessmentData.assessments.find(a => a.model === model);
                        const score = assessment ? (assessment.traits[trait] || 0) : 0;
                        updateDetailsPanel(model, trait, score);
                    } else {
                        const trait = selectedTraits[index];
                        const score = datasets[0].data[index];
                        updateDetailsPanel(selectedModel, trait, score);
                    }
                }
            }
        }
    });
}

function updateTimelineChart(selectedModel, selectedTraits) {
    const ctx = document.getElementById('timelineChart').getContext('2d');
    
    // Destroy existing chart
    if (charts.timeline) {
        charts.timeline.destroy();
    }
    
    // Filter assessments by model
    let filteredAssessments = selectedModel === 'all' 
        ? assessmentData.assessments 
        : assessmentData.assessments.filter(a => a.model === selectedModel);
    
    // Sort by timestamp
    filteredAssessments.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    
    // Prepare data
    const labels = filteredAssessments.map(a => new Date(a.timestamp).toLocaleDateString());
    const datasets = [{
        label: 'Overall Score',
        data: filteredAssessments.map(a => a.overall_score),
        borderColor: colorPalette.primary,
        backgroundColor: colorPalette.primary + '33',
        tension: 0.4
    }];
    
    // Create chart
    charts.timeline = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Score Evolution Over Time',
                    color: '#4A90E2', // Updated to blue
                    font: {
                        size: 18
                    }
                },
                legend: {
                    labels: {
                        color: '#eee'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        color: '#bbb'
                    },
                    grid: {
                        color: '#2a2a3e'
                    }
                },
                x: {
                    ticks: {
                        color: '#eee'
                    },
                    grid: {
                        color: '#2a2a3e'
                    }
                }
            }
        }
    });
}

function updateHeatmap(selectedModel, selectedTraits) {
    const container = document.getElementById('heatmap');
    container.innerHTML = '';
    
    // Create grid
    const models = selectedModel === 'all' 
        ? assessmentData.available_models 
        : [selectedModel];
    
    // Create header row
    const headerRow = document.createElement('div');
    headerRow.style.display = 'grid';
    headerRow.style.gridTemplateColumns = `120px repeat(${selectedTraits.length}, 1fr)`;
    headerRow.style.marginBottom = '10px';
    
    // Empty corner cell
    const cornerCell = document.createElement('div');
    headerRow.appendChild(cornerCell);
    
    // Trait headers
    selectedTraits.forEach(trait => {
        const cell = document.createElement('div');
        cell.textContent = formatTraitName(trait);
        cell.style.textAlign = 'center';
        cell.style.fontSize = '0.9rem';
        cell.style.color = '#eee';
        headerRow.appendChild(cell);
    });
    
    container.appendChild(headerRow);
    
    // Create rows for each model
    models.forEach(model => {
        const row = document.createElement('div');
        row.style.display = 'grid';
        row.style.gridTemplateColumns = `120px repeat(${selectedTraits.length}, 1fr)`;
        row.style.marginBottom = '5px';
        
        // Model label
        const modelLabel = document.createElement('div');
        modelLabel.textContent = model.toUpperCase();
        modelLabel.style.paddingRight = '10px';
        modelLabel.style.textAlign = 'right';
        modelLabel.style.color = '#eee';
        row.appendChild(modelLabel);
        
        // Score cells
        const assessment = assessmentData.assessments.find(a => a.model === model);
        
        selectedTraits.forEach(trait => {
            const cell = document.createElement('div');
            cell.className = 'heatmap-cell';
            
            const score = assessment ? (assessment.traits[trait] || 0) : 0;
            const intensity = Math.round(score * 255);
            const color = `rgba(74, 144, 226, ${score})`; // Updated to blue
            
            cell.style.backgroundColor = color;
            cell.textContent = score.toFixed(3);
            cell.style.color = score > 0.5 ? '#fff' : '#bbb';
            cell.style.padding = '10px';
            cell.style.textAlign = 'center';
            
            cell.addEventListener('click', () => {
                updateDetailsPanel(model, trait, score);
            });
            
            row.appendChild(cell);
        });
        
        container.appendChild(row);
    });
}

// ============================================
// UI Helper Functions
// ============================================

function switchView(viewMode) {
    // Hide all chart wrappers
    document.querySelectorAll('.chart-wrapper').forEach(wrapper => {
        wrapper.style.display = 'none';
    });
    
    // Show selected view
    switch (viewMode) {
        case 'radar':
            document.getElementById('radarChartWrapper').style.display = 'block';
            break;
        case 'bar':
            document.getElementById('barChartWrapper').style.display = 'block';
            break;
        case 'timeline':
            document.getElementById('timelineChartWrapper').style.display = 'block';
            break;
        case 'heatmap':
            document.getElementById('heatmapWrapper').style.display = 'block';
            break;
    }
    
    // Update visualization
    updateVisualizations();
}

function updateDetailsPanel(model, trait, score) {
    const detailsContent = document.getElementById('detailsContent');
    
    // Find the most recent assessment for this model that has this trait
    const assessment = assessmentData.assessments
        .filter(a => {
            // Handle both string model names and uppercase labels
            const modelName = typeof model === 'string' ? model.toLowerCase() : model;
            return a.model.toLowerCase() === modelName.toLowerCase() && a.traits && a.traits[trait] !== undefined;
        })
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))[0];
    
    const scoringMethod = assessment?.metadata?.scoring_method || 'unknown';
    
    // Determine score interpretation
    let interpretation = '';
    let emoji = '';
    
    if (score >= 0.8) {
        interpretation = 'Excellent consciousness indicators';
        emoji = '🌟';
    } else if (score >= 0.6) {
        interpretation = 'Good consciousness capabilities';
        emoji = '✅';
    } else if (score >= 0.4) {
        interpretation = 'Moderate consciousness signs';
        emoji = '⚠️';
    } else if (score >= 0.2) {
        interpretation = 'Weak consciousness indicators';
        emoji = '❓';
    } else {
        interpretation = 'Minimal consciousness signs';
        emoji = '❌';
    }
    
    detailsContent.innerHTML = `
        <div class="detail-item">
            <strong>Model:</strong> ${model.toUpperCase()}
        </div>
        <div class="detail-item">
            <strong>Trait:</strong> ${formatTraitName(trait)}
        </div>
        <div class="detail-item">
            <strong>Score:</strong> ${score.toFixed(3)}
        </div>
        <div class="detail-item">
            <strong>Interpretation:</strong> ${emoji} ${interpretation}
        </div>
    `;
}

function displayLatestAssessment() {
    const latestContent = document.getElementById('latestContent');
    
    if (!assessmentData.assessments || assessmentData.assessments.length === 0) {
        latestContent.innerHTML = '<p class="placeholder">No assessments yet.</p>';
        return;
    }
    
    const latest = assessmentData.assessments[0];
    const model = latest.model;
    
    let html = `<div class="latest-info">`;
    
    // Show composite profile if available
    if (assessmentData.composite_profile && assessmentData.composite_profile[model]) {
        const composite = assessmentData.composite_profile[model];
        html += `
            <h4>Composite Profile for ${model.toUpperCase()}</h4>
            <p><strong>Overall Score:</strong> ${composite.overall_score.toFixed(3)}</p>
            <p><strong>Traits Assessed:</strong></p>
            <ul style="margin-left: 20px;">
        `;
        
        for (const [trait, score] of Object.entries(composite.traits)) {
            const updated = composite.last_updated[trait];
            const date = updated ? new Date(updated).toLocaleDateString() : 'Unknown';
            
            // Find the scoring method for this trait from recent assessments
            const traitAssessment = assessmentData.assessments.find(a => 
                a.model === model && 
                a.traits[trait] !== undefined
            );
            const scoringMethod = traitAssessment?.metadata?.scoring_method || 'unknown';
            const methodBadge = getScoringMethodBadge(scoringMethod);
            
            html += `<li>${formatTraitName(trait)}: ${score.toFixed(3)} ${methodBadge} <small>(${date})</small></li>`;
        }
        
        html += `</ul>`;
    }
    
    // Show the latest individual assessment with scoring method
    html += `
        <h4>Latest Assessment Run</h4>
        <p><strong>Date:</strong> ${new Date(latest.timestamp).toLocaleString()}</p>
        <p><strong>Model:</strong> ${latest.model.toUpperCase()}</p>
        <p><strong>Scoring Method:</strong> ${getScoringMethodBadge(latest.metadata?.scoring_method || 'keyword')}</p>
        <p><strong>Traits Tested:</strong> ${latest.traits_tested.join(', ')}</p>
    `;
    
    if (latest.metadata?.duration) {
        html += `<p><strong>Duration:</strong> ${latest.metadata.duration.toFixed(1)}s</p>`;
    }
    
    if (latest.metadata?.partial_run) {
        html += `<p><em>⚠️ This was a partial run (not all traits tested)</em></p>`;
    }
    
    html += '</div>';
    
    latestContent.innerHTML = html;
}

function formatTraitName(trait) {
    return trait
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
}

function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loadingScreen');
    loadingScreen.classList.add('hidden');
}

function showError(message) {
    const detailsContent = document.getElementById('detailsContent');
    detailsContent.innerHTML = `
        <div class="error-message" style="color: #4A90E2;"> <!-- Updated to blue -->
            <strong>⚠️ Error:</strong> ${message}
        </div>
    `;
}

function getScoringMethodBadge(method) {
    const badges = {
        'keyword': '<span class="method-badge keyword-badge">Keyword</span>',
        'geval': '<span class="method-badge geval-badge">G-Eval</span>',
        'hybrid': '<span class="method-badge hybrid-badge">Hybrid</span>',
        'unknown': '<span class="method-badge unknown-badge">Unknown</span>'
    };
    return badges[method] || badges['unknown'];
}

function addScoringMethodComparison() {
    // This could be added as a new view mode
    const container = document.createElement('div');
    container.id = 'scoringComparison';
    container.className = 'scoring-comparison';
    
    // Group assessments by model and trait
    const comparisons = {};
    
    assessmentData.assessments.forEach(assessment => {
        const key = `${assessment.model}_${Object.keys(assessment.traits)[0]}`;
        if (!comparisons[key]) {
            comparisons[key] = [];
        }
        comparisons[key].push({
            method: assessment.metadata?.scoring_method || 'keyword',
            score: Object.values(assessment.traits)[0],
            timestamp: assessment.timestamp
        });
    });
    
    // Display comparisons
    let html = '<h3>Scoring Method Comparisons</h3>';
    for (const [key, scores] of Object.entries(comparisons)) {
        if (scores.length > 1) {
            const [model, trait] = key.split('_');
            html += `
                <div class="comparison-item">
                    <h4>${model.toUpperCase()} - ${formatTraitName(trait)}</h4>
                    <div class="score-bars">
            `;
            
            scores.forEach(s => {
                const width = s.score * 100;
                html += `
                    <div class="score-bar">
                        <span class="bar-label">${getScoringMethodBadge(s.method)}</span>
                        <div class="bar-container">
                            <div class="bar-fill" style="width: ${width}%; background: ${scoringMethodColors[s.method] || '#666'}"></div>
                            <span class="bar-value">${s.score.toFixed(3)}</span>
                        </div>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
    }
    
    container.innerHTML = html;
    return container;
}
// ============================================
// Utility Functions
// ============================================

// Add smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        // Update active state
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        
        // Filter assessments
        filterByScoringMethod(e.target.dataset.method);
    });
});

let currentScoringFilter = 'all';
currentScoringFilter = 'all'; // Ensure it's initialized

function filterByScoringMethod(method) {
    currentScoringFilter = method;
    updateVisualizations();
    console.log(`Filter set to: ${method}`);
}

function getFilteredAssessments() {
    if (currentScoringFilter === 'all') {
        return assessmentData.assessments;
    }
    const filtered = assessmentData.assessments.filter(a => 
        a.metadata?.scoring_method === currentScoringFilter
    );
    
    // If no results for the selected filter, show a message
    if (filtered.length === 0 && currentScoringFilter !== 'all') {
        console.log(`No assessments found with ${currentScoringFilter} scoring method`);
    }
    
    return filtered;
}

// Export functions for debugging
window.debugData = () => console.log(assessmentData);
window.refreshData = () => location.reload();