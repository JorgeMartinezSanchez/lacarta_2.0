import { tomarMensajes } from "../state.js";
import { esc } from "../utils.js";

export function Mensajes() {
  const lista = tomarMensajes();
  return `<ul id="mensajes" class="mensajes">${lista
    .map((m) => `<li class="mensajes__item mensajes__item--${m.tipo}">${esc(m.texto)}</li>`)
    .join("")}</ul>`;
}

// Muestra un error sin re-renderizar la vista (p. ej. al fallar un formulario).
export function mostrarError(err) {
  const ul = document.getElementById("mensajes");
  if (ul) ul.innerHTML = `<li class="mensajes__item mensajes__item--error">${esc(err?.message || err)}</li>`;
  window.scrollTo(0, 0);
}
