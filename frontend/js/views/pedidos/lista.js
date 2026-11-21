import { api } from "../../api.js";
import { dinero, esc, fecha } from "../../utils.js";

export async function PedidosLista() {
  const pedidos = await api.getPedidos();

  const filas = pedidos
    .map((p) => `
      <tr>
        <td class="tabla__celda">${p.id}</td>
        <td class="tabla__celda">${fecha(p.fecha)}</td>
        <td class="tabla__celda">${esc(p.restaurante_nombre)}</td>
        <td class="tabla__celda"><span class="estado estado--${esc(p.estado)}">${esc(p.estado_etiqueta)}</span></td>
        <td class="tabla__celda">${dinero(p.total)}</td>
        <td class="tabla__celda"><a href="#/pedidos/${p.id}">Ver</a></td>
      </tr>`)
    .join("");

  return {
    html: `
      <h1>Mis pedidos</h1>
      ${pedidos.length
        ? `<table class="tabla">
             <thead class="tabla__cabecera"><tr><th class="tabla__celda tabla__celda--titulo">#</th><th class="tabla__celda tabla__celda--titulo">Fecha</th><th class="tabla__celda tabla__celda--titulo">Restaurante</th><th class="tabla__celda tabla__celda--titulo">Estado</th><th class="tabla__celda tabla__celda--titulo">Total</th><th class="tabla__celda tabla__celda--titulo"></th></tr></thead>
             <tbody>${filas}</tbody>
           </table>`
        : `<p>Todavía no has hecho ningún pedido.</p>`}
      <p><a href="#/restaurantes">Ver la carta</a></p>`,
  };
}
