import { api } from "../../api.js";
import { botonEliminar } from "../../components/acciones.js";
import { puede } from "../../state.js";
import { dinero, esc } from "../../utils.js";

export async function PlatoDetalle({ id }) {
  const p = await api.getPlato(id);

  return {
    html: `
      <h1>${esc(p.nombre)}</h1>
      <p><strong>Precio:</strong> ${dinero(p.precio)}</p>
      <p><strong>Disponibilidad:</strong> ${p.disponible ? "Disponible" : "No disponible"}</p>
      <p><strong>Restaurante:</strong>
        <a href="#/restaurantes/${p.restaurante_id}">${esc(p.restaurante_nombre)}</a></p>

      <p class="acciones">
        ${puede("write:carta") ? `<a href="#/platos/${p.id}/editar">Editar plato</a>` : ""}
        ${puede("delete:carta") ? `<button class="boton boton--peligro" type="button" id="btn-eliminar">Eliminar plato</button>` : ""}
      </p>

      <p><a href="#/platos">Volver al listado de platos</a></p>`,
    mount() {
      botonEliminar("btn-eliminar", {
        pregunta: `¿Eliminar el plato "${p.nombre}"?`,
        accion: () => api.deletePlato(p.id),
        destino: `#/restaurantes/${p.restaurante_id}`,
      });
    },
  };
}
