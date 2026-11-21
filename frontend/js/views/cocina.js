import { api } from "../api.js";
import { mostrarError } from "../components/mensajes.js";
import { flash, puede } from "../state.js";
import { esc, fecha } from "../utils.js";
import { render } from "../router.js";

export async function Cocina() {
  const cola = await api.getCola();

  const tarjetas = cola
    .map((p) => `
      <section class="tarjeta">
        <h2 class="tarjeta__titulo">Pedido #${p.id} · ${esc(p.restaurante_nombre)}</h2>
        <p class="tarjeta__meta">${fecha(p.fecha)} · <span class="estado estado--${esc(p.estado)}">${esc(p.estado_etiqueta)}</span></p>
        <ul class="tarjeta__lista">${p.items.map((i) => `<li>${i.cantidad} × ${esc(i.plato_nombre)}</li>`).join("")}</ul>
        ${p.siguiente && puede("update:pedidos")
          ? `<button class="boton" type="button" data-avanzar="${p.id}" data-estado="${esc(p.siguiente.estado)}">
               Pasar a ${esc(p.siguiente.etiqueta)}</button>`
          : ""}
      </section>`)
    .join("");

  return {
    html: `
      <h1>Cola de la cocina</h1>
      <p>Pedidos activos, los más antiguos primero.</p>
      ${cola.length ? `<div class="cola">${tarjetas}</div>` : `<p>No hay pedidos activos.</p>`}`,
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
