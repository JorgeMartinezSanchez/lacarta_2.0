import { api } from "../../api.js";
import { puede } from "../../state.js";
import { esc } from "../../utils.js";

export async function EmpleadosLista() {
  const empleados = await api.getEmpleados();

  const filas = empleados
    .map((e) => `
      <tr>
        <td class="tabla__celda"><a href="#/empleados/${e.id}">${esc(e.nombre_completo)}</a></td>
        <td class="tabla__celda">${esc(e.ci)}</td>
        <td class="tabla__celda">${esc(e.telefono)}</td>
        <td class="tabla__celda">${esc(e.email)}</td>
      </tr>`)
    .join("");

  return {
    html: `
      <h1>Empleados</h1>
      ${puede("write:empleados") ? `<p><a href="#/empleados/nuevo" class="boton">Registrar empleado</a></p>` : ""}
      ${empleados.length
        ? `<table class="tabla">
             <thead class="tabla__cabecera"><tr><th class="tabla__celda tabla__celda--titulo">Nombre</th><th class="tabla__celda tabla__celda--titulo">CI</th><th class="tabla__celda tabla__celda--titulo">Teléfono</th><th class="tabla__celda tabla__celda--titulo">Email</th></tr></thead>
             <tbody>${filas}</tbody>
           </table>`
        : `<p>No hay empleados registrados.</p>`}`,
  };
}
