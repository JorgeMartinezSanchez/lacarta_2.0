// Punto de entrada: carga quién inició sesión y arranca el router.
import { iniciarRouter } from "./router.js";
import { cargarUsuario } from "./state.js";

await cargarUsuario();
iniciarRouter();
