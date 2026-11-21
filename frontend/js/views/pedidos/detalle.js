import { api } from "../../api.js";
import { mostrarError } from "../../../blocks/mensajes/mensajes.js";
import { pintarEstado } from "../../../blocks/estado/estado.js";
import { pintarTabla } from "../../../blocks/tabla/tabla.js";
import { flash } from "../../state.js";
import { dinero, esc, fecha } from "../../utils.js";
import { render } from "../../router.js";

export async function PedidoDetalle({ id }) {
  const p = await api.getPedido(id);

  return {
    html: `
      <h1>Pedido #${p.id}</h1>
      <p><strong>Restaurante:</strong>
        <a href="#/restaurantes/${p.restaurante_id}">${esc(p.restaurante_nombre)}</a></p>
      <p><strong>Fecha:</strong> ${fecha(p.fecha)}</p>
      <p><strong>Estado:</strong> ${pintarEstado(p)}</p>

      ${pintarTabla({
        columnas: ["Plato", "Cantidad", "Precio unitario", "Subtotal"],
        filas: p.items.map((i) => [
          esc(i.plato_nombre),
          i.cantidad,
          dinero(i.precio_unitario),
          dinero(i.precio_unitario * i.cantidad),
        ]),
        pie: [{ html: "Total", colspan: 3 }, dinero(p.total)],
      })}

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
