// Estado global de la app: quién inició sesión y los mensajes "flash".
import { api } from "./api.js";

export const state = {
  usuario: null, // { name, email, sub, permissions } o null
  mensajes: [], // [{ tipo: "exito" | "error", texto }]
};

export async function cargarUsuario() {
  try {
    state.usuario = (await api.me()).usuario;
  } catch {
    state.usuario = null;
  }
}

// Ocultar botones es solo UX: el backend vuelve a comprobar cada permiso.
export const puede = (permiso) => !!state.usuario?.permissions?.includes(permiso);

// Mensaje que se mostrará en la próxima vista que se renderice.
export function flash(texto, tipo = "exito") {
  state.mensajes.push({ tipo, texto });
}

export function tomarMensajes() {
  const m = state.mensajes;
  state.mensajes = [];
  return m;
}
