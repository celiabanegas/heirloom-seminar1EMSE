// Heirloom frontend: plain JavaScript, no build step. Hash routes:
//   #/                          home: create a cookbook or open one with its code
//   #/c/CODE                    recipes of a cookbook (+ search)
//   #/c/CODE/new                new recipe
//   #/c/CODE/r/ID               one recipe
//   #/c/CODE/r/ID/edit          edit a recipe ("your special touch")
//   #/c/CODE/discover           browse the catalog of classics
//   #/c/CODE/discover/ID        preview a catalog recipe and add it

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
const debounce = (fn, ms = 250) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };

let categories = [];
async function getCategories() {
  if (!categories.length) categories = await api("/api/catalog/categories");
  return categories;
}

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
  if (r.category) bits.push(`<span class="chip">${esc(r.category)}</span>`);
  if (r.minutes) bits.push(`<span>⏱ ${r.minutes} min</span>`);
  if (r.servings) bits.push(`<span>🍽 ${r.servings} ${r.servings === 1 ? "ración" : "raciones"}</span>`);
  if (r.author) bits.push(`<span>👤 ${esc(r.author)}</span>`);
  if (r.notes) bits.push(`<span class="touch">✨ Con tu toque</span>`);
  return bits.join("");
}

function recipeBody(r) {
  return `
    <div class="grid2 recipe-body">
      <section><h2>Ingredientes</h2><ul>${lines(r.ingredients).map((l) => `<li>${esc(l)}</li>`).join("") || "<li class='muted'>—</li>"}</ul></section>
      <section><h2>Preparación</h2><ol>${lines(r.steps).map((l) => `<li>${esc(l)}</li>`).join("") || "<li class='muted'>—</li>"}</ol></section>
    </div>`;
}

function setNav(book) {
  bookNav.innerHTML = `<a href="#/c/${book.code}">${esc(book.name)}</a>`;
}

// ---------- views ----------

function homeView() {
  bookNav.innerHTML = "";
  const last = lastBook();
  view.innerHTML = `
    <section class="hero">
      <h1>Las recetas de la familia, en un solo sitio.</h1>
      <p>Crea un recetario, compártelo con un enlace, descubre clásicos para añadir y dales tu toque. Sin cuentas ni contraseñas.</p>
    </section>
    ${last ? `<a class="card resume" href="#/c/${esc(last.code)}">Seguir en <strong>${esc(last.name)}</strong> →</a>` : ""}
    <div class="grid2">
      <form class="card" id="create">
        <h2>Nuevo recetario</h2>
        <label>Nombre<input name="name" required maxlength="80" placeholder="Recetas de la familia Banegas"></label>
        <label class="check"><input type="checkbox" name="starter" checked> Empezar con algunas recetas clásicas</label>
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
    const f = e.target.elements;
    try {
      const book = await api("/api/cookbooks", { method: "POST", body: { name: f.name.value, starter: f.starter.checked } });
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
  setNav(book);
  view.innerHTML = `
    <section class="book-head">
      <div>
        <h1>${esc(book.name)}</h1>
        <p class="muted">Código <code>${book.code}</code> · ${book.recipe_count} ${book.recipe_count === 1 ? "receta" : "recetas"}</p>
      </div>
      <div class="actions">
        <button class="btn ghost" id="share">Compartir</button>
        <a class="btn ghost" href="#/c/${book.code}/discover">🔍 Descubrir recetas</a>
        <a class="btn" href="#/c/${book.code}/new">+ Nueva receta</a>
      </div>
    </section>
    <input id="search" type="search" placeholder="Buscar en tu recetario: plato, ingrediente, autor…" aria-label="Buscar">
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
      : `<li class="card empty">${q
          ? `Ninguna receta coincide. <a href="#/c/${book.code}/discover">Busca en el catálogo →</a>`
          : `Todavía no hay recetas. <a href="#/c/${book.code}/discover">Descubre algunas</a> o apunta la primera.`}</li>`;
  }
  document.getElementById("search").oninput = debounce((e) => load(e.target.value));
  await load();
}

async function discoverView(code) {
  const [book, cats] = await Promise.all([api(`/api/cookbooks/${code}`), getCategories()]);
  setNav(book);
  view.innerHTML = `
    <section class="book-head">
      <div>
        <a class="back" href="#/c/${book.code}">← ${esc(book.name)}</a>
        <h1>Descubrir recetas</h1>
        <p class="muted">Añade un clásico a tu recetario y después dale tu toque.</p>
      </div>
    </section>
    <input id="search" type="search" placeholder="Busca: lentejas, huevo, horno, postre…" aria-label="Buscar en el catálogo">
    <div class="chips" id="cats">
      <button class="chip-btn on" data-cat="">Todas</button>
      ${cats.map((c) => `<button class="chip-btn" data-cat="${esc(c)}">${esc(c)}</button>`).join("")}
    </div>
    <ul id="list" class="cards"></ul>`;

  let q = "", cat = "";
  const list = document.getElementById("list");
  async function load() {
    const items = await api(`/api/catalog?q=${encodeURIComponent(q)}&category=${encodeURIComponent(cat)}`);
    list.innerHTML = items.length
      ? items.map((r) => `
          <li class="card catalog-card">
            <a href="#/c/${book.code}/discover/${r.id}"><strong>${esc(r.title)}</strong></a>
            <span class="meta">${meta(r)}</span>
            <p class="muted small">${esc(lines(r.ingredients).slice(0, 4).join(" · "))}…</p>
            <button class="btn small" data-add="${r.id}">+ Añadir</button>
          </li>`).join("")
      : `<li class="card empty">No hay recetas con esa búsqueda.</li>`;
  }
  document.getElementById("search").oninput = debounce((e) => { q = e.target.value; load(); });
  document.getElementById("cats").onclick = (e) => {
    const b = e.target.closest("[data-cat]");
    if (!b) return;
    cat = b.dataset.cat;
    document.querySelectorAll("#cats .chip-btn").forEach((x) => x.classList.toggle("on", x === b));
    load();
  };
  list.onclick = async (e) => {
    const b = e.target.closest("[data-add]");
    if (!b) return;
    b.disabled = true;
    const copy = await api(`/api/cookbooks/${book.code}/recipes/from-catalog/${b.dataset.add}`, { method: "POST" });
    b.outerHTML = `<a class="btn small ghost" href="#/c/${book.code}/r/${copy.id}/edit">✓ Añadida · Dale tu toque</a>`;
  };
  await load();
}

