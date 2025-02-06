// Basic game interactions
document.addEventListener('DOMContentLoaded', function() {
    // Handle choice selection
    const choiceItems = document.querySelectorAll('.choice-item');
    choiceItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove selected class from all choices
            choiceItems.forEach(choice => choice.classList.remove('selected'));
            // Add selected class to clicked choice
            this.classList.add('selected');
        });
    });
});