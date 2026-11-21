import { api } from "../../api.js";
import { puede } from "../../state.js";
import { esc, navegar } from "../../utils.js";

export async function RestaurantesLista(params, query) {
  const ciudad = query.get("ciudad") || "";
  const restaurantes = await api.getRestaurantes(ciudad);

  const filas = restaurantes
    .map((r) => `
      <tr>
        <td class="tabla__celda"><a href="#/restaurantes/${r.id}">${esc(r.nombre)}</a></td>
        <td class="tabla__celda">${esc(r.ciudad)}</td>
        <td class="tabla__celda">${esc(r.direccion || "-")}</td>
        <td class="tabla__celda">${r.num_platos}</td>
      </tr>`)
    .join("");

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
        ? `<table class="tabla">
             <thead class="tabla__cabecera"><tr><th class="tabla__celda tabla__celda--titulo">Nombre</th><th class="tabla__celda tabla__celda--titulo">Ciudad</th><th class="tabla__celda tabla__celda--titulo">Dirección</th><th class="tabla__celda tabla__celda--titulo">Platos</th></tr></thead>
             <tbody>${filas}</tbody>
           </table>`
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
