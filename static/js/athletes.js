/* Athletes Page JavaScript */

// Submit add athlete form
async function submitAddAthlete() {
    const form = document.getElementById('addAthleteForm');
    const data = getFormData(form);
    
    const result = await makeAPICall('/api/athletes', 'POST', data);
    
    if (result) {
        showAlert('Athlete added successfully!', 'success');
        form.reset();
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('addAthleteModal'));
        modal.hide();
        
        // Reload page
        setTimeout(() => {
            location.reload();
        }, 1000);
    }
}

// Edit athlete
function editAthlete(athleteId) {
    // Placeholder for edit functionality
    alert('Edit functionality - Athlete ID: ' + athleteId);
}

// Delete athlete
async function deleteAthlete(athleteId) {
    if (confirm('Are you sure you want to delete this athlete?')) {
        const result = await makeAPICall(`/api/athletes/${athleteId}`, 'DELETE');
        
        if (result) {
            showAlert('Athlete deleted successfully!', 'success');
            setTimeout(() => {
                location.reload();
            }, 1000);
        }
    }
}

// Search athletes
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            const tableBody = document.getElementById('athletesTableBody');
            const rows = tableBody.getElementsByTagName('tr');
            
            Array.from(rows).forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    }

    // Sport filter
    const sportFilter = document.getElementById('sportFilter');
    if (sportFilter) {
        sportFilter.addEventListener('change', function() {
            const filter = this.value.toLowerCase();
            const tableBody = document.getElementById('athletesTableBody');
            const rows = tableBody.getElementsByTagName('tr');
            
            Array.from(rows).forEach(row => {
                if (filter === '') {
                    row.style.display = '';
                } else {
                    const sport = row.cells[2].textContent.toLowerCase();
                    row.style.display = sport.includes(filter) ? '' : 'none';
                }
            });
        });
    }
});