async function catalogPreview(code, id) {
  const r = await api(`/api/catalog/${id}`);
  view.innerHTML = `
    <article class="card recipe">
      <a class="back" href="#/c/${code}/discover">← Descubrir recetas</a>
      <h1>${esc(r.title)}</h1>
      <p class="meta">${meta(r)}</p>
      ${recipeBody(r)}
      <div class="actions"><button class="btn" id="add">+ Añadir a mi recetario</button></div>
    </article>`;
  document.getElementById("add").onclick = async () => {
    const copy = await api(`/api/cookbooks/${code}/recipes/from-catalog/${id}`, { method: "POST" });
    location.hash = `#/c/${code}/r/${copy.id}?added`;
  };
}

async function recipeView(code, id, justAdded) {
  const r = await api(`/api/cookbooks/${code}/recipes/${id}`);
  view.innerHTML = `
    <article class="card recipe">
      <a class="back" href="#/c/${code}">← Todas las recetas</a>
      ${justAdded ? `<p class="banner">Añadida a tu recetario. ¿La hacéis distinta en casa? <a href="#/c/${code}/r/${r.id}/edit">Dale tu toque ✨</a></p>` : ""}
      <h1>${esc(r.title)}</h1>
      <p class="meta">${meta(r)}</p>
      ${r.source_title && r.source_title !== r.title ? `<p class="muted small">Basada en «${esc(r.source_title)}» del catálogo</p>` : ""}
      ${r.notes ? `<aside class="touch-box"><h2>✨ Nuestro toque</h2>${lines(r.notes).map((l) => `<p>${esc(l)}</p>`).join("")}</aside>` : ""}
      ${recipeBody(r)}
      <div class="actions">
        <a class="btn" href="#/c/${code}/r/${r.id}/edit">${r.notes ? "Editar" : "✨ Dale tu toque"}</a>
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
  const [r, cats] = await Promise.all([id ? api(`/api/cookbooks/${code}/recipes/${id}`) : {}, getCategories()]);
  view.innerHTML = `
    <form class="card recipe-form" id="form">
      <a class="back" href="#/c/${code}${id ? `/r/${id}` : ""}">← Volver</a>
      <h1>${id ? "Editar receta" : "Nueva receta"}</h1>
      ${r.source_title ? `<p class="muted small">Basada en «${esc(r.source_title)}». Cámbiala a tu gusto: es tu copia.</p>` : ""}
      <label>Nombre del plato<input name="title" required maxlength="120" value="${esc(r.title)}" placeholder="Lentejas de la abuela"></label>
      <div class="grid4">
        <label>Quién la aporta<input name="author" maxlength="60" value="${esc(r.author)}" placeholder="Mamá"></label>
        <label>Categoría<select name="category"><option value="">—</option>${cats.map((c) => `<option ${c === r.category ? "selected" : ""}>${esc(c)}</option>`).join("")}</select></label>
        <label>Raciones<input name="servings" type="number" min="1" max="100" value="${esc(r.servings)}"></label>
        <label>Minutos<input name="minutes" type="number" min="1" value="${esc(r.minutes)}"></label>
      </div>
      <label class="touch-field">✨ Tu toque especial <small>(el truco, el cambio, el secreto de la familia)</small>
        <textarea name="notes" rows="3" placeholder="La abuela añade una pizca de comino y la deja reposar 10 minutos antes de servir.">${esc(r.notes)}</textarea></label>
      <label>Ingredientes <small>(uno por línea)</small>
        <textarea name="ingredients" rows="8" placeholder="300 g de lentejas&#10;1 chorizo&#10;2 zanahorias&#10;1,5 l de agua">${esc(r.ingredients)}</textarea></label>
      <label>Preparación <small>(un paso por línea)</small>
        <textarea name="steps" rows="8" placeholder="Poner las lentejas en remojo la noche anterior.&#10;Sofreír la verdura…">${esc(r.steps)}</textarea></label>
      <button class="btn">${id ? "Guardar cambios" : "Guardar receta"}</button>
    </form>`;

  document.getElementById("form").onsubmit = async (e) => {
    e.preventDefault();
    const f = e.target.elements;
    const num = (v) => (v === "" ? null : Number(v));
    const body = {
      title: f.title.value, author: f.author.value, category: f.category.value,
      servings: num(f.servings.value), minutes: num(f.minutes.value),
      ingredients: f.ingredients.value, steps: f.steps.value, notes: f.notes.value,
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
  const [path, query] = location.hash.replace(/^#\/?/, "").split("?");
  const parts = path.split("/").filter(Boolean);
  window.scrollTo(0, 0);
  try {
    if (parts[0] === "c" && parts[1]) {
      const code = parts[1].toUpperCase();
      if (parts[2] === "new") return await formView(code);
      if (parts[2] === "discover") return parts[3] ? await catalogPreview(code, parts[3]) : await discoverView(code);
      if (parts[2] === "r" && parts[3]) {
        return parts[4] === "edit" ? await formView(code, parts[3]) : await recipeView(code, parts[3], query === "added");
      }
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
