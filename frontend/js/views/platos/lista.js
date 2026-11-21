import { api } from "../../api.js";
import { pintarTabla } from "../../../blocks/tabla/tabla.js";
import { puede } from "../../state.js";
import { dinero, esc, navegar } from "../../utils.js";

export async function PlatosLista(params, query) {
  const restauranteId = query.get("restaurante_id") || "";
  const [platos, restaurantes] = await Promise.all([
    api.getPlatos(restauranteId),
    api.getRestaurantes(),
  ]);

  const opciones = restaurantes
    .map((r) => `<option value="${r.id}" ${String(r.id) === restauranteId ? "selected" : ""}>${esc(r.nombre)}</option>`)
    .join("");

  return {
    html: `
      <h1>Platos</h1>
      <form class="filtro">
        <label class="filtro__etiqueta" for="filtro-restaurante">Restaurante:</label>
        <select class="filtro__control" id="filtro-restaurante">
          <option value="">Todos</option>${opciones}
        </select>
      </form>
      ${puede("write:carta") ? `<p><a href="#/platos/nuevo${restauranteId ? `?restaurante_id=${restauranteId}` : ""}" class="boton">Nuevo plato</a></p>` : ""}
      ${platos.length
        ? pintarTabla({
            columnas: ["Plato", "Precio", "Disponibilidad", "Restaurante"],
            filas: platos.map((p) => [
              `<a href="#/platos/${p.id}">${esc(p.nombre)}</a>`,
              dinero(p.precio),
              p.disponible ? "Disponible" : "No disponible",
              `<a href="#/restaurantes/${p.restaurante_id}">${esc(p.restaurante_nombre)}</a>`,
            ]),
          })
        : `<p>No hay platos.</p>`}`,
    mount() {
      document.getElementById("filtro-restaurante").addEventListener("change", (ev) => {
        const v = ev.target.value;
        navegar(v ? `#/platos?restaurante_id=${v}` : "#/platos");
      });
    },
  };
}
