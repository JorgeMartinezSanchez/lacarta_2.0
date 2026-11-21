// Router por hash: #/platos/3 -> PlatoDetalle({ id: "3" }).
// Usar el hash evita chocar con las rutas de Flask (/platos/, /auth/...)
// cuando ambos se sirven desde el mismo dominio.
import { Mensajes } from "./components/mensajes.js";
import { Navbar, montarNavbar } from "./components/navbar.js";
import { Cocina } from "./views/cocina.js";
import { EmpleadoDetalle } from "./views/empleados/detalle.js";
import { EmpleadoFormulario } from "./views/empleados/formulario.js";
import { EmpleadosLista } from "./views/empleados/lista.js";
import { ErrorView } from "./views/errores/error.js";
import { PedidoDetalle } from "./views/pedidos/detalle.js";
import { PedidoFormulario } from "./views/pedidos/formulario.js";
import { PedidosLista } from "./views/pedidos/lista.js";
import { PlatoDetalle } from "./views/platos/detalle.js";
import { PlatoFormulario } from "./views/platos/formulario.js";
import { PlatosLista } from "./views/platos/lista.js";
import { RestauranteDetalle } from "./views/restaurantes/detalle.js";
import { RestauranteFormulario } from "./views/restaurantes/formulario.js";
import { RestaurantesLista } from "./views/restaurantes/lista.js";

// El orden importa: "nuevo" va antes de ":id".
const routes = [
  ["/restaurantes", RestaurantesLista],
  ["/restaurantes/nuevo", RestauranteFormulario],
  ["/restaurantes/:id", RestauranteDetalle],
  ["/restaurantes/:id/editar", RestauranteFormulario],
  ["/platos", PlatosLista],
  ["/platos/nuevo", PlatoFormulario],
  ["/platos/:id", PlatoDetalle],
  ["/platos/:id/editar", PlatoFormulario],
  ["/pedidos", PedidosLista],
  ["/pedidos/nuevo", PedidoFormulario],
  ["/pedidos/:id", PedidoDetalle],
  ["/cocina", Cocina],
  ["/empleados", EmpleadosLista],
  ["/empleados/nuevo", EmpleadoFormulario],
  ["/empleados/:id", EmpleadoDetalle],
  ["/empleados/:id/editar", EmpleadoFormulario],
].map(([patron, view]) => ({
  regex: new RegExp("^" + patron.replace(/:(\w+)/g, "(?<$1>\\d+)") + "/?$"),
  view,
}));

function resolver() {
  const [path, search = ""] = (location.hash.slice(1) || "/restaurantes").split("?");
  const query = new URLSearchParams(search);
  for (const { regex, view } of routes) {
    const m = path.match(regex);
    if (m) return { view, params: m.groups ?? {}, query };
  }
  return { view: null, params: {}, query };
}

let renderActual = 0;

export async function render() {
  const app = document.getElementById("app");
  const id = ++renderActual;
  const { view, params, query } = resolver();

  let resultado;
  try {
    resultado = view ? await view(params, query) : ErrorView(404);
  } catch (e) {
    console.error(e);
    resultado = ErrorView(e.status || 500, e.status === 400 || e.status === 404 ? e.message : undefined);
  }
  if (id !== renderActual) return; // el usuario ya navegó a otra vista

  app.innerHTML = `${Navbar()}<main class="pagina">${Mensajes()}${resultado.html}</main>`;
  montarNavbar();
  resultado.mount?.();
  window.scrollTo(0, 0);
}

export function iniciarRouter() {
  window.addEventListener("hashchange", render);
  return render();
}
