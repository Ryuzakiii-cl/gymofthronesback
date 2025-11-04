// --- SweetAlerts para mensajes de Django ---
document.addEventListener("DOMContentLoaded", () => {
  // Busca los mensajes de Django en data attributes si los pasas desde la plantilla
  const alertBox = document.getElementById("django-alert");
  if (!alertBox) return;

  const tipo = alertBox.dataset.tipo; // success, error, warning, info
  const mensaje = alertBox.dataset.mensaje;

  if (!tipo || !mensaje) return;

  // Configuración del ícono
  let icono = "info";
  if (tipo.includes("success")) icono = "success";
  if (tipo.includes("error")) icono = "error";
  if (tipo.includes("warning")) icono = "warning";

  Swal.fire({
    icon: icono,
    title:
      tipo === "success"
        ? "✅ Operación exitosa"
        : tipo === "error"
        ? "❌ Error"
        : "ℹ️ Aviso",
    text: mensaje,
    confirmButtonColor: "#212529",
    confirmButtonText: "Aceptar",
    background: "#fff",
    color: "#000",
    customClass: {
      popup: "rounded-4 shadow-lg",
      confirmButton: "fw-bold px-4 py-2",
    },
  });
});
