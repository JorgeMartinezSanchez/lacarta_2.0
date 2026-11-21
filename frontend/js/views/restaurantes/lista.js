import { api } from "../../api.js";
import { pintarTabla } from "../../../blocks/tabla/tabla.js";
import { puede } from "../../state.js";
import { esc, navegar } from "../../utils.js";

export async function RestaurantesLista(params, query) {
  const ciudad = query.get("ciudad") || "";
  const restaurantes = await api.getRestaurantes(ciudad);

  return {
    html: `
      <h1>Restaurantes</h1>
      <form id="form-filtro" class="filtro">
        <label class="filtro__etiqueta" for="ciudad">Filtrar por ciudad:</label>
        <input class="filtro__control" type="text" id="ciudad" name="ciudad" value="${esc(ciudad)}">
        <button class="boton" type="submit">Filtrar</button>
        ${ciudad ? `<a href="#/restaurantes">Quitar filtro</a>` : ""}
      </form>
      ${puede("write:carta") ? `<p><a href="#/restaurantes/nuevo" class="boton">Nuevo restaurante</a></p>` : ""}
      ${restaurantes.length
        ? pintarTabla({
            columnas: ["Nombre", "Ciudad", "Dirección", "Platos"],
            filas: restaurantes.map((r) => [
              `<a href="#/restaurantes/${r.id}">${esc(r.nombre)}</a>`,
              esc(r.ciudad),
              esc(r.direccion || "-"),
              r.num_platos,
            ]),
          })
        : `<p>No hay restaurantes${ciudad ? ` en ${esc(ciudad)}` : ""}.</p>`}`,
    mount() {
      document.getElementById("form-filtro").addEventListener("submit", (ev) => {
        ev.preventDefault();
        const c = ev.target.ciudad.value.trim();
        navegar(c ? `#/restaurantes?ciudad=${encodeURIComponent(c)}` : "#/restaurantes");
      });
    },
  };
}
