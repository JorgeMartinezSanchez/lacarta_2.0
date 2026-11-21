import { flash } from "../state.js";
import { datosForm, navegar } from "../utils.js";
import { mostrarError } from "./mensajes.js";

// Engancha un botón "Eliminar": confirma, llama a la API y redirige.
export function botonEliminar(id, { pregunta, accion, destino }) {
  document.getElementById(id)?.addEventListener("click", async () => {
    if (!confirm(pregunta)) return;
    try {
      const r = await accion();
      flash(r?.mensaje || "Eliminado.");
      navegar(destino);
    } catch (e) {
      mostrarError(e);
    }
  });
}

// Engancha un <form>: convierte sus campos, llama a la API y redirige.
// `transformar` adapta los datos del form al JSON que espera el backend.
export function enviarFormulario(id, { transformar = (d) => d, accion, mensaje, destino }) {
  const form = document.getElementById(id);
  form?.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const boton = form.querySelector("[type=submit]");
    boton.disabled = true;
    try {
      const r = await accion(transformar(datosForm(form), form));
      flash(mensaje);
      navegar(typeof destino === "function" ? destino(r) : destino);
    } catch (e) {
      mostrarError(e);
      boton.disabled = false;
    }
  });
}
