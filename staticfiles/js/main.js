// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Existing message fade-out effect
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.transition = 'opacity 0.5s ease-in-out';
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 500);
        }, 5000);
    });

    // Existing nav active state
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-item');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Add answer submission functionality
    function submitAnswer(questionId, choiceId) {
        // Get CSRF token from the meta tag
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

        fetch('/game/submit_answer/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: `question_id=${questionId}&choice_id=${choiceId}`
        })
        .then(response => response.json())
        .then(data => {
            // Update score display immediately
            const scoreDisplay = document.getElementById('score-display');
            if (scoreDisplay) {
                scoreDisplay.textContent = data.score;
                // Add animation class for visual feedback
                scoreDisplay.classList.add('score-updated');
                setTimeout(() => {
                    scoreDisplay.classList.remove('score-updated');
                }, 500);
            }

            // Show explanation
            const explanation = document.getElementById('explanation');
            if (explanation) {
                explanation.textContent = data.explanation;
                explanation.style.display = 'block';
            }

            // Update choice styling
            const choiceElement = document.getElementById(`choice-${choiceId}`);
            if (choiceElement) {
                choiceElement.classList.add(data.result ? 'correct-answer' : 'incorrect-answer');
            }
        })
        .catch(error => {
            console.error('Error submitting answer:', error);
        });
    }

    // Add click event listeners to choice buttons
    const choiceButtons = document.querySelectorAll('.choice-btn');
    choiceButtons.forEach(button => {
        button.addEventListener('click', function() {
            const questionId = this.getAttribute('data-question-id');
            const choiceId = this.getAttribute('data-choice-id');
            submitAnswer(questionId, choiceId);
        });
    });
});