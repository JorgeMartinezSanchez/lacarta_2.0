import { api } from "../../api.js";
import { botonEliminar } from "../../components/acciones.js";
import { puede } from "../../state.js";
import { dinero, esc } from "../../utils.js";

export async function RestauranteDetalle({ id }) {
  const r = await api.getRestaurante(id);

  const platos = r.platos
    .map((p) => `
      <tr>
        <td class="tabla__celda"><a href="#/platos/${p.id}">${esc(p.nombre)}</a></td>
        <td class="tabla__celda">${dinero(p.precio)}</td>
        <td class="tabla__celda">${p.disponible ? "Disponible" : "No disponible"}</td>
      </tr>`)
    .join("");

  return {
    html: `
      <h1>${esc(r.nombre)}</h1>
      <p><strong>Ciudad:</strong> ${esc(r.ciudad)}</p>
      <p><strong>Dirección:</strong> ${esc(r.direccion || "-")}</p>
      <p><strong>Teléfono:</strong> ${esc(r.telefono || "-")}</p>

      <p class="acciones">
        ${puede("create:pedidos") && r.platos.some((p) => p.disponible)
          ? `<a href="#/pedidos/nuevo?restaurante_id=${r.id}" class="boton">Hacer un pedido</a>` : ""}
        ${puede("write:carta") ? `
          <a href="#/restaurantes/${r.id}/editar">Editar restaurante</a>
          <a href="#/platos/nuevo?restaurante_id=${r.id}">Agregar plato</a>` : ""}
        ${puede("delete:carta") ? `<button class="boton boton--peligro" type="button" id="btn-eliminar">Eliminar restaurante</button>` : ""}
      </p>

      <h2>Carta</h2>
      ${r.platos.length
        ? `<table class="tabla">
             <thead class="tabla__cabecera"><tr><th class="tabla__celda tabla__celda--titulo">Plato</th><th class="tabla__celda tabla__celda--titulo">Precio</th><th class="tabla__celda tabla__celda--titulo">Disponibilidad</th></tr></thead>
             <tbody>${platos}</tbody>
           </table>`
        : `<p>Este restaurante todavía no tiene platos.</p>`}

      <p><a href="#/restaurantes">Volver al listado</a></p>`,
    mount() {
      botonEliminar("btn-eliminar", {
        pregunta: `¿Eliminar el restaurante "${r.nombre}"?`,
        accion: () => api.deleteRestaurante(r.id),
        destino: "#/restaurantes",
      });
    },
  };
}
