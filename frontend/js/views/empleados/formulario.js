import { api } from "../../api.js";
import { pintarCampo } from "../../../blocks/campo/campo.js";
import { enviarFormulario } from "../../components/acciones.js";
import { esc } from "../../utils.js";

// Sin id: crear. Con id: editar.
export async function EmpleadoFormulario({ id }) {
  const e = id ? await api.getEmpleado(id) : {};
  const campo = (name, label, opciones = {}) =>
    pintarCampo({ name, label, value: e[name], required: true, max: 50, ...opciones });

  return {
    html: `
      <h1>${id ? `Editar ${esc(e.nombre_completo)}` : "Registrar nuevo empleado"}</h1>
      <form id="form-empleado">
        ${campo("primer_nombre", "Primer nombre")}
        ${campo("segundo_nombre", "Segundo nombre", { required: false })}
        ${campo("apellido", "Apellido")}
        ${campo("ci", "CI", { max: 80 })}
        ${campo("telefono", "Teléfono", { max: 30 })}
        ${campo("email", "Email", { max: 200, type: "email" })}
        <button class="boton" type="submit">${id ? "Guardar cambios" : "Crear empleado"}</button>
      </form>
      <p><a href="${id ? `#/empleados/${id}` : "#/empleados"}">Cancelar / Volver</a></p>`,
    mount() {
      enviarFormulario("form-empleado", {
        transformar: (d) => ({ ...d, segundo_nombre: d.segundo_nombre || null }),
        accion: (data) => (id ? api.updateEmpleado(id, data) : api.createEmpleado(data)),
        mensaje: id ? "Empleado actualizado." : "Empleado registrado.",
        destino: (res) => `#/empleados/${res.id}`,
      });
    },
  };
}
