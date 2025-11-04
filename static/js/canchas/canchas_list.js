document.addEventListener("DOMContentLoaded", () => {
  // ✅ Mensajes Django → SweetAlert
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(a => a.remove()); // Limpia si quedaron alertas HTML previas

  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('success')) {
    const type = urlParams.get('success');
    let msg = '';
    if (type === 'created') msg = '✅ Cancha creada correctamente.';
    else if (type === 'updated') msg = '✅ Cancha actualizada correctamente.';
    else if (type === 'deleted') msg = '🗑️ Cancha eliminada correctamente.';
    if (msg) {
      Swal.fire({
        icon: 'success',
        title: msg,
        timer: 1500,
        showConfirmButton: false
      });
    }
  }

  // 🗑️ Confirmación de eliminación
  document.querySelectorAll('.btn-delete').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const id = btn.dataset.id;
      const nombre = btn.dataset.nombre;

      const confirm = await Swal.fire({
        title: `¿Eliminar la cancha "${nombre}"?`,
        text: "Esta acción no se puede deshacer.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
      });

      if (confirm.isConfirmed) {
        window.location.href = `/canchas/eliminar/${id}/?success=deleted`;
      }
    });
  });
});
