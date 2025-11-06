document.addEventListener("DOMContentLoaded", () => {
  const url = new URL(window.location.href);
  const success = url.searchParams.get("success");
  const error = url.searchParams.get("error");

  // 🔍 BUSCADOR EN TIEMPO REAL + BOTÓN LIMPIAR
  const buscador = document.getElementById('buscador');
  const btnLimpiar = document.getElementById('btnLimpiar');
  const filas = document.querySelectorAll('#tablaSocios tbody tr');

  if (buscador) {
    const filtrar = () => {
      const texto = buscador.value.toLowerCase();
      filas.forEach(fila => {
        const coincide = fila.innerText.toLowerCase().includes(texto);
        fila.style.display = coincide ? '' : 'none';
      });
    };

    buscador.addEventListener('keyup', filtrar);

    // 🔘 Botón para limpiar búsqueda
    if (btnLimpiar) {
      btnLimpiar.addEventListener('click', () => {
        buscador.value = '';
        filtrar();
      });
    }
  }

  // ✅ CONFIRMACIÓN DE ELIMINACIÓN
  document.querySelectorAll(".eliminar-socio").forEach(boton => {
    boton.addEventListener("click", e => {
      e.preventDefault();
      const href = boton.getAttribute("href");

      Swal.fire({
        title: "¿Eliminar socio?",
        text: "Esta acción no se puede deshacer.",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#6c757d",
        confirmButtonText: "Sí, eliminar",
        cancelButtonText: "Cancelar",
        reverseButtons: true,
        customClass: {
          popup: "rounded-4 shadow-lg",
          confirmButton: "fw-bold px-4 py-2",
          cancelButton: "fw-bold px-4 py-2"
        }
      }).then(result => {
        if (result.isConfirmed) {
          window.location.href = href;
        }
      });
    });
  });

  // 🟢 MENSAJES DE ÉXITO
  if (success) {
    let mensaje = "";
    let icon = "success";

    switch (success) {
      case "created":
        mensaje = "✅ Socio creado correctamente.";
        break;
      case "updated":
        mensaje = "✏️ Socio actualizado correctamente.";
        break;
      case "deleted":
        mensaje = "🗑️ Socio eliminado correctamente.";
        break;
      default:
        mensaje = "Operación realizada correctamente.";
    }

    Swal.fire({
      icon,
      title: "Operación exitosa",
      text: mensaje,
      confirmButtonColor: "#212529",
      confirmButtonText: "Aceptar",
      background: "#fff",
      color: "#000",
      customClass: {
        popup: "rounded-4 shadow-lg",
        confirmButton: "fw-bold px-4 py-2",
      },
    }).then(() => {
      window.history.replaceState({}, document.title, window.location.pathname);
    });
  }

  // 🔴 MENSAJES DE ERROR
  if (error) {
    let mensaje = "";
    switch (error) {
      case "exists":
        mensaje = "❌ Ya existe un socio con ese RUT.";
        break;
      default:
        mensaje = "Ocurrió un error inesperado.";
    }

    Swal.fire({
      icon: "error",
      title: "Error",
      text: mensaje,
      confirmButtonColor: "#dc3545",
      background: "#fff",
      color: "#000",
    }).then(() => {
      window.history.replaceState({}, document.title, window.location.pathname);
    });
  }
});
