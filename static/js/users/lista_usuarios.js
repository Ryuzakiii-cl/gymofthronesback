document.addEventListener("DOMContentLoaded", () => {
  const hasSwal = typeof window.Swal !== "undefined";

  // ====== MENSAJES GET (?success=..., ?error=...) ======
  const params = new URLSearchParams(window.location.search);
  const success = params.get("success");
  const error = params.get("error");

  if (hasSwal && success) {
    let config = {
      icon: "success",
      confirmButtonColor: "#212529",
      confirmButtonText: "Aceptar",
      customClass: { popup: "rounded-4 shadow-lg" },
    };

    switch (success) {
      case "created":
        config.title = "✅ Usuario creado correctamente";
        config.text = "El nuevo usuario ha sido registrado en el sistema.";
        break;
      case "updated":
        config.title = "✏️ Usuario actualizado correctamente";
        config.text = "Los datos del usuario se modificaron con éxito.";
        break;
      case "deleted":
        config.title = "🗑️ Usuario eliminado";
        config.text = "El usuario ha sido eliminado del sistema.";
        break;
      case "logout":
        config.title = "👋 Sesión cerrada correctamente";
        config.text = "Hasta pronto.";
        break;
      default:
        config = null;
    }
    if (config) {
      Swal.fire(config).then(() => {
        window.history.replaceState({}, document.title, window.location.pathname);
      });
    }
  }

  if (hasSwal && error) {
    let config = {
      icon: "error",
      confirmButtonColor: "#d33",
      confirmButtonText: "Aceptar",
      customClass: { popup: "rounded-4 shadow-lg" },
    };

    switch (error) {
      case "exists":
        config.title = "⚠️ Usuario ya existente";
        config.text = "Ya hay un usuario registrado con ese RUT.";
        config.icon = "warning";
        break;
      case "invalid":
        config.title = "❌ RUT o contraseña incorrectos";
        config.text = "Verifica tus credenciales e intenta nuevamente.";
        break;
      case "sinrol":
        config.title = "🚫 Sin rol asignado";
        config.text = "Tu cuenta no tiene un rol asignado. Contacta al administrador.";
        break;
      default:
        config = null;
    }
    if (config) {
      Swal.fire(config).then(() => {
        window.history.replaceState({}, document.title, window.location.pathname);
      });
    }
  }

  // ====== CONFIRMAR ELIMINACIÓN (solo si hay botones y SweetAlert) ======
  if (hasSwal) {
    document.querySelectorAll(".eliminar-usuario").forEach((boton) => {
      boton.addEventListener("click", (e) => {
        e.preventDefault();
        const url = boton.getAttribute("href");
        Swal.fire({
          title: "¿Eliminar usuario?",
          text: "Esta acción no se puede deshacer.",
          icon: "warning",
          showCancelButton: true,
          confirmButtonColor: "#d33",
          cancelButtonColor: "#6c757d",
          confirmButtonText: "Sí, eliminar",
          cancelButtonText: "Cancelar",
          reverseButtons: true,
          customClass: { popup: "rounded-4 shadow-lg" },
        }).then((result) => {
          if (result.isConfirmed) window.location.href = url;
        });
      });
    });
  }

  // ====== BUSCADOR EN LISTA (si existe la tabla) ======
  const buscador = document.getElementById('buscador');
  const btnLimpiar = document.getElementById('btnLimpiar');
  const filas = document.querySelectorAll('#tablaUsuarios tbody tr');
  if (buscador && filas.length) {
    const filtrar = () => {
      const texto = (buscador.value || "").toLowerCase();
      filas.forEach(fila => {
        const coincide = fila.innerText.toLowerCase().includes(texto);
        fila.style.display = coincide ? '' : 'none';
      });
    };
    buscador.addEventListener('keyup', filtrar);
    if (btnLimpiar) btnLimpiar.addEventListener('click', () => { buscador.value = ''; filtrar(); });
  }

  // ====== ESPECIALIDAD (Crear/Editar usuario) ======
  const rolSelect = document.getElementById('rol');
  const especialidadBlock = document.getElementById('especialidad-block');
  if (rolSelect && especialidadBlock) {
    const toggleEspecialidad = () => {
      especialidadBlock.style.display = (rolSelect.value === 'profesor') ? 'block' : 'none';
    };
    toggleEspecialidad(); // al cargar
    rolSelect.addEventListener('change', toggleEspecialidad);
  }
});
