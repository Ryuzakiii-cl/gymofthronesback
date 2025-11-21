document.addEventListener("DOMContentLoaded", () => {

    // ============================================
    //  SWEETALERT MENSAJES GENERALES
    // ============================================
    if (window.Swal) {
        const m = document.getElementById("mensaje-rutina");
        if (m) {
            Swal.fire({
                icon: "success",
                title: m.dataset.mensaje,
                timer: 1700,
                showConfirmButton: false
            });
        }
    }

    // ============================================
    //  CONFIRMAR ELIMINACIÓN EN LISTA RUTINAS
    // ============================================
    document.querySelectorAll(".eliminar-rutina").forEach(btn => {
        btn.addEventListener("click", e => {
            e.preventDefault();
            const url = btn.href;

            Swal.fire({
                title: "¿Eliminar rutina?",
                text: "Esta acción no se puede deshacer",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#d33",
                confirmButtonText: "Eliminar",
                cancelButtonText: "Cancelar"
            }).then(resp => {
                if (resp.isConfirmed) window.location.href = url;
            });
        });
    });


    // ============================================
    //  EDITOR SOLO SI EXISTE tabla-ejercicios-nuevos
    // ============================================
    const tablaNuevos = document.getElementById("tabla-ejercicios-nuevos");
    if (!tablaNuevos) return;

    const tablaAntiguos = document.getElementById("tabla-ejercicios-existentes");
    const inputJSON = document.getElementById("contenido-json");

    const semanaSelect = document.getElementById("semana-select");
    const diaInput = document.getElementById("dia-input");
    const ejercicioSelect = document.getElementById("ejercicio-select");
    const inputOtro = document.getElementById("ejercicio-personalizado");
    const seriesInput = document.getElementById("series-input");
    const repsInput = document.getElementById("reps-input");
    const descansoInput = document.getElementById("descanso-input");
    const btnAdd = document.getElementById("btn-agregar-fila");
    const form = document.getElementById("form-rutina");


    // Mostrar campo "Otro"
    ejercicioSelect.addEventListener("change", () => {
        if (ejercicioSelect.value === "Otro")
            inputOtro.classList.remove("d-none");
        else {
            inputOtro.classList.add("d-none");
            inputOtro.value = "";
        }
    });


    // --------------------------------------------
    //  FUNCION AGREGAR FILA NUEVA
    // --------------------------------------------
    function agregarFilaNueva({ semana, dia, ejercicio, series, reps, descanso }) {

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><input class="form-control form-control-sm semana-input" value="${semana}" type="number"></td>
            <td><input class="form-control form-control-sm dia-input" value="${dia}" type="number"></td>
            <td><input class="form-control form-control-sm ejercicio-input" value="${ejercicio}" type="text"></td>
            <td><input class="form-control form-control-sm series-input" value="${series}" type="number"></td>
            <td><input class="form-control form-control-sm reps-input" value="${reps}" type="text"></td>
            <td><input class="form-control form-control-sm descanso-input" value="${descanso}" type="text"></td>
            <td><button type="button" class="btn btn-sm btn-outline-danger btn-eliminar-fila">🗑️</button></td>
        `;

        tr.querySelector(".btn-eliminar-fila").addEventListener("click", () => {
            tr.remove();
            actualizarJSON();
        });

        tablaNuevos.appendChild(tr);
    }


    // --------------------------------------------
    //  ELIMINAR EJERCICIOS ANTIGUOS (solo visual)
    // --------------------------------------------
    tablaAntiguos.querySelectorAll(".btn-eliminar-antiguo").forEach(btn => {
        btn.addEventListener("click", () => {
            btn.closest("tr").remove();
            actualizarJSON();
        });
    });


    // --------------------------------------------
    //  CONSTRUIR JSON FINAL = antiguos restantes + nuevos
    // --------------------------------------------
    function construirJSON() {
        const obj = {};

        // 1. ejercicios antiguos (si quedaron en tabla)
        tablaAntiguos.querySelectorAll("tr").forEach(row => {
            const semana = row.children[0].innerText;
            const dia = row.children[1].innerText;
            const ejercicio = row.children[2].innerText;
            const series = row.children[3].innerText;
            const reps = row.children[4].innerText;
            const descanso = row.children[5].innerText;

            const sKey = `semana${semana}`;
            const dKey = `dia${dia}`;

            if (!obj[sKey]) obj[sKey] = {};
            if (!obj[sKey][dKey]) obj[sKey][dKey] = [];

            obj[sKey][dKey].push({
                ejercicio,
                series: Number(series),
                reps,
                descanso
            });
        });

        // 2. ejercicios nuevos
        tablaNuevos.querySelectorAll("tr").forEach(row => {
            const semana = row.querySelector(".semana-input").value;
            const dia = row.querySelector(".dia-input").value;
            const ejercicio = row.querySelector(".ejercicio-input").value;
            const series = row.querySelector(".series-input").value;
            const reps = row.querySelector(".reps-input").value;
            const descanso = row.querySelector(".descanso-input").value;

            const sKey = `semana${semana}`;
            const dKey = `dia${dia}`;

            if (!obj[sKey]) obj[sKey] = {};
            if (!obj[sKey][dKey]) obj[sKey][dKey] = [];

            obj[sKey][dKey].push({
                ejercicio,
                series: Number(series),
                reps,
                descanso
            });
        });

        return obj;
    }


    function actualizarJSON() {
        inputJSON.value = JSON.stringify(construirJSON(), null, 2);
    }


    // --------------------------------------------
    //  BOTÓN AGREGAR EJERCICIO NUEVO
    // --------------------------------------------
    btnAdd.addEventListener("click", () => {

        let ejercicio = ejercicioSelect.value;
        if (ejercicio === "Otro") {
            ejercicio = inputOtro.value.trim();
            if (!ejercicio) {
                Swal.fire({ icon: "warning", title: "Escribe el ejercicio" });
                return;
            }
        }

        agregarFilaNueva({
            semana: semanaSelect.value,
            dia: diaInput.value,
            ejercicio,
            series: seriesInput.value,
            reps: repsInput.value,
            descanso: descansoInput.value
        });

        actualizarJSON();
    });

    // Guardado final
    form.addEventListener("submit", actualizarJSON);

});
