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
//  CLIMA — SEGURO VÍA DJANGO BACKEND
// ----------------------------------------

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

// ------------ LLAMA A DJANGO (SIN API KEY EN JS) ------------
async function getWeatherSecure(lat, lon) {
    try {
        const response = await fetch(`/api/weather/?lat=${lat}&lon=${lon}`);
        const data = await response.json();

        if (data.error) {
            setWeatherUI("⚠️", "--°C", "Sin datos");
            return;
        }

        const icon = chooseIcon(data.condition);
        const temp = `${data.temp}°C`;
        const comuna = data.location;

        setWeatherUI(icon, temp, comuna);

    } catch (error) {
        console.log("Error obteniendo clima:", error);
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
            getWeatherSecure(lat, lon);  // <--- AHORA LLAMA AL BACKEND
        },
        err => {
            console.log("GPS bloqueado:", err);
            setWeatherUI("⚠️", "--°C", "GPS bloqueado");
        }
    );
}

document.addEventListener("DOMContentLoaded", initWeather);
