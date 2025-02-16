// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Mission card hover effects
    const missionCards = document.querySelectorAll('.mission-card:not(.mission-locked)');
    missionCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Quiz form validation
    const quizForm = document.querySelector('#quiz-form');
    if (quizForm) {
        quizForm.addEventListener('submit', function(e) {
            const unansweredQuestions = [];
            const questions = this.querySelectorAll('.question-card');
            
            questions.forEach((question, index) => {
                const answered = question.querySelector('input[type="radio"]:checked');
                if (!answered) {
                    unansweredQuestions.push(index + 1);
                }
            });

            if (unansweredQuestions.length > 0) {
                e.preventDefault();
                alert(`Please answer question(s): ${unansweredQuestions.join(', ')}`);
            } else {
                if (!confirm('Are you sure you want to submit your answers?')) {
                    e.preventDefault();
                }
            }
        });
    }

    // Achievement notification
    function showAchievement(title, message) {
        const notification = document.createElement('div');
        notification.className = 'achievement-notification';
        notification.innerHTML = `
            <div class="achievement-content">
                <h4>🏆 ${title}</h4>
                <p>${message}</p>
            </div>
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Timer for quiz (if on quiz page)
    if (document.querySelector('.question-card')) {
        let timeLeft = 1800; // 30 minutes
        const timerDisplay = document.createElement('div');
        timerDisplay.className = 'quiz-timer';
        document.querySelector('.card-header').appendChild(timerDisplay);

        const timer = setInterval(() => {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            timerDisplay.textContent = `Time Remaining: ${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            if (timeLeft <= 300) { // Last 5 minutes
                timerDisplay.classList.add('timer-warning');
            }
            
            if (timeLeft <= 0) {
                clearInterval(timer);
                document.querySelector('#quiz-form').submit();
            }
            timeLeft--;
        }, 1000);
    }

    // Dynamic progress bar for missions
    const updateProgress = () => {
        const completedMissions = document.querySelectorAll('.mission-card .alert-success').length;
        const totalMissions = document.querySelectorAll('.mission-card').length;
        const progressPercentage = (completedMissions / totalMissions) * 100;
        
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = `${progressPercentage}%`;
            progressBar.setAttribute('aria-valuenow', progressPercentage);
            progressBar.textContent = `${Math.round(progressPercentage)}% Complete`;
        }
    };

    updateProgress();
});