// Heirloom frontend: plain JavaScript, no build step. Hash routes:
//   #/                    home: create a cookbook or open one with its code
//   #/c/CODE              recipes of a cookbook (+ search)
//   #/c/CODE/new          new recipe
//   #/c/CODE/r/ID         one recipe
//   #/c/CODE/r/ID/edit    edit a recipe

const API = (window.HEIRLOOM_CONFIG?.apiUrl || "").replace(/\/$/, "");
const view = document.getElementById("view");
const bookNav = document.getElementById("book-nav");

// ---------- helpers ----------

async function api(path, options = {}) {
  const res = await fetch(API + path, {
    ...options,
    headers: { "Content-Type": "application/json" },
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw Object.assign(new Error(data.detail || res.statusText), { status: res.status });
  return data;
}

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const lines = (s) => String(s || "").split("\n").map((l) => l.trim()).filter(Boolean);
const shareUrl = (code) => `${location.origin}${location.pathname}#/c/${code}`;

function remember(book) {
  try { localStorage.setItem("heirloom:last", JSON.stringify({ code: book.code, name: book.name })); } catch {}
}
function lastBook() {
  try { return JSON.parse(localStorage.getItem("heirloom:last")); } catch { return null; }
}

function showError(err) {
  const msg = err.status === 404 ? "No lo encontramos. ¿El código es correcto?" : `Algo ha fallado: ${esc(err.message)}`;
  view.innerHTML = `<section class="card empty"><p>${msg}</p><a class="btn" href="#/">Volver al inicio</a></section>`;
}

function meta(r) {
  const bits = [];
  if (r.minutes) bits.push(`⏱ ${r.minutes} min`);
  if (r.servings) bits.push(`🍽 ${r.servings} ${r.servings === 1 ? "ración" : "raciones"}`);
  if (r.author) bits.push(`👤 ${esc(r.author)}`);
  return bits.map((b) => `<span>${b}</span>`).join("");
}

// ---------- views ----------

function homeView() {
  bookNav.innerHTML = "";
  const last = lastBook();
  view.innerHTML = `
    <section class="hero">
      <h1>Las recetas de la familia, en un solo sitio.</h1>
      <p>Crea un recetario, comparte el enlace y que cada uno apunte sus platos. Sin cuentas ni contraseñas.</p>
    </section>
    ${last ? `<a class="card resume" href="#/c/${esc(last.code)}">Seguir en <strong>${esc(last.name)}</strong> →</a>` : ""}
    <div class="grid2">
      <form class="card" id="create">
        <h2>Nuevo recetario</h2>
        <label>Nombre<input name="name" required maxlength="80" placeholder="Recetas de la familia Banegas"></label>
        <button class="btn">Crear</button>
      </form>
      <form class="card" id="join">
        <h2>Tengo un código</h2>
        <label>Código<input name="code" required maxlength="8" placeholder="ABCD2345" autocapitalize="characters"></label>
        <button class="btn ghost">Abrir</button>
      </form>
    </div>`;

  document.getElementById("create").onsubmit = async (e) => {
    e.preventDefault();
    try {
      const book = await api("/api/cookbooks", { method: "POST", body: { name: e.target.elements.name.value } });
      remember(book);
      location.hash = `#/c/${book.code}`;
    } catch (err) { showError(err); }
  };
  document.getElementById("join").onsubmit = (e) => {
    e.preventDefault();
    location.hash = `#/c/${e.target.elements.code.value.trim().toUpperCase()}`;
  };
}

async function bookView(code) {
  const book = await api(`/api/cookbooks/${code}`);
  remember(book);
  bookNav.innerHTML = `<a href="#/c/${book.code}">${esc(book.name)}</a>`;
  view.innerHTML = `
    <section class="book-head">
      <div>
        <h1>${esc(book.name)}</h1>
        <p class="muted">Código <code>${book.code}</code> · ${book.recipe_count} ${book.recipe_count === 1 ? "receta" : "recetas"}</p>
      </div>
      <div class="actions">
        <button class="btn ghost" id="share">Compartir</button>
        <a class="btn" href="#/c/${book.code}/new">+ Nueva receta</a>
      </div>
    </section>
    <input id="search" type="search" placeholder="Buscar por plato, ingrediente o autor…" aria-label="Buscar">
    <ul id="list" class="list"></ul>`;

  document.getElementById("share").onclick = async () => {
    const url = shareUrl(book.code);
    if (navigator.share) {
      navigator.share({ title: book.name, text: `Nuestro recetario: ${book.name}`, url }).catch(() => {});
    } else {
      await navigator.clipboard?.writeText(url);
      document.getElementById("share").textContent = "¡Enlace copiado!";
    }
  };

  const list = document.getElementById("list");
  async function load(q = "") {
    const recipes = await api(`/api/cookbooks/${book.code}/recipes?q=${encodeURIComponent(q)}`);
    list.innerHTML = recipes.length
      ? recipes.map((r) => `
          <li><a class="card recipe-row" href="#/c/${book.code}/r/${r.id}">
            <strong>${esc(r.title)}</strong><span class="meta">${meta(r)}</span>
          </a></li>`).join("")
      : `<li class="card empty">${q ? "Ninguna receta coincide." : "Todavía no hay recetas. ¡Apunta la primera!"}</li>`;
  }
  let t;
  document.getElementById("search").oninput = (e) => { clearTimeout(t); t = setTimeout(() => load(e.target.value), 250); };
  await load();
}

async function recipeView(code, id) {
  const r = await api(`/api/cookbooks/${code}/recipes/${id}`);
  view.innerHTML = `
    <article class="card recipe">
      <a class="back" href="#/c/${code}">← Todas las recetas</a>
      <h1>${esc(r.title)}</h1>
      <p class="meta">${meta(r)}</p>
      <div class="grid2 recipe-body">
        <section><h2>Ingredientes</h2><ul>${lines(r.ingredients).map((l) => `<li>${esc(l)}</li>`).join("") || "<li class='muted'>—</li>"}</ul></section>
        <section><h2>Preparación</h2><ol>${lines(r.steps).map((l) => `<li>${esc(l)}</li>`).join("") || "<li class='muted'>—</li>"}</ol></section>
      </div>
      <div class="actions">
        <a class="btn ghost" href="#/c/${code}/r/${r.id}/edit">Editar</a>
        <button class="btn danger" id="del">Borrar</button>
      </div>
    </article>`;
  const del = document.getElementById("del");
  del.onclick = async () => {
    if (!del.dataset.sure) { del.dataset.sure = "1"; del.textContent = "¿Seguro? Pulsa otra vez"; return; }
    await api(`/api/cookbooks/${code}/recipes/${r.id}`, { method: "DELETE" });
    location.hash = `#/c/${code}`;
  };
}

async function formView(code, id) {
  const r = id ? await api(`/api/cookbooks/${code}/recipes/${id}`) : {};
  view.innerHTML = `
    <form class="card recipe-form" id="form">
      <a class="back" href="#/c/${code}${id ? `/r/${id}` : ""}">← Volver</a>
      <h1>${id ? "Editar receta" : "Nueva receta"}</h1>
      <label>Nombre del plato<input name="title" required maxlength="120" value="${esc(r.title)}" placeholder="Lentejas de la abuela"></label>
      <div class="grid3">
        <label>Quién la aporta<input name="author" maxlength="60" value="${esc(r.author)}" placeholder="Mamá"></label>
        <label>Raciones<input name="servings" type="number" min="1" max="100" value="${esc(r.servings)}"></label>
        <label>Minutos<input name="minutes" type="number" min="1" value="${esc(r.minutes)}"></label>
      </div>
      <label>Ingredientes <small>(uno por línea)</small>
        <textarea name="ingredients" rows="7" placeholder="300 g de lentejas&#10;1 chorizo&#10;2 zanahorias&#10;1 l de agua">${esc(r.ingredients)}</textarea></label>
      <label>Preparación <small>(un paso por línea)</small>
        <textarea name="steps" rows="7" placeholder="Poner las lentejas en remojo la noche anterior.&#10;Sofreír la verdura…">${esc(r.steps)}</textarea></label>
      <button class="btn">${id ? "Guardar cambios" : "Guardar receta"}</button>
    </form>`;

  document.getElementById("form").onsubmit = async (e) => {
    e.preventDefault();
    const f = e.target.elements;
    const num = (v) => (v === "" ? null : Number(v));
    const body = {
      title: f.title.value, author: f.author.value, servings: num(f.servings.value), minutes: num(f.minutes.value),
      ingredients: f.ingredients.value, steps: f.steps.value,
    };
    try {
      const saved = id
        ? await api(`/api/cookbooks/${code}/recipes/${id}`, { method: "PUT", body })
        : await api(`/api/cookbooks/${code}/recipes`, { method: "POST", body });
      location.hash = `#/c/${code}/r/${saved.id}`;
    } catch (err) { showError(err); }
  };
}

// ---------- router ----------

async function route() {
  const parts = location.hash.replace(/^#\/?/, "").split("/").filter(Boolean);
  window.scrollTo(0, 0);
  try {
    if (parts[0] === "c" && parts[1]) {
      const code = parts[1].toUpperCase();
      if (parts[2] === "new") return await formView(code);
      if (parts[2] === "r" && parts[3]) return parts[4] === "edit" ? await formView(code, parts[3]) : await recipeView(code, parts[3]);
      return await bookView(code);
    }
    homeView();
  } catch (err) { showError(err); }
}

async function checkApi() {
  const el = document.getElementById("api-status");
  try {
    const h = await api("/health");
    el.textContent = `API conectada · versión ${String(h.version).slice(0, 7)}`;
    el.className = "ok";
  } catch {
    el.textContent = "La API no responde (puede estar arrancando, prueba en unos segundos)";
    el.className = "bad";
  }
}

window.addEventListener("hashchange", route);
route();
checkApi();
