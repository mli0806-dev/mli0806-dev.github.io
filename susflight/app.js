// Initializes values for the app
async function init() {
    // Get the list of destinations from data folder
    const routes = await fetch('data/routes.json').then(response => response.json());
    const saf_levies = await fetch('data/saf_levies.json').then(response => response.json());

    console.log(routes.length);

    // Initializes dropdown menu for destinations
    const dropdown = document.getElementById('destination');

    // Creates the dropdown menu for destinations using the routes.json file
    for (const route of routes) {
        const option = document.createElement('option');
        option.value = route.iata_code;
        option.textContent = route.city + ' (' + route.iata_code + ')';
        dropdown.appendChild(option);
    }

    // Initializes the chart for CO2 emissions
    const co2Chart = new Chart(document.getElementById('co2Chart'), {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{label: 'Estimated CO2 Emissions per Passenger (kg)', data: []}]
        },
        options: {responsive: true, maintainAspectRatio: false, scales: {y: {beginAtZero: true}}}
    });

    // Shows the results of the selected destination and cabin class through innerHTML
    function showResults() {
        const iataCode = dropdown.value;
        const route = routes.find(r => r.iata_code === iataCode);
        const cabin = document.querySelector('input[name="cabin"]:checked').value;
        const price = saf_levies[route.saf_band][cabin];
        const cabinmultiplier = cabin === 'premium' ? 3 : 1; // JS if statement: Business/First class has triple the space per passenger
        const co2_per_passenger_adjusted = route.co2_per_passenger * cabinmultiplier; // Adjusts CO2 emissions based on cabin class

        document.getElementById('results').innerHTML = `
            <br><h3>Results</h3>
            <p>Destination: ${route.city} (${route.iata_code})</p>
            <p>Distance: ${route.distance_from_singapore} km</p>
            <p>Aircraft Type: ${route.aircraft}</p>
            <p>Estimated CO2 Emissions per Passenger: ${co2_per_passenger_adjusted.toFixed(2)} kg</p>
            <p>Estimated SAF levy: S$${price.toFixed(2)}</p>
        `; // Lol innerHTML bad but basically no XSS possible so idc

        // Initializes samplecodes array with some default destinations, and adds the selected destination to the array if it is not already present
        const samplecodes = ['LAX', 'JFK', 'LHR', 'HND', 'SYD', 'DXB', 'KUL', "HKG"];
        if (!samplecodes.includes(route.iata_code)) {
            samplecodes.push(route.iata_code);
        }

        // Updates the chart with the CO2 emissions for the selected destination and some sample destinations
        const samples = samplecodes.map(code => routes.find(r => r.iata_code === code));
        samples.sort((a, b) => a.co2_per_passenger - b.co2_per_passenger); // Sorts the samples by CO2 emissions
        co2Chart.data.labels = samples.map(r => r.city + ' (' + r.iata_code + ')');
        co2Chart.data.datasets[0].data = samples.map(r => r.co2_per_passenger * cabinmultiplier);
        co2Chart.data.datasets[0].backgroundColor = samples.map(r => r.iata_code === route.iata_code ? 'lightgreen' : 'lightblue'); // Checks if the sample is the selected destination and colors it light green if it is, and light blue if it is not
        co2Chart.update();
    }

    // Checks for changes in the dropdown and calls showResults when a change is detected
    dropdown.addEventListener('change', showResults);

    for (const button of document.querySelectorAll('input[name="cabin"]')) {
        button.addEventListener('change', showResults);
    }

    showResults(); // Shows default results when the page is first loaded
}

// Calls init to start app
init();
