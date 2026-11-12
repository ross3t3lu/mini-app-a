const form = document.querySelector("#options-form");
const lengthInput = document.querySelector("#length-input");
const lengthValue = document.querySelector("#length-value");
const output = document.querySelector("#password-output");
const copyButton = document.querySelector("#copy-button");
const strengthBar = document.querySelector("#strength-bar");
const strengthLabel = document.querySelector("#strength-label");
const entropyLabel = document.querySelector("#entropy-label");
const historyList = document.querySelector("#history-list");
const errorMessage = document.querySelector("#error-message");

const STRENGTH_STYLES = {
  "Débil": { width: "25%", className: "is-weak" },
  "Aceptable": { width: "50%", className: "is-fair" },
  "Fuerte": { width: "75%", className: "is-strong" },
  "Muy fuerte": { width: "100%", className: "is-very-strong" },
};
const HISTORY_LIMIT = 5;
const history = [];

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.classList.remove("hidden");
  window.setTimeout(() => errorMessage.classList.add("hidden"), 4500);
}

function readOptions() {
  const data = new FormData(form);
  return {
    length: Number(lengthInput.value),
    uppercase: data.has("uppercase"),
    lowercase: data.has("lowercase"),
    digits: data.has("digits"),
    symbols: data.has("symbols"),
    exclude_ambiguous: data.has("exclude_ambiguous"),
    count: 1,
  };
}

async function generate() {
  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(readOptions()),
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = typeof body.detail === "string" ? body.detail : null;
      throw new Error(detail || "No pudimos generar la contraseña.");
    }
    render(body.passwords[0]);
  } catch (error) {
    showError(error.message);
  }
}

function render(result) {
  output.textContent = result.password;
  copyButton.textContent = "Copiar";

  const style = STRENGTH_STYLES[result.strength];
  strengthBar.style.width = style.width;
  strengthBar.className = `strength-bar ${style.className}`;
  strengthLabel.textContent = result.strength;
  entropyLabel.textContent = `${result.entropy_bits} bits de entropía`;

  history.unshift(result.password);
  history.length = Math.min(history.length, HISTORY_LIMIT);
  renderHistory();
}

function renderHistory() {
  historyList.replaceChildren(
    ...history.map((password) => {
      const item = document.createElement("li");
      const text = document.createElement("code");
      text.textContent = password;
      const button = document.createElement("button");
      button.type = "button";
      button.className = "history-copy";
      button.textContent = "Copiar";
      button.addEventListener("click", () => copy(password, button));
      item.append(text, button);
      return item;
    }),
  );
}

async function copy(text, button) {
  try {
    await navigator.clipboard.writeText(text);
    button.textContent = "¡Copiada!";
    window.setTimeout(() => (button.textContent = "Copiar"), 1800);
  } catch {
    showError("No pudimos copiar al portapapeles.");
  }
}

lengthInput.addEventListener("input", () => {
  lengthValue.textContent = lengthInput.value;
});
lengthInput.addEventListener("change", generate);
form.querySelectorAll('input[type="checkbox"]').forEach((input) =>
  input.addEventListener("change", generate),
);
form.addEventListener("submit", (event) => {
  event.preventDefault();
  generate();
});
document.querySelector("#regenerate-button").addEventListener("click", generate);
copyButton.addEventListener("click", () => {
  if (history.length) copy(history[0], copyButton);
});

generate();
