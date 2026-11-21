import { api } from "../../api.js";
import { enviarFormulario } from "../../components/acciones.js";
import { esc } from "../../utils.js";

// Sin id: crear. Con id: editar.
export async function RestauranteFormulario({ id }) {
  const r = id ? await api.getRestaurante(id) : {};
  const campo = (name, label, { required = false, max = 100 } = {}) => `
    <div class="campo">
      <label class="campo__etiqueta" for="${name}">${label}${required ? "*" : ""}</label>
      <input class="campo__control" type="text" id="${name}" name="${name}" maxlength="${max}"
             value="${esc(r[name])}" ${required ? "required" : ""}>
    </div>`;

  return {
    html: `
      <h1>${id ? `Editar ${esc(r.nombre)}` : "Nuevo restaurante"}</h1>
      <form id="form-restaurante">
        ${campo("nombre", "Nombre", { required: true })}
        ${campo("ciudad", "Ciudad", { required: true })}
        ${campo("direccion", "Dirección", { max: 200 })}
        ${campo("telefono", "Teléfono", { max: 30 })}
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
