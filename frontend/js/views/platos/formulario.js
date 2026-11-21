import { api } from "../../api.js";
import { pintarCampo, pintarCheckbox, pintarSelect } from "../../../blocks/campo/campo.js";
import { enviarFormulario } from "../../components/acciones.js";
import { esc } from "../../utils.js";

// Sin id: crear (opcional ?restaurante_id=). Con id: editar.
// Al editar no se puede cambiar de restaurante (lo impide el backend).
export async function PlatoFormulario({ id }, query) {
  const p = id ? await api.getPlato(id) : { disponible: true };
  const restaurantes = id ? [] : await api.getRestaurantes();

  const selectorRestaurante = id
    ? `<p><strong>Restaurante:</strong> ${esc(p.restaurante_nombre)}</p>`
    : pintarSelect({
        name: "restaurante_id",
        label: "Restaurante",
        required: true,
        vacio: "-- Elige --",
        seleccionado: query.get("restaurante_id") || "",
        opciones: restaurantes.map((r) => ({ value: r.id, texto: r.nombre })),
      });

  return {
    html: `
      <h1>${id ? `Editar ${esc(p.nombre)}` : "Nuevo plato"}</h1>
      <form id="form-plato">
        ${selectorRestaurante}
        ${pintarCampo({ name: "nombre", label: "Nombre", value: p.nombre, required: true, max: 100 })}
        ${pintarCampo({ name: "precio", label: "Precio", value: p.precio, type: "number", required: true, attrs: 'min="0" step="0.01"' })}
        ${pintarCheckbox({ name: "disponible", label: "Disponible", checked: p.disponible })}
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
