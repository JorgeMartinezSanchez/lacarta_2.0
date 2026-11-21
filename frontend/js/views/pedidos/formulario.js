import { api } from "../../api.js";
import { mostrarError } from "../../components/mensajes.js";
import { flash } from "../../state.js";
import { dinero, esc, navegar } from "../../utils.js";

// #/pedidos/nuevo?restaurante_id=1
// Solo se envían plato y cantidad: precio y total los calcula el servidor (R1.4).
export async function PedidoFormulario(params, query) {
  const restauranteId = Number(query.get("restaurante_id"));
  const r = await api.getRestaurante(restauranteId);
  const disponibles = r.platos.filter((p) => p.disponible);

  const filas = disponibles
    .map((p) => `
      <tr>
        <td class="tabla__celda">${esc(p.nombre)}</td>
        <td class="tabla__celda">${dinero(p.precio)}</td>
        <td class="tabla__celda"><input class="tabla__control" type="number" name="plato-${p.id}" data-plato="${p.id}"
                   data-precio="${p.precio}" min="0" max="20" value="0"></td>
      </tr>`)
    .join("");

  return {
    html: `
      <h1>Hacer un pedido en ${esc(r.nombre)}</h1>
      ${disponibles.length
        ? `<p>Indica cuántas unidades quieres de cada plato (de 1 a 20). Deja en 0 los que no pidas.</p>
           <form id="form-pedido">
             <table class="tabla">
               <thead class="tabla__cabecera"><tr><th class="tabla__celda tabla__celda--titulo">Plato</th><th class="tabla__celda tabla__celda--titulo">Precio</th><th class="tabla__celda tabla__celda--titulo">Cantidad</th></tr></thead>
               <tbody>${filas}</tbody>
               <tfoot><tr><th class="tabla__celda tabla__celda--titulo" colspan="2">Total estimado</th><th class="tabla__celda tabla__celda--titulo" id="total">${dinero(0)}</th></tr></tfoot>
             </table>
             <button class="boton" type="submit">Hacer pedido</button>
           </form>`
        : `<p>Este restaurante no tiene platos disponibles en este momento.</p>`}
      <p><a href="#/restaurantes/${r.id}">Volver al restaurante</a></p>`,
    mount() {
      const form = document.getElementById("form-pedido");
      if (!form) return;
      const inputs = [...form.querySelectorAll("input[data-plato]")];

      form.addEventListener("input", () => {
        const total = inputs.reduce((s, i) => s + Number(i.dataset.precio) * (Number(i.value) || 0), 0);
        document.getElementById("total").textContent = dinero(total);
      });

      form.addEventListener("submit", async (ev) => {
        ev.preventDefault();
        const items = inputs
          .filter((i) => Number(i.value) > 0)
          .map((i) => ({ plato_id: Number(i.dataset.plato), cantidad: Number(i.value) }));
        if (!items.length) return mostrarError("Elige al menos un plato.");
        try {
          const pedido = await api.createPedido({ restaurante_id: r.id, items });
          flash(`Pedido #${pedido.id} realizado.`);
          navegar(`#/pedidos/${pedido.id}`);
        } catch (e) {
          mostrarError(e);
        }
      });
    },
  };
}
