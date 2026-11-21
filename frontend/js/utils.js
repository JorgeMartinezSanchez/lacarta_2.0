// Utilidades compartidas por las vistas.

// Escapa texto antes de meterlo en un template HTML (evita XSS).
export function esc(valor) {
  return String(valor ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[c]);
}

export const dinero = (n) => `$${Number(n ?? 0).toFixed(2)}`;

export const fecha = (iso) => (iso ? new Date(iso).toLocaleDateString("es-BO") : "");

// Lee un <form> como objeto plano.
export const datosForm = (form) => Object.fromEntries(new FormData(form));

export const navegar = (hash) => {
  location.hash = hash;
};
