document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");

  form.addEventListener("submit", (e) => {
    const precio = parseFloat(document.getElementById("precio").value);
    const duracion = parseInt(document.getElementById("duracion").value);

    if (precio <= 0 || isNaN(precio)) {
      e.preventDefault();
      Swal.fire("⚠️ Error", "El precio debe ser un número positivo.", "warning");
      return;
    }

    if (duracion <= 0 || isNaN(duracion)) {
      e.preventDefault();
      Swal.fire("⚠️ Error", "La duración debe ser un número mayor que 0.", "warning");
      return;
    }
  });
});
