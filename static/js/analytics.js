/* Analytics Page JavaScript */

// Initialize charts
document.addEventListener('DOMContentLoaded', function() {
    initializeTalentDistributionChart();
    initializeInjuryRiskDistributionChart();
    initializePerformanceTrendsChart();
    initializeInjuryTrendsChart();
    loadAnalyticsData();
});

// Fetch dashboard stats
async function loadAnalyticsData() {
    const stats = await makeAPICall('/api/dashboard-stats', 'GET');
    
    if (stats) {
        // Update high-risk athletes list
        document.getElementById('highRiskAthletesList').innerHTML = 
            `<div class="text-center"><strong>${stats.high_risk_athletes}</strong> Athletes</div>`;
        
        // Update elite athletes list
        document.getElementById('eliteAthletesList').innerHTML = 
            `<div class="text-center"><strong>${stats.high_potential_athletes}</strong> Athletes</div>`;
    }
}

// Talent Distribution Chart
function initializeTalentDistributionChart() {
    const ctx = document.getElementById('talentDistributionChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['0-30', '30-50', '50-70', '70-100'],
            datasets: [{
                label: 'Talent Potential Distribution',
                data: [15, 45, 65, 35],
                backgroundColor: [
                    'rgba(220, 53, 69, 0.7)',
                    'rgba(255, 193, 7, 0.7)',
                    'rgba(40, 167, 69, 0.7)',
                    'rgba(0, 123, 255, 0.7)'
                ],
                borderColor: [
                    '#dc3545',
                    '#ffc107',
                    '#28a745',
                    '#007bff'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Athletes'
                    }
                }
            }
        }
    });
}

// Injury Risk Distribution Chart
function initializeInjuryRiskDistributionChart() {
    const ctx = document.getElementById('injuryRiskDistributionChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Low Risk', 'Medium Risk', 'High Risk'],
            datasets: [{
                data: [120, 65, 15],
                backgroundColor: [
                    'rgba(40, 167, 69, 0.7)',
                    'rgba(255, 193, 7, 0.7)',
                    'rgba(220, 53, 69, 0.7)'
                ],
                borderColor: [
                    '#28a745',
                    '#ffc107',
                    '#dc3545'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Performance Trends Chart
function initializePerformanceTrendsChart() {
    const ctx = document.getElementById('performanceTrendsChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Year 1', 'Year 2', 'Year 3', 'Year 4'],
            datasets: [
                {
                    label: 'Average Performance Score',
                    data: [55, 62, 71, 78],
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointBackgroundColor: '#007bff'
                },
                {
                    label: 'Injury Rate (%)',
                    data: [18, 15, 12, 8],
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointBackgroundColor: '#dc3545'
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Athlete Lifecycle Performance (4-Year Track)'
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

// Injury Trends Chart
function initializeInjuryTrendsChart() {
    const ctx = document.getElementById('injuryTrendsChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [{
                label: 'Injuries Reported',
                data: [5, 4, 6, 3, 7, 5, 4, 8, 6, 5, 4, 3],
                backgroundColor: 'rgba(220, 53, 69, 0.7)',
                borderColor: '#dc3545',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Training Hours Chart
function initializeTrainingHoursChart() {
    const ctx = document.getElementById('trainingHoursChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['High Load', 'Normal Load', 'Low Load'],
            datasets: [{
                data: [45, 135, 20],
                backgroundColor: [
                    'rgba(220, 53, 69, 0.7)',
                    'rgba(40, 167, 69, 0.7)',
                    'rgba(23, 162, 184, 0.7)'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom'
                }
            }
        }
    });
}

// Initialize (placeholder for additional charts)
function initializeSleepDeprivationChart() {
    // Implementation similar to above
}

function initializePreviousInjuryChart() {
    // Implementation similar to above
}

function initializeRecoveryTimelineChart() {
    const ctx = document.getElementById('recoveryTimelineChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Sprain', 'Strain', 'Fracture', 'Concussion', 'Tendinitis'],
            datasets: [{
                label: 'Average Recovery (days)',
                data: [21, 28, 42, 35, 45],
                backgroundColor: [
                    'rgba(255, 193, 7, 0.7)',
                    'rgba(255, 193, 7, 0.7)',
                    'rgba(220, 53, 69, 0.7)',
                    'rgba(220, 53, 69, 0.7)',
                    'rgba(220, 53, 69, 0.7)'
                ],
                borderColor: '#ffc107',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    });
}
