// Todas las llamadas fetch al backend Flask.
// La sesión vive en una cookie de Flask, así que el frontend debe servirse
// desde el MISMO origen que la API (p. ej. detrás de Nginx). Si la API
// estuviera en otro sitio, cambia BASE.
export const BASE = "";

export class ApiError extends Error {
  constructor(status, data) {
    super(data?.mensaje || `Error ${status}`);
    this.status = status;
    this.data = data;
  }
}

async function request(path, { method = "GET", body } = {}) {
  const res = await fetch(BASE + path, {
    method,
    credentials: "include",
    headers: body !== undefined ? { "Content-Type": "application/json" } : {},
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new ApiError(res.status, data);
  return data;
}

const qs = (params) => {
  const s = new URLSearchParams(
    Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== "")
  ).toString();
  return s ? `?${s}` : "";
};

export const api = {
  // Auth (login y callback son redirecciones del navegador: ver loginUrl)
  me: () => request("/auth/me"),
  logout: () => request("/auth/logout", { method: "POST" }),
  loginUrl: (next = location.pathname + location.hash) =>
    `${BASE}/auth/login?next=${encodeURIComponent(next)}`,

  // Restaurantes
  getRestaurantes: (ciudad) => request(`/restaurantes/${qs({ ciudad })}`),
  getRestaurante: (id) => request(`/restaurantes/${id}`),
  createRestaurante: (data) => request("/restaurantes/", { method: "POST", body: data }),
  updateRestaurante: (id, data) => request(`/restaurantes/${id}`, { method: "PUT", body: data }),
  deleteRestaurante: (id) => request(`/restaurantes/${id}`, { method: "DELETE" }),

  // Platos
  getPlatos: (restaurante_id) => request(`/platos/${qs({ restaurante_id })}`),
  getPlato: (id) => request(`/platos/${id}`),
  createPlato: (data) => request("/platos/", { method: "POST", body: data }),
  updatePlato: (id, data) => request(`/platos/${id}`, { method: "PUT", body: data }),
  deletePlato: (id) => request(`/platos/${id}`, { method: "DELETE" }),

  // Pedidos del cliente
  getPedidos: () => request("/pedidos/"),
  getPedido: (id) => request(`/pedidos/${id}`),
  createPedido: (data) => request("/pedidos/", { method: "POST", body: data }),
  cancelarPedido: (id) => request(`/pedidos/${id}/cancelar`, { method: "POST" }),

  // Cocina
  getCola: () => request("/cocina/"),
  avanzarPedido: (id, estado) =>
    request(`/cocina/${id}/avanzar`, { method: "POST", body: { estado } }),

  // Empleados
  getEmpleados: () => request("/empleados/"),
  getEmpleado: (id) => request(`/empleados/${id}`),
  createEmpleado: (data) => request("/empleados/", { method: "POST", body: data }),
  updateEmpleado: (id, data) => request(`/empleados/${id}`, { method: "PUT", body: data }),
  deleteEmpleado: (id) => request(`/empleados/${id}`, { method: "DELETE" }),
};
