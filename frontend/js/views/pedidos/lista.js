import { api } from "../../api.js";
import { pintarEstado } from "../../../blocks/estado/estado.js";
import { pintarTabla } from "../../../blocks/tabla/tabla.js";
import { dinero, esc, fecha } from "../../utils.js";

export async function PedidosLista() {
  const pedidos = await api.getPedidos();

  return {
    html: `
      <h1>Mis pedidos</h1>
      ${pedidos.length
        ? pintarTabla({
            columnas: ["#", "Fecha", "Restaurante", "Estado", "Total", ""],
            filas: pedidos.map((p) => [
              p.id,
              fecha(p.fecha),
              esc(p.restaurante_nombre),
              pintarEstado(p),
              dinero(p.total),
              `<a href="#/pedidos/${p.id}">Ver</a>`,
            ]),
          })
        : `<p>Todavía no has hecho ningún pedido.</p>`}
      <p><a href="#/restaurantes">Ver la carta</a></p>`,
  };
}
