import { api } from "../../api.js";
import { pintarCampo } from "../../../blocks/campo/campo.js";
import { enviarFormulario } from "../../components/acciones.js";
import { esc } from "../../utils.js";

// Sin id: crear. Con id: editar.
export async function RestauranteFormulario({ id }) {
  const r = id ? await api.getRestaurante(id) : {};

  return {
    html: `
      <h1>${id ? `Editar ${esc(r.nombre)}` : "Nuevo restaurante"}</h1>
      <form id="form-restaurante">
        ${pintarCampo({ name: "nombre", label: "Nombre", value: r.nombre, required: true, max: 100 })}
        ${pintarCampo({ name: "ciudad", label: "Ciudad", value: r.ciudad, required: true, max: 100 })}
        ${pintarCampo({ name: "direccion", label: "Dirección", value: r.direccion, max: 200 })}
        ${pintarCampo({ name: "telefono", label: "Teléfono", value: r.telefono, max: 30 })}
        <button class="boton" type="submit">${id ? "Guardar cambios" : "Crear restaurante"}</button>
      </form>
      <p><a href="${id ? `#/restaurantes/${id}` : "#/restaurantes"}">Cancelar / Volver</a></p>`,
    mount() {
      enviarFormulario("form-restaurante", {
        accion: (data) => (id ? api.updateRestaurante(id, data) : api.createRestaurante(data)),
        mensaje: id ? "Restaurante actualizado." : "Restaurante creado.",
        destino: (res) => `#/restaurantes/${res.id}`,
      });
    },
  };
}
