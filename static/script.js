document.addEventListener('DOMContentLoaded', function() {
    // Initialize Select2 withsearch functionality
    $('#movieSelect').select2({
        placeholder: 'Type or select a movie...',
        allowClear: true,
        theme: 'classic',
        width: '100%',
        minimumInputLength: 1, // Require at least 1 character to start searching
        matcher: matchCustom
    });

    // Theme Switcher
    const toggleSwitch = document.querySelector('#checkbox');
    const currentTheme = localStorage.getItem('theme');

    if (currentTheme) {
        document.documentElement.setAttribute('data-theme', currentTheme);
        if (currentTheme === 'dark') {
            toggleSwitch.checked = true;
        }
    }

    function switchTheme(e) {
        if (e.target.checked) {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
        }
    }

    toggleSwitch.addEventListener('change', switchTheme);

    // Movie Recommendations Logic
    const recommendBtn = document.getElementById('showRecommendations');
    const grid = document.getElementById('recommendationsGrid');

    // Initially disable the button
    recommendBtn.disabled = true;

    // Enable buttonwhen a movie is selected
    $('#movieSelect').on('select2:select', function(e) {
        recommendBtn.disabled = false;
        recommendBtn.classList.add('active');
    });

    // Disable button when selection is cleared
    $('#movieSelect').on('select2:clear', function(e) {
        recommendBtn.disabled = true;
        recommendBtn.classList.remove('active');
        grid.innerHTML = ''; // Clear previous recommendations
    });

    // Custom matcher function for better search
    function matchCustom(params, data) {
        // If there are no search terms, return all of the data
        if ($.trim(params.term) === '') {
            return data;
        }

        // Do not display the item if there is no 'text' property
        if (typeof data.text === 'undefined') {
            return null;
        }

        // `params.term` should be the term that is used for searching
        // `data.text` is the text that is displayed for the data object
        if (data.text.toLowerCase().indexOf(params.term.toLowerCase()) > -1) {
            return data;
        }

        // Return `null` if the term should not be displayed
        return null;
    }

    recommendBtn.addEventListener('click', function() {
        const selectedMovie = $('#movieSelect').val();
        if (selectedMovie) {
            // Show loading state with animation
            recommendBtn.disabled = true;
            recommendBtn.textContent = 'Finding Movies...';
            grid.innerHTML = `
                <div class="loading">
                    <div>Discovering great movies similar to "${selectedMovie}"...</div>
                </div>`;

            fetch('/get_recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    movie: selectedMovie
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                grid.innerHTML = '';
                
                if (data.length === 0) {
                    grid.innerHTML = `
                        <div class="error">
                            No recommendations found for "${selectedMovie}". Please try another movie.
                        </div>`;
                    return;
                }
                
                data.forEach(movie => {
                    const movieCard = document.createElement('div');
                    movieCard.className = 'movie-card';
                    movieCard.innerHTML = `
                        <img src="${movie.poster_url}" alt="${movie.title}" 
                             onerror="this.src='https://via.placeholder.com/300x450?text=No+Poster+Available'">
                        <h3>${movie.title}</h3>
                    `;
                    grid.appendChild(movieCard);
                });
            })
            .catch(error => {
                console.error('Error:', error);
                grid.innerHTML = `
                    <div class="error">
                        Oops! Something went wrong while fetching recommendations. Please try again.
                    </div>`;
            })
            .finally(() => {
                // Reset button state
                recommendBtn.disabled = false;
                recommendBtn.classList.add('active');
                recommendBtn.textContent = 'Show Recommendations';
            });
        }
    });

    // Update Select2 theme when switching dark/light mode
    toggleSwitch.addEventListener('change', function() {
        setTimeout(() => {
            $('#movieSelect').select2('destroy');
            $('#movieSelect').select2({
                placeholder: 'Type or select a movie...',
                allowClear: true,
                theme: 'classic',
                width: '100%',
                minimumInputLength: 1, // Require at least 1 characterto start searching
                matcher: matchCustom
            });
        }, 100);
    });
});

// Add some loading and error styles
const additionalStyles = `
.loading, .error {
    text-align: center;
    padding: 20px;
    font-size: 18px;
    color: #666;
}

.error {
    color: #ff4444;
}
`;

// Add the styles to the page
const styleSheet = document.createElement("style");
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

