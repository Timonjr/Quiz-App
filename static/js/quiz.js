/**
 * Quiz Timer and Management
 */

let timer;
let remainingSeconds = 0;
let quizSubmitted = false;

/**
 * Initialize the quiz timer with a specified duration
 * @param {number} seconds - Total seconds for the quiz
 * @param {string} displayElementId - ID of the element to display the timer
 * @param {string} formId - ID of the quiz form to submit when time runs out
 */
function initQuizTimer(seconds, displayElementId, formId) {
    remainingSeconds = seconds;
    const timerDisplay = document.getElementById(displayElementId);
    const quizForm = document.getElementById(formId);
    
    // Update timer display
    updateTimerDisplay(timerDisplay);
    
    // Start the timer
    timer = setInterval(function() {
        remainingSeconds--;
        updateTimerDisplay(timerDisplay);
        
        // Update progress bar if exists
        const progressBar = document.getElementById('timerProgressBar');
        if (progressBar) {
            const totalDuration = parseInt(progressBar.getAttribute('data-total-duration'));
            const progressPercentage = (remainingSeconds / totalDuration) * 100;
            progressBar.style.width = progressPercentage + '%';
            
            // Change color based on time remaining
            if (progressPercentage < 25) {
                progressBar.className = 'progress-bar bg-danger';
            } else if (progressPercentage < 50) {
                progressBar.className = 'progress-bar bg-warning';
            }
        }
        
        // Check if time is up
        if (remainingSeconds <= 0) {
            clearInterval(timer);
            if (!quizSubmitted && quizForm) {
                // Create a hidden input to indicate time's up
                const timeUpInput = document.createElement('input');
                timeUpInput.type = 'hidden';
                timeUpInput.name = 'time_up';
                timeUpInput.value = 'true';
                quizForm.appendChild(timeUpInput);
                
                // Submit the form
                quizSubmitted = true;
                quizForm.submit();
            }
        }
    }, 1000);
    
    // Save timer state in localStorage
    saveTimerState();
}

/**
 * Update the timer display with the current remaining time
 * @param {HTMLElement} timerDisplay - Element to show the time
 */
function updateTimerDisplay(timerDisplay) {
    const minutes = Math.floor(remainingSeconds / 60);
    const seconds = remainingSeconds % 60;
    
    // Format time as MM:SS
    timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    // Change color based on time remaining
    if (remainingSeconds < 60) {
        timerDisplay.classList.add('text-danger');
    } else if (remainingSeconds < 300) {
        timerDisplay.classList.add('text-warning');
        timerDisplay.classList.remove('text-danger');
    }
}

/**
 * Save the current timer state to localStorage
 */
function saveTimerState() {
    if (typeof localStorage !== 'undefined') {
        const quizId = document.getElementById('quizId')?.value;
        if (quizId) {
            localStorage.setItem(`quiz_timer_${quizId}`, JSON.stringify({
                remainingSeconds: remainingSeconds,
                timestamp: Date.now()
            }));
        }
    }
}

/**
 * Restore the timer state from localStorage if it exists
 * @returns {number|null} - The remaining seconds, or null if no saved state
 */
function restoreTimerState() {
    if (typeof localStorage !== 'undefined') {
        const quizId = document.getElementById('quizId')?.value;
        if (quizId) {
            const savedState = localStorage.getItem(`quiz_timer_${quizId}`);
            if (savedState) {
                try {
                    const { remainingSeconds, timestamp } = JSON.parse(savedState);
                    const elapsedMs = Date.now() - timestamp;
                    const elapsedSeconds = Math.floor(elapsedMs / 1000);
                    return Math.max(0, remainingSeconds - elapsedSeconds);
                } catch (e) {
                    console.error('Error restoring timer state:', e);
                }
            }
        }
    }
    return null;
}

/**
 * Submit the quiz form
 * @param {string} formId - ID of the quiz form
 */
function submitQuiz(formId) {
    if (confirm('Are you sure you want to submit the quiz? You cannot return to this quiz after submission.')) {
        const quizForm = document.getElementById(formId);
        
        // Add a hidden field for final submission
        const submitInput = document.createElement('input');
        submitInput.type = 'hidden';
        submitInput.name = 'submit_quiz';
        submitInput.value = 'true';
        quizForm.appendChild(submitInput);
        
        quizSubmitted = true;
        clearInterval(timer);
        
        // Clear the timer state from localStorage
        const quizId = document.getElementById('quizId')?.value;
        if (quizId && typeof localStorage !== 'undefined') {
            localStorage.removeItem(`quiz_timer_${quizId}`);
        }
        
        quizForm.submit();
    }
}

/**
 * Handle option selection in the quiz
 * @param {string} optionId - ID of the selected option element
 * @param {string} optionValue - Value of the selected option (A, B, C, D)
 */
function selectOption(optionId, optionValue) {
    // Remove selected class from all options
    const allOptions = document.querySelectorAll('.quiz-option');
    allOptions.forEach(option => {
        option.classList.remove('selected');
    });
    
    // Add selected class to the clicked option
    document.getElementById(optionId).classList.add('selected');
    
    // Update the hidden input value
    document.getElementById('selectedOption').value = optionValue;
}

/**
 * Set up event listeners for quiz form submission
 * @param {string} formId - ID of the quiz form
 */
function setupQuizFormListeners(formId) {
    const quizForm = document.getElementById(formId);
    
    if (quizForm) {
        // Save timer state periodically
        setInterval(saveTimerState, 5000);
        
        // Handle unload events to save state
        window.addEventListener('beforeunload', saveTimerState);
        
        // Handle form submission
        quizForm.addEventListener('submit', function() {
            quizSubmitted = true;
            clearInterval(timer);
            
            // Clear localStorage timer state if this is the final submission
            if (document.getElementById('submit_quiz')?.value === 'true') {
                const quizId = document.getElementById('quizId')?.value;
                if (quizId && typeof localStorage !== 'undefined') {
                    localStorage.removeItem(`quiz_timer_${quizId}`);
                }
            }
        });
    }
}

// Initialize timer state when the page loads
document.addEventListener('DOMContentLoaded', function() {
    const timerDisplay = document.getElementById('quizTimer');
    const quizForm = document.getElementById('quizForm');
    
    if (timerDisplay && quizForm) {
        const savedSeconds = restoreTimerState();
        
        if (savedSeconds !== null) {
            // Use saved timer state
            initQuizTimer(savedSeconds, 'quizTimer', 'quizForm');
        } else {
            // Use the duration from the data attribute
            const duration = parseInt(timerDisplay.getAttribute('data-duration'));
            if (duration) {
                initQuizTimer(duration, 'quizTimer', 'quizForm');
            }
        }
        
        // Set up form listeners
        setupQuizFormListeners('quizForm');
    }
});
