import { api } from "../../api.js";
import { mostrarError } from "../../components/mensajes.js";
import { flash } from "../../state.js";
import { dinero, esc, fecha } from "../../utils.js";
import { render } from "../../router.js";

export async function PedidoDetalle({ id }) {
  const p = await api.getPedido(id);

  const items = p.items
    .map((i) => `
      <tr>
        <td class="tabla__celda">${esc(i.plato_nombre)}</td>
        <td class="tabla__celda">${i.cantidad}</td>
        <td class="tabla__celda">${dinero(i.precio_unitario)}</td>
        <td class="tabla__celda">${dinero(i.precio_unitario * i.cantidad)}</td>
      </tr>`)
    .join("");

  return {
    html: `
      <h1>Pedido #${p.id}</h1>
      <p><strong>Restaurante:</strong>
        <a href="#/restaurantes/${p.restaurante_id}">${esc(p.restaurante_nombre)}</a></p>
      <p><strong>Fecha:</strong> ${fecha(p.fecha)}</p>
      <p><strong>Estado:</strong> <span class="estado estado--${esc(p.estado)}">${esc(p.estado_etiqueta)}</span></p>

      <table class="tabla">
        <thead class="tabla__cabecera"><tr><th class="tabla__celda tabla__celda--titulo">Plato</th><th class="tabla__celda tabla__celda--titulo">Cantidad</th><th class="tabla__celda tabla__celda--titulo">Precio unitario</th><th class="tabla__celda tabla__celda--titulo">Subtotal</th></tr></thead>
        <tbody>${items}</tbody>
        <tfoot><tr><th class="tabla__celda tabla__celda--titulo" colspan="3">Total</th><th class="tabla__celda tabla__celda--titulo">${dinero(p.total)}</th></tr></tfoot>
      </table>

      ${p.estado === "pendiente"
        ? `<p><button class="boton boton--peligro" type="button" id="btn-cancelar">Cancelar pedido</button></p>`
        : ""}

      <p><a href="#/pedidos">Volver a mis pedidos</a></p>`,
    mount() {
      document.getElementById("btn-cancelar")?.addEventListener("click", async () => {
        if (!confirm("¿Cancelar este pedido?")) return;
        try {
          await api.cancelarPedido(p.id);
          flash("Pedido cancelado.");
          render(); // volver a dibujar la misma vista con el estado nuevo
        } catch (e) {
          mostrarError(e);
        }
      });
    },
  };
}
