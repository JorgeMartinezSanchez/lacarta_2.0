import { api } from "../../api.js";
import { enviarFormulario } from "../../components/acciones.js";
import { esc } from "../../utils.js";

// Sin id: crear (opcional ?restaurante_id=). Con id: editar.
// Al editar no se puede cambiar de restaurante (lo impide el backend).
export async function PlatoFormulario({ id }, query) {
  const p = id ? await api.getPlato(id) : { disponible: true };
  const restaurantes = id ? [] : await api.getRestaurantes();
  const preseleccion = query.get("restaurante_id");

  const selectorRestaurante = id
    ? `<p><strong>Restaurante:</strong> ${esc(p.restaurante_nombre)}</p>`
    : `<div class="campo">
         <label class="campo__etiqueta" for="restaurante_id">Restaurante*</label>
         <select class="campo__control" id="restaurante_id" name="restaurante_id" required>
           <option value="">-- Elige --</option>
           ${restaurantes
             .map((r) => `<option value="${r.id}" ${String(r.id) === preseleccion ? "selected" : ""}>${esc(r.nombre)}</option>`)
             .join("")}
         </select>
       </div>`;

  return {
    html: `
      <h1>${id ? `Editar ${esc(p.nombre)}` : "Nuevo plato"}</h1>
      <form id="form-plato">
        ${selectorRestaurante}
        <div class="campo">
          <label class="campo__etiqueta" for="nombre">Nombre*</label>
          <input class="campo__control" type="text" id="nombre" name="nombre" maxlength="100" value="${esc(p.nombre)}" required>
        </div>
        <div class="campo">
          <label class="campo__etiqueta" for="precio">Precio*</label>
          <input class="campo__control" type="number" id="precio" name="precio" min="0" step="0.01" value="${esc(p.precio)}" required>
        </div>
        <div class="campo campo--checkbox">
          <label class="campo__etiqueta"><input class="campo__checkbox" type="checkbox" name="disponible" ${p.disponible ? "checked" : ""}> Disponible</label>
        </div>
        <button class="boton" type="submit">${id ? "Guardar cambios" : "Crear plato"}</button>
      </form>
      <p><a href="${id ? `#/platos/${id}` : "#/platos"}">Cancelar / Volver</a></p>`,
    mount() {
      enviarFormulario("form-plato", {
        transformar: (d, form) => ({
          ...d,
          disponible: form.disponible.checked, // el backend exige true/false
        }),
        accion: (data) => (id ? api.updatePlato(id, data) : api.createPlato(data)),
        mensaje: id ? "Plato actualizado." : "Plato creado.",
        destino: (res) => `#/platos/${res.id}`,
      });
    },
  };
}
