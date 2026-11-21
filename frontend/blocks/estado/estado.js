// Bloque "estado": etiqueta de color con el estado de un pedido.
import { esc } from "../../js/utils.js";

// pintarEstado(pedido) -> <span class="estado estado--pendiente">Pendiente</span>
export function pintarEstado({ estado, estado_etiqueta }) {
  return `<span class="estado estado--${esc(estado)}">${esc(estado_etiqueta)}</span>`;
}
