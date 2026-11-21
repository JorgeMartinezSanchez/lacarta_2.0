import { api } from "../../api.js";
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

  const filas = platos
    .map((p) => `
      <tr>
        <td class="tabla__celda"><a href="#/platos/${p.id}">${esc(p.nombre)}</a></td>
        <td class="tabla__celda">${dinero(p.precio)}</td>
        <td class="tabla__celda">${p.disponible ? "Disponible" : "No disponible"}</td>
        <td class="tabla__celda"><a href="#/restaurantes/${p.restaurante_id}">${esc(p.restaurante_nombre)}</a></td>
      </tr>`)
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
        ? `<table class="tabla">
             <thead class="tabla__cabecera"><tr><th class="tabla__celda tabla__celda--titulo">Plato</th><th class="tabla__celda tabla__celda--titulo">Precio</th><th class="tabla__celda tabla__celda--titulo">Disponibilidad</th><th class="tabla__celda tabla__celda--titulo">Restaurante</th></tr></thead>
             <tbody>${filas}</tbody>
           </table>`
        : `<p>No hay platos.</p>`}`,
    mount() {
      document.getElementById("filtro-restaurante").addEventListener("change", (ev) => {
        const v = ev.target.value;
        navegar(v ? `#/platos?restaurante_id=${v}` : "#/platos");
      });
    },
  };
}
