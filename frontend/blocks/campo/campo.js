// Bloque "campo": etiqueta + control de un formulario.
import { esc } from "../../js/utils.js";

// pintarCampo({ name: "nombre", label: "Nombre", required: true, value: r.nombre })
export function pintarCampo({
  name, label, value = "", type = "text", required = false, max, attrs = "",
}) {
  return `
    <div class="campo">
      <label class="campo__etiqueta" for="${name}">${label}${required ? "*" : ""}</label>
      <input class="campo__control" type="${type}" id="${name}" name="${name}"
             value="${esc(value)}" ${max ? `maxlength="${max}"` : ""}
             ${required ? "required" : ""} ${attrs}>
    </div>`;
}

// pintarSelect({ name, label, opciones: [{ value, texto }], seleccionado, required })
export function pintarSelect({ name, label, opciones, seleccionado = "", required = false, vacio }) {
  return `
    <div class="campo">
      <label class="campo__etiqueta" for="${name}">${label}${required ? "*" : ""}</label>
      <select class="campo__control" id="${name}" name="${name}" ${required ? "required" : ""}>
        ${vacio ? `<option value="">${esc(vacio)}</option>` : ""}
        ${opciones
          .map((o) => `<option value="${esc(o.value)}" ${String(o.value) === String(seleccionado) ? "selected" : ""}>${esc(o.texto)}</option>`)
          .join("")}
      </select>
    </div>`;
}

// pintarCheckbox({ name: "disponible", label: "Disponible", checked: true })
export function pintarCheckbox({ name, label, checked = false }) {
  return `
    <div class="campo campo--checkbox">
      <label class="campo__etiqueta">
        <input class="campo__checkbox" type="checkbox" name="${name}" ${checked ? "checked" : ""}>
        ${label}
      </label>
    </div>`;
}
