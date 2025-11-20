document.addEventListener("DOMContentLoaded", () => {
    const hasSwal = typeof window.Swal !== "undefined";

    const mensajeElemento = document.getElementById("mensaje-rutina");
    if (hasSwal && mensajeElemento) {
        Swal.fire({
            icon: "success",
            title: mensajeElemento.dataset.mensaje,
            timer: 1700,
            showConfirmButton: false,
            confirmButtonColor: "#212529",
        });
    }

    if (hasSwal) {
        document.querySelectorAll(".eliminar-rutina").forEach((boton) => {
            boton.addEventListener("click", (e) => {
                e.preventDefault();
                const url = boton.getAttribute("href");

                Swal.fire({
                    title: "¿Eliminar rutina?",
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
                    if (result.isConfirmed) {
                        window.location.href = url;
                    }
                });
            });
        });
    }
});
