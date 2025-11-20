document.addEventListener("DOMContentLoaded", () => {

    // =====================================================
    // 🗑️ CONFIRMAR ELIMINACIÓN DE RUTINA
    // =====================================================
    const botones = document.querySelectorAll(".eliminar-rutina");

    botones.forEach(boton => {
        boton.addEventListener("click", function (e) {
            e.preventDefault();
            const url = this.getAttribute("href");

            Swal.fire({
                title: "¿Estás seguro?",
                text: "Esta rutina será eliminada permanentemente.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#d33",
                cancelButtonColor: "#6c757d",
                confirmButtonText: "Eliminar",
                cancelButtonText: "Cancelar"
            }).then(result => {
                if (result.isConfirmed) {
                    window.location.href = url;
                }
            });
        });
    });


    // =====================================================
    // ✅ SWEETALERT PARA RUTINA MODIFICADA / CREADA
    // (USA MENSAJES DE DJANGO AUTOMÁTICAMENTE)
    // =====================================================
    const mensajeElemento = document.getElementById("mensaje-rutina");
    if (mensajeElemento) {
        const mensaje = mensajeElemento.dataset.mensaje;

        Swal.fire({
            icon: 'success',
            title: mensaje,
            confirmButtonColor: '#111',
            timer: 1700,
            showConfirmButton: false
        });
    }

});
