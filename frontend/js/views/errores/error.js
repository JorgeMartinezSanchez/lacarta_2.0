import { api } from "../../api.js";
import { esc } from "../../utils.js";

// Reemplaza a errores/404.html, errores/500.html, auth/forbidden.html y auth/signin.html.
const TEXTOS = {
  401: ["Inicia sesión", "Necesitas iniciar sesión para ver esta página."],
  403: ["Acceso denegado", "No tienes permiso para ver esta página."],
  404: ["Página no encontrada", "Lo que buscas no existe o fue eliminado."],
  500: ["Error del servidor", "Ocurrió un error inesperado. Intenta de nuevo más tarde."],
};

export function ErrorView(status = 404, mensaje) {
  const [titulo, texto] = TEXTOS[status] || [`Error ${status}`, "Algo salió mal."];
  return {
    html: `
      <h1>${esc(titulo)}</h1>
      <p>${esc(mensaje || texto)}</p>
      ${status === 401
        ? `<p><a href="${api.loginUrl()}" class="boton">Iniciar sesión</a></p>`
        : status === 403
        ? `<p><a href="${api.loginUrl()}&force=1">Entrar con otra cuenta</a></p>`
        : ""}
      <p><a href="#/restaurantes">Volver al inicio</a></p>`,
  };
}
