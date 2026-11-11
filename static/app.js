const homeScreen = document.querySelector("#home-screen");
const quizScreen = document.querySelector("#quiz-screen");
const resultScreen = document.querySelector("#result-screen");
const categoriesContainer = document.querySelector("#categories");
const errorMessage = document.querySelector("#error-message");

const state = {
  category: "",
  questions: [],
  questionIndex: 0,
  score: 0,
  answered: false,
};

const letters = ["A", "B", "C", "D"];

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.classList.remove("hidden");
  window.setTimeout(() => errorMessage.classList.add("hidden"), 4500);
}

async function request(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "No pudimos completar la solicitud.");
  }
  return response.json();
}

async function loadCategories() {
  try {
    const categories = await request("/api/categories");
    categoriesContainer.replaceChildren(
      ...categories.map((category) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = `category-card category-${category.color}`;
        button.setAttribute("aria-label", `Jugar ${category.name}`);

        const icon = document.createElement("span");
        icon.className = "category-icon";
        icon.setAttribute("aria-hidden", "true");
        icon.textContent = category.icon;
        const name = document.createElement("span");
        name.className = "category-name";
        name.textContent = category.name;
        const description = document.createElement("span");
        description.className = "category-description";
        description.textContent = category.description;
        const count = document.createElement("span");
        count.className = "category-arrow";
        count.textContent = `${category.question_count} preguntas ↗`;

        button.append(icon, name, description, count);
        button.addEventListener("click", () => startQuiz(category.name));
        return button;
      }),
    );
  } catch {
    categoriesContainer.innerHTML =
      '<p class="loading-categories">No pudimos cargar las categorías. Recarga la página para intentarlo de nuevo.</p>';
  }
}

async function startQuiz(category) {
  try {
    state.category = category;
    state.questions = await request(
      `/api/questions?category=${encodeURIComponent(category)}&limit=10`,
    );
    state.questionIndex = 0;
    state.score = 0;
    state.answered = false;
    homeScreen.classList.add("hidden");
    resultScreen.classList.add("hidden");
    quizScreen.classList.remove("hidden");
    renderQuestion();
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (error) {
    showError(error.message);
  }
}

function renderQuestion() {
  const question = state.questions[state.questionIndex];
  if (!question) {
    showResults();
    return;
  }

  state.answered = false;
  document.querySelector("#quiz-category").textContent = question.category;
  document.querySelector("#question-count").textContent =
    `${String(state.questionIndex + 1).padStart(2, "0")} / ${String(state.questions.length).padStart(2, "0")}`;
  document.querySelector("#progress-bar").style.width =
    `${((state.questionIndex + 1) / state.questions.length) * 100}%`;
  document.querySelector("#question-difficulty").textContent = question.difficulty;
  document.querySelector("#question-text").textContent = question.question;
  document.querySelector("#feedback").classList.add("hidden");
  document.querySelector("#next-button").classList.add("hidden");

  const answerList = document.querySelector("#answer-list");
  answerList.replaceChildren(
    ...question.options.map((option, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "answer-option";
      const letter = document.createElement("span");
      letter.className = "option-letter";
      letter.textContent = letters[index];
      const text = document.createElement("span");
      text.textContent = option;
      button.append(letter, text);
      button.addEventListener("click", () => submitAnswer(index));
      return button;
    }),
  );
}

async function submitAnswer(optionIndex) {
  if (state.answered) return;
  state.answered = true;
  const question = state.questions[state.questionIndex];
  const options = [...document.querySelectorAll(".answer-option")];
  options.forEach((option) => (option.disabled = true));

  try {
    const result = await request("/api/answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question_id: question.id, option_index: optionIndex }),
    });

    options[result.correct_index].classList.add("is-correct");
    if (result.correct) {
      state.score += 1;
    } else {
      options[optionIndex].classList.add("is-incorrect");
    }

    const feedback = document.querySelector("#feedback");
    const heading = document.createElement("strong");
    heading.textContent = result.correct ? "¡Muy bien!" : "Casi, ¡la próxima!";
    const explanation = document.createElement("span");
    explanation.textContent = result.explanation;
    feedback.replaceChildren(heading, explanation);
    feedback.classList.remove("hidden");

    const nextButton = document.querySelector("#next-button");
    nextButton.querySelector("span").textContent =
      state.questionIndex + 1 === state.questions.length ? "✦" : "→";
    nextButton.classList.remove("hidden");
    nextButton.focus();
  } catch (error) {
    state.answered = false;
    options.forEach((option) => (option.disabled = false));
    showError(error.message);
  }
}

function showResults() {
  quizScreen.classList.add("hidden");
  resultScreen.classList.remove("hidden");

  const percentage = state.score / state.questions.length;
  const title = percentage === 1 ? "¡Imparable!" : percentage >= 0.6 ? "¡Muy bien hecho!" : "¡Qué buena ronda!";
  const copy =
    percentage === 1
      ? "No se te escapa ni un dato. Se nota esa mente curiosa."
      : percentage >= 0.6
        ? "Sabes un montón. Y ahora te llevas algún dato nuevo."
        : "Cada pregunta es una oportunidad para descubrir algo nuevo.";

  document.querySelector("#result-title").textContent = title;
  document.querySelector("#result-copy").textContent = copy;
  document.querySelector("#result-icon").textContent = percentage >= 0.6 ? "✦" : "✳";
  document.querySelector("#final-score").textContent = state.score;
  document.querySelector("#score-total").textContent = `/ ${state.questions.length}`;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

document.querySelector("#next-button").addEventListener("click", () => {
  state.questionIndex += 1;
  renderQuestion();
});
document.querySelector("#back-button").addEventListener("click", () => {
  quizScreen.classList.add("hidden");
  homeScreen.classList.remove("hidden");
});
document.querySelector("#replay-button").addEventListener("click", () => startQuiz(state.category));
document.querySelector("#home-button").addEventListener("click", () => {
  resultScreen.classList.add("hidden");
  homeScreen.classList.remove("hidden");
});

loadCategories();
