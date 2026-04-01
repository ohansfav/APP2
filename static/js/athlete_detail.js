/* Athlete Detail Page JavaScript */

// Submit injury risk assessment
async function submitInjuryRiskAssessment(athleteId) {
    const form = document.getElementById('injuryRiskForm');
    const data = getFormData(form);
    data.athlete_id = athleteId;
    
    const result = await makeAPICall('/api/predict/injury-risk', 'POST', data);
    
    if (result) {
        showAlert(
            `Injury Risk Assessment Complete\n` +
            `Risk Score: ${(result.injury_risk_score * 100).toFixed(1)}%\n` +
            `Category: ${result.risk_category}\n` +
            `${result.recommendation}`,
            'info'
        );
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('assessInjuryRiskModal'));
        modal.hide();
        
        // Reload page
        setTimeout(() => {
            location.reload();
        }, 2000);
    }
}

// Submit talent assessment
async function submitTalentAssessment(athleteId) {
    const form = document.getElementById('talentAssessmentForm');
    const data = getFormData(form);
    data.athlete_id = athleteId;
    data.performance_score = 75; // Use athlete's current performance score
    data.age = 20; // Would come from athlete data
    
    const result = await makeAPICall('/api/predict/talent-potential', 'POST', data);
    
    if (result) {
        showAlert(
            `Talent Assessment Complete\n` +
            `Talent Potential: ${result.talent_potential.toFixed(1)}/100\n` +
            `Category: ${result.talent_category}\n` +
            `${result.recommendation}`,
            'success'
        );
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('assessTalentModal'));
        modal.hide();
        
        // Reload page
        setTimeout(() => {
            location.reload();
        }, 2000);
    }
}

// Submit log injury
async function submitLogInjury(athleteId) {
    const form = document.getElementById('logInjuryForm');
    const data = getFormData(form);
    data.athlete_id = athleteId;
    
    const result = await makeAPICall('/api/injuries', 'POST', data);
    
    if (result) {
        showAlert('Injury logged successfully!', 'warning');
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('logInjuryModal'));
        modal.hide();
        
        // Reload page
        setTimeout(() => {
            location.reload();
        }, 1500);
    }
}

// Edit athlete profile
function editAthleteProfile(athleteId) {
    alert('Edit profile functionality - Athlete ID: ' + athleteId);
}

// Initialize date inputs with today's date
document.addEventListener('DOMContentLoaded', function() {
    const dateInput = document.querySelector('input[name="date_occurred"]');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }
});
