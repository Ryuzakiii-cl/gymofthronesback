document.addEventListener("DOMContentLoaded", () => {
  // ✅ Detectar mensaje de éxito en la URL
  const params = new URLSearchParams(window.location.search);
  const success = params.get("success");

  if (success) {
    let config = {
      icon: "success",
      confirmButtonColor: "#212529",
      confirmButtonText: "Aceptar",
    };

    if (success === "created") {
      config.title = "✅ Plan creado correctamente";
      config.text = "El nuevo plan ha sido registrado con éxito.";
    } else if (success === "updated") {
      config.title = "✏️ Plan actualizado correctamente";
      config.text = "Los cambios se guardaron exitosamente.";
    } else if (success === "deleted") {
      config.title = "🗑️ Plan eliminado";
      config.text = "El plan fue eliminado del sistema.";
    }

    Swal.fire(config).then(() => {
      // Limpiar el parámetro de la URL
      window.history.replaceState({}, document.title, window.location.pathname);
    });
  }

  // ⚠️ Confirmar eliminación con SweetAlert
  document.querySelectorAll(".eliminar-plan").forEach((boton) => {
    boton.addEventListener("click", (e) => {
      e.preventDefault();
      const url = boton.getAttribute("href");

      Swal.fire({
        title: "¿Eliminar plan?",
        text: "Esta acción no se puede deshacer.",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#6c757d",
        confirmButtonText: "Sí, eliminar",
        cancelButtonText: "Cancelar",
        reverseButtons: true,
      }).then((result) => {
        if (result.isConfirmed) {
          window.location.href = url; // Redirige y activa el SweetAlert al volver
        }
      });
    });
  });
});
