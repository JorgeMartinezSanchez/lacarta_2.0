import { api } from "../../api.js";
import { botonEliminar } from "../../components/acciones.js";
import { puede } from "../../state.js";
import { esc } from "../../utils.js";

export async function EmpleadoDetalle({ id }) {
  const e = await api.getEmpleado(id);

  return {
    html: `
      <h1>${esc(e.nombre_completo)}</h1>
      <p><strong>CI:</strong> ${esc(e.ci)}</p>
      <p><strong>Teléfono:</strong> ${esc(e.telefono)}</p>
      <p><strong>Email:</strong> ${esc(e.email)}</p>

      <p class="acciones">
        ${puede("write:empleados") ? `<a href="#/empleados/${e.id}/editar">Editar empleado</a>` : ""}
        ${puede("delete:empleados") ? `<button class="boton boton--peligro" type="button" id="btn-eliminar">Eliminar empleado</button>` : ""}
      </p>

      <p><a href="#/empleados">Volver al listado</a></p>`,
    mount() {
      botonEliminar("btn-eliminar", {
        pregunta: `¿Eliminar a ${e.nombre_completo}?`,
        accion: () => api.deleteEmpleado(e.id),
        destino: "#/empleados",
      });
    },
  };
}
