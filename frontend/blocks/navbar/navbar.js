import { api } from "../api.js";
import { state, puede } from "../state.js";
import { esc } from "../utils.js";

export function Navbar() {
  const u = state.usuario;
  return `
    <header>
      <nav class="navbar">
        <a href="#/restaurantes" class="navbar__marca">La Carta</a>
        <a class="navbar__enlace" href="#/restaurantes">Restaurantes</a>
        <a class="navbar__enlace" href="#/platos">Platos</a>
        ${puede("read:mis-pedidos") ? `<a class="navbar__enlace" href="#/pedidos">Mis pedidos</a>` : ""}
        ${puede("read:pedidos") ? `<a class="navbar__enlace" href="#/cocina">Cocina</a>` : ""}
        ${puede("read:empleados") ? `<a class="navbar__enlace" href="#/empleados">Empleados</a>` : ""}
        <span class="navbar__espacio"></span>
        ${u
          ? `<span class="navbar__usuario">${esc(u.name || u.email)}</span>
             <button class="boton boton--secundario" type="button" id="btn-logout">Cerrar sesión</button>`
          : `<a class="navbar__enlace" href="${api.loginUrl()}">Iniciar sesión</a>`}
      </nav>
    </header>`;
}

export function montarNavbar() {
  document.getElementById("btn-logout")?.addEventListener("click", async () => {
    const { logout_url } = await api.logout();
    location.href = logout_url;
  });
}
