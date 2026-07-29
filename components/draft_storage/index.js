const STORAGE_KEY = "brujula_democratica_draft";

export default function (component) {
  const { data, setStateValue } = component;

  const operation = data?.operation;

  if (operation === "read") {
    let storedDraft = null;
    try {
      storedDraft = window.localStorage.getItem(STORAGE_KEY);
    } catch {
      storedDraft = null;
    }
    setStateValue("draft", storedDraft);
    return;
  }

  if (operation === "save" && typeof data?.payload === "string") {
    try {
      if (window.localStorage.getItem(STORAGE_KEY) !== data.payload) {
        window.localStorage.setItem(STORAGE_KEY, data.payload);
      }
    } catch {
      // El cuestionario sigue funcionando si el navegador bloquea localStorage.
    }
    return;
  }

  if (operation === "clear") {
    try {
      window.localStorage.removeItem(STORAGE_KEY);
    } catch {
      // La limpieza no debe interrumpir el resultado ni el reinicio.
    }
  }
}
