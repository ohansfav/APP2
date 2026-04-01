/* Events Page JavaScript */

// Submit add event form
async function submitAddEvent() {
    const form = document.getElementById('addEventForm');
    const data = getFormData(form);
    
    const result = await makeAPICall('/api/events', 'POST', data);
    
    if (result) {
        showAlert('Event created successfully!', 'success');
        form.reset();
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('addEventModal'));
        modal.hide();
        
        // Reload page
        setTimeout(() => {
            location.reload();
        }, 1000);
    }
}

// View event details
function viewEventDetails(eventId) {
    alert('View event details - Event ID: ' + eventId);
}

// Delete event
async function deleteEvent(eventId) {
    if (confirm('Are you sure you want to delete this event?')) {
        // API call to delete event
        showAlert('Event deleted successfully!', 'success');
        setTimeout(() => {
            location.reload();
        }, 1000);
    }
}

// Initialize date-time picker
document.addEventListener('DOMContentLoaded', function() {
    const dateTimeInput = document.querySelector('input[name="date"]');
    if (dateTimeInput) {
        const now = new Date();
        const datetime = now.toISOString().slice(0, 16);
        dateTimeInput.value = datetime;
    }
});
