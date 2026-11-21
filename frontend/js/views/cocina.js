import { api } from "../api.js";
import { mostrarError } from "../../blocks/mensajes/mensajes.js";
import { pintarTarjeta } from "../../blocks/tarjeta/tarjeta.js";
import { flash, puede } from "../state.js";
import { render } from "../router.js";

export async function Cocina() {
  const cola = await api.getCola();
  const puedeAvanzar = puede("update:pedidos");

  return {
    html: `
      <h1>Cola de la cocina</h1>
      <p>Pedidos activos, los más antiguos primero.</p>
      ${cola.length
        ? `<div class="cola">${cola.map((p) => pintarTarjeta(p, { puedeAvanzar })).join("")}</div>`
        : `<p>No hay pedidos activos.</p>`}`,
    mount() {
      document.querySelectorAll("[data-avanzar]").forEach((btn) =>
        btn.addEventListener("click", async () => {
          btn.disabled = true;
          try {
            const p = await api.avanzarPedido(btn.dataset.avanzar, btn.dataset.estado);
            flash(`Pedido #${p.id}: ${p.estado_etiqueta}.`);
            render();
          } catch (e) {
            mostrarError(e);
            btn.disabled = false;
          }
        })
      );
    },
  };
}
