document.addEventListener("DOMContentLoaded", () => {
  const planSelect = document.querySelector("select[name='plan']");
  const inputMonto = document.querySelector("input[name='monto_pagado']");

  if (!planSelect || !inputMonto) return;

  // Al cambiar el plan, autocompleta el monto pagado
  planSelect.addEventListener("change", () => {
    const selectedOption = planSelect.options[planSelect.selectedIndex];
    const texto = selectedOption.textContent;

    // Busca un número dentro del texto (precio)
    const precio = texto.match(/\$([\d.,]+)/);
    if (precio && precio[1]) {
      const valor = precio[1].replace(/[.,]/g, "");
      inputMonto.value = parseFloat(valor);
    }
  });
});
