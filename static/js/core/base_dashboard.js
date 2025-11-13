// ---------------------------
//  SUBMENÚ RESERVAS
// ---------------------------
(function () {
    const toggle = document.getElementById('toggleReservas');
    const submenu = document.getElementById('submenuReservas');
    const arrow = document.querySelector('.arrow');
    if (toggle) {
        toggle.addEventListener('click', () => {
            submenu.classList.toggle('show');
            arrow.classList.toggle('rotate');
        });
    }
})();


// ----------------------------------------
//  CLIMA — GPS REAL + OPENWEATHERMAP
// ----------------------------------------

const OPENWEATHER_KEY = "2ab2f2161c225383a63ad8e77084caa1";

// --- UI Helpers ---
function setWeatherUI(icon, temp, location) {
    document.getElementById("weather-icon").innerText = icon;
    document.getElementById("weather-temp").innerText = temp;
    document.getElementById("weather-location").innerText = location;
}

// --- Selección de icono ---
function chooseIcon(condition) {
    condition = condition.toLowerCase();

    if (condition.includes("cloud")) return "☁️";
    if (condition.includes("rain")) return "🌧️";
    if (condition.includes("clear")) return "☀️";
    if (condition.includes("storm")) return "⛈️";
    if (condition.includes("snow")) return "❄️";
    if (condition.includes("mist") || condition.includes("fog")) return "🌫️";

    return "🌤️";
}

// --- Obtener clima y comuna REAL por GPS ---
async function getWeatherByCoords(lat, lon) {
    try {
        // 1) Clima desde OpenWeather
        const weatherURL = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${OPENWEATHER_KEY}&units=metric&lang=es`;
        const weatherData = await fetch(weatherURL).then(r => r.json());

        if (!weatherData || weatherData.cod !== 200) throw new Error("Weather API error");

        const icon = chooseIcon(weatherData.weather[0].main);
        const temp = `${Math.round(weatherData.main.temp)}°C`;

        // 2) Reverse geocoding DETALLADO (comuna real)
        const reverseURL = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=10&addressdetails=1`;
        const geo = await fetch(reverseURL).then(r => r.json());

        const comuna =
            geo.address.suburb ||
            geo.address.city ||
            geo.address.town ||
            geo.address.village ||
            geo.address.municipality ||
            "Ubicación desconocida";

        setWeatherUI(icon, temp, comuna);

    } catch (error) {
        console.log("Error de clima o geolocalización:", error);
        setWeatherUI("⚠️", "--°C", "Sin datos");
    }
}

// --- Inicio ---
function initWeather() {
    if (!navigator.geolocation) {
        setWeatherUI("⚠️", "--°C", "GPS no soportado");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        pos => {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            getWeatherByCoords(lat, lon);
        },
        err => {
            console.log("GPS bloqueado:", err);
            setWeatherUI("⚠️", "--°C", "GPS bloqueado");
        }
    );
}

document.addEventListener("DOMContentLoaded", initWeather);
