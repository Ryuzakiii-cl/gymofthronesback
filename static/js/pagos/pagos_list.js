// ✅ Confirmación al eliminar
function confirmarEliminacion(pagoId) {
  Swal.fire({
    title: "¿Eliminar pago?",
    text: "Esta acción no se puede deshacer.",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#d33",
    cancelButtonColor: "#6c757d",
    confirmButtonText: "Sí, eliminar",
    cancelButtonText: "Cancelar"
  }).then(result => {
    if (result.isConfirmed) {
      window.location.href = `/pagos/eliminar/${pagoId}/`;
    }
  });
}

// ✅ SweetAlert según el querystring
const params = new URLSearchParams(window.location.search);
if (params.has("success")) {
  let msg = "";
  switch (params.get("success")) {
    case "created":
      msg = "✅ Pago registrado correctamente.";
      break;
    case "updated":
      msg = "✅ Pago actualizado correctamente.";
      break;
    case "deleted":
      msg = "🗑️ Pago eliminado correctamente.";
      break;
  }
  if (msg) {
    Swal.fire({
      icon: "success",
      title: msg,
      timer: 1500,
      showConfirmButton: false
    });
  }
}
