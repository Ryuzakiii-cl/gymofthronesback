function actualizarResumen() {
    const planSelect = document.getElementById("plan");
    const selected = planSelect.options[planSelect.selectedIndex];
    const precio = selected.getAttribute("data-precio");
    const duracion = selected.getAttribute("data-duracion");
    const beneficios = selected.getAttribute("data-beneficios");

    document.getElementById("precio").value = precio ? `$${precio}` : "";
    document.getElementById("duracion").value = duracion || "";

    const resumen = document.getElementById("planResumen");
    const textoBeneficios = document.getElementById("beneficios");
    if (beneficios) {
        textoBeneficios.textContent = beneficios;
        resumen.style.display = "block";
    } else {
        resumen.style.display = "none";
    }
}