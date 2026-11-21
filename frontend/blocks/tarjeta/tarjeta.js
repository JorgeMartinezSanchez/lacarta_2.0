// Bloque "tarjeta": pinta un pedido de la cocina a partir de tarjeta.html.
import { fecha } from "../../js/utils.js";

// El <template> se descarga una sola vez, al importar el módulo.
const html = await fetch(new URL("./tarjeta.html", import.meta.url)).then((r) => r.text());
const contenedor = document.createElement("div");
contenedor.innerHTML = html;
const template = contenedor.querySelector("#tpl-tarjeta");

// pintarTarjeta(pedido, { puedeAvanzar }) -> string HTML
// Todo se llena con textContent, así que no hace falta esc().
export function pintarTarjeta(p, { puedeAvanzar = false } = {}) {
  const nodo = template.content.firstElementChild.cloneNode(true);
  const campo = (n) => nodo.querySelector(`[data-campo="${n}"]`);

  campo("id").textContent = p.id;
  campo("restaurante").textContent = p.restaurante_nombre;
  campo("fecha").textContent = fecha(p.fecha);

  const estado = campo("estado");
  estado.textContent = p.estado_etiqueta;
  estado.classList.add(`estado--${p.estado}`);

  for (const i of p.items) {
    const li = document.createElement("li");
    li.className = "tarjeta__item";
    li.textContent = `${i.cantidad} × ${i.plato_nombre}`;
    campo("items").append(li);
  }

  const boton = campo("avanzar");
  if (p.siguiente && puedeAvanzar) {
    boton.hidden = false;
    boton.textContent = `Pasar a ${p.siguiente.etiqueta}`;
    boton.dataset.avanzar = p.id;
    boton.dataset.estado = p.siguiente.estado;
  } else {
    boton.remove();
  }

  return nodo.outerHTML;
}
