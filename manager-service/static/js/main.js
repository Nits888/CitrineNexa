$(document).ready(function() {
    // Check local storage for theme
    if (localStorage.getItem('theme') === 'dark') {
        $('body').addClass('dark-theme');
        $('.sun-icon').hide();
        $('.moon-icon').show();
    }

    // Toggle theme on SVG icon click
    $('#themeToggleIcon').on('click', function() {
        if ($('body').hasClass('dark-theme')) {
            $('body').removeClass('dark-theme');
            localStorage.setItem('theme', 'light');
            $('.sun-icon').show();
            $('.moon-icon').hide();
        } else {
            $('body').addClass('dark-theme');
            localStorage.setItem('theme', 'dark');
            $('.sun-icon').hide();
            $('.moon-icon').show();
        }
    });
});

