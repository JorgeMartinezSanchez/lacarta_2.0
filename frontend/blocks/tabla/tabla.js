// Bloque "tabla": arma el <table> con sus clases BEM.
// Las celdas llegan como HTML ya escapado (usa esc() en la vista).
//
//   pintarTabla({
//     columnas: ["Plato", "Precio"],
//     filas: platos.map((p) => [esc(p.nombre), dinero(p.precio)]),
//     pie: [{ html: "Total", colspan: 1 }, { html: dinero(total), id: "total" }],
//   })

const celda = (contenido, tag = "td", titulo = false) => {
  const c = typeof contenido === "object" && contenido !== null ? contenido : { html: contenido };
  const clases = titulo ? "tabla__celda tabla__celda--titulo" : "tabla__celda";
  const attrs = `${c.colspan ? ` colspan="${c.colspan}"` : ""}${c.id ? ` id="${c.id}"` : ""}`;
  return `<${tag} class="${clases}"${attrs}>${c.html ?? ""}</${tag}>`;
};

export function pintarTabla({ columnas, filas, pie }) {
  return `
    <table class="tabla">
      <thead class="tabla__cabecera">
        <tr>${columnas.map((c) => celda(c, "th", true)).join("")}</tr>
      </thead>
      <tbody>
        ${filas.map((f) => `<tr>${f.map((c) => celda(c)).join("")}</tr>`).join("")}
      </tbody>
      ${pie ? `<tfoot><tr>${pie.map((c) => celda(c, "th", true)).join("")}</tr></tfoot>` : ""}
    </table>`;
}
