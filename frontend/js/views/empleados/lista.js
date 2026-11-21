import { api } from "../../api.js";
import { pintarTabla } from "../../../blocks/tabla/tabla.js";
import { puede } from "../../state.js";
import { esc } from "../../utils.js";

export async function EmpleadosLista() {
  const empleados = await api.getEmpleados();

  return {
    html: `
      <h1>Empleados</h1>
      ${puede("write:empleados") ? `<p><a href="#/empleados/nuevo" class="boton">Registrar empleado</a></p>` : ""}
      ${empleados.length
        ? pintarTabla({
            columnas: ["Nombre", "CI", "Teléfono", "Email"],
            filas: empleados.map((e) => [
              `<a href="#/empleados/${e.id}">${esc(e.nombre_completo)}</a>`,
              esc(e.ci),
              esc(e.telefono),
              esc(e.email),
            ]),
          })
        : `<p>No hay empleados registrados.</p>`}`,
  };
}
