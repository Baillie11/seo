document.addEventListener('DOMContentLoaded', function() {
    // Get the subscribe form
    const subscribeForm = document.getElementById('subscribeForm');
    if (subscribeForm) {
        subscribeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleSubscribe();
        });
    }
});

async function handleSubscribe() {
    const email = document.getElementById('email').value;
    const featureUpdates = document.getElementById('featureUpdates').checked;
    const seoTips = document.getElementById('seoTips').checked;

    try {
        const response = await fetch('/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                featureUpdates: featureUpdates,
                seoTips: seoTips
            })
        });

        const data = await response.json();
        
        // Show message to user
        alert(data.message);
        
        if (data.success) {
            // Clear the form
            document.getElementById('email').value = '';
            document.getElementById('featureUpdates').checked = true;
            document.getElementById('seoTips').checked = true;
            
            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('subscribeModal'));
            modal.hide();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again later.');
    }
} 