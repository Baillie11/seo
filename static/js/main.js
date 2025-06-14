function submitSubscribe() {
    const email = document.getElementById('email').value;
    const featureUpdates = document.getElementById('featureUpdates').checked;
    const seoTips = document.getElementById('seoTips').checked;

    // Here you would typically send this to your backend
    console.log('Subscription request:', { email, featureUpdates, seoTips });
    
    // Show success message
    alert('Thank you for subscribing! We\'ll keep you updated with the latest features.');
    
    // Close the modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('subscribeModal'));
    modal.hide();
} 