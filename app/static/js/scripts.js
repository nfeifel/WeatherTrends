let placeSelected = false;

function initAutocomplete() {
    const input = document.getElementById('location-input');
    const autocomplete = new google.maps.places.Autocomplete(input);

    // Function to remove the address portion and retain city, zip, and country
    function removeAddressPortion(place) {
        let city = '';
        let region = '';
        let country = '';
        let zipCode = '';
        let fallback = '';  // Fallback for cases like Java or Crete
    
        for (const component of place.address_components) {
            if (component.types.includes('locality')) {
                city = component.long_name;
            } else if (component.types.includes('administrative_area_level_1') || component.types.includes('administrative_area_level_2')) {
                region = component.long_name;  // Use region as fallback
            } else if (component.types.includes('postal_code')) {
                zipCode = component.long_name;
            } else if (component.types.includes('country')) {
                country = component.short_name;
            } else if (component.types.includes('political') || component.types.includes('colloquial_area')) {
                fallback = component.long_name;  // Use as a fallback if no locality or region is found
            }
        }
    
        // Handle the case where locality (city) is not available
        if (!city && region) {
            city = region;
        } else if (!city && !region && fallback) {
            city = fallback;  // Use fallback for cases like Java or Crete
        }
    
        // Construct the cleaned location string without an extra comma
        let cleanedLocation = city;
        if (zipCode) {
            cleanedLocation += `, ${zipCode}`;
        }
        cleanedLocation += `, ${country}`;
    
        return cleanedLocation;
    }
    

    autocomplete.addListener('place_changed', function () {
        const place = autocomplete.getPlace();

        if (place.geometry) {
            placeSelected = true;  // A valid place was selected
            const latitude = place.geometry.location.lat();
            const longitude = place.geometry.location.lng();
            console.log('Latitude:', latitude);
            console.log('Longitude:', longitude);

            // Use the function to remove the address portion
            const cleanedLocation = removeAddressPortion(place);
            console.log('Cleaned Location:', cleanedLocation);

            // Store the cleaned location in a new hidden input field
            document.getElementById('cleaned-location').value = cleanedLocation;

            // Keep the original location-input value intact
        } else {
            placeSelected = false;  // No valid place was selected
        }
    });
}

function displayError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';  // Show the error message
}

function isValidDate(year, month, day) {
    // JavaScript Date object will automatically handle invalid dates like February 31
    const date = new Date(year, month - 1, day);  // Months are zero-indexed in JS
    return (date.getFullYear() === year && date.getMonth() + 1 === month && date.getDate() === day);
}

function validateAndSubmitForm(event) {
    const locationInput = document.getElementById('location-input').value.trim();
    const startYear = parseInt(document.getElementById('start_year').value);
    const endYear = parseInt(document.getElementById('end_year').value);
    const month = parseInt(document.getElementById('month').value);
    const day = parseInt(document.getElementById('day').value);

    // Reset any previous error messages
    document.getElementById('error-message').style.display = 'none';

    // **Check 1: Ensure the text box is not empty**
    if (locationInput === '') {
        displayError('The location field cannot be empty. Please enter a location.');
        event.preventDefault();  // Prevent form submission
        return;
    }

    // **Check 2: Ensure the text entered matches one of the options from the Places API**
    if (!placeSelected) {
        displayError('The location you entered does not match any known places. Please select a valid location from the suggestions.');
        event.preventDefault();  // Prevent form submission
        return;
    }

    // **Check 3: Ensure end_year is greater than or equal to start_year**
    if (endYear < startYear) {
        displayError('End Year must be the same as or later than Start Year.');
        event.preventDefault();  // Prevent form submission
        return;
    }

    // **Check 4: Ensure the month + day combination is a valid date**
    if (!isValidDate(startYear, month, day)) {
        displayError('The date you entered is not valid. Please select a valid month and day.');
        event.preventDefault();  // Prevent form submission
        return;
    }

    // If all validations pass, show the spinner and proceed with form submission
    showSpinner();
    return true;  // Allow form submission to proceed
    placeSelected = false;
}

window.onload = function() {
    initAutocomplete();  // Initialize Google Places Autocomplete
    document.getElementById('weatherForm').onsubmit = validateAndSubmitForm;
};

google.maps.event.addDomListener(window, 'load', initAutocomplete);

// Handle form submission with loading indicator
document.getElementById("weatherForm").onsubmit = function() {
    document.getElementById("loading").style.display = "block";
};

document.addEventListener('DOMContentLoaded', function () {
    initAutocomplete();
});

autocomplete.addListener('place_changed', function () {
    const place = autocomplete.getPlace();

    if (place.geometry) {
        const latitude = place.geometry.location.lat();
        const longitude = place.geometry.location.lng();
        
        console.log('Latitude:', latitude);
        console.log('Longitude:', longitude);

        // Initialize a variable to hold the country code
        let countryCode = '';

        // Loop through the address components to find the country
        for (const component of place.address_components) {
            if (component.types.includes('country')) {
                countryCode = component.short_name;
                break;
            }
        }

        console.log('Country Code:', countryCode);
    } else {
        console.log('No geometry information available for this place.');
    }
});

function showSpinner() {
    const loadingDiv = document.getElementById('loading');
    loadingDiv.style.display = 'block';  // Show the spinner and loading message
}