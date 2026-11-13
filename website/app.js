"use strict";

const grid = document.querySelector("#grid");
const status = document.querySelector("#status");
const count = document.querySelector("#count");
const search = document.querySelector("#search");
const year = document.querySelector("#year");
const tag = document.querySelector("#tag");
const sort = document.querySelector("#sort");
const themeToggle = document.querySelector("#theme-toggle");
let presentations = [];

function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  themeToggle.setAttribute("aria-label", `Switch to ${theme === "dark" ? "light" : "dark"} mode`);
}

let savedTheme;
try { savedTheme = localStorage.getItem("theme"); } catch (error) { console.warn("Theme preference is unavailable:", error); }
setTheme(savedTheme === "light" || savedTheme === "dark" ? savedTheme : (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"));
themeToggle.addEventListener("click", () => {
  const theme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  setTheme(theme);
  try { localStorage.setItem("theme", theme); } catch (error) { console.warn("Could not save theme preference:", error); }
});

function textElement(element, className, text) {
  const node = document.createElement(element);
  node.className = className;
  node.textContent = text;
  return node;
}

function cardFor(item, index) {
  const card = document.createElement("article");
  card.className = "card";
  const top = document.createElement("div");
  top.className = "card-top";
  top.append(textElement("span", "card-type", "RESEARCH PRESENTATION"), textElement("span", "card-number", String(index + 1).padStart(2, "0")));
  card.append(top, textElement("h3", "card-title", item.title));
  const authors = Array.isArray(item.authors) ? item.authors.join(", ") : item.authors;
  const details = [authors, item.year].filter(value => value !== undefined && value !== null && String(value).trim()).join(" · ");
  if (details) card.append(textElement("p", "card-details", details));
  if (item.description) card.append(textElement("p", "card-description", item.description));
  if (item.tags && item.tags.length) {
    const tags = document.createElement("div");
    tags.className = "tags";
    item.tags.forEach(value => tags.append(textElement("span", "tag", value)));
    card.append(tags);
  }
  const link = document.createElement("a");
  link.className = "card-link";
  link.href = item.url;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.append(document.createTextNode("View Slides "), textElement("span", "", "↗"));
  link.setAttribute("aria-label", `View slides: ${item.title} (opens in a new tab)`);
  card.append(link);
  return card;
}

function render() {
  const query = search.value.trim().toLocaleLowerCase();
  const filtered = presentations.filter(item => {
    const text = [item.title, item.authors, item.year, item.description, item.tags].flat().filter(Boolean).join(" ").toLocaleLowerCase();
    return text.includes(query) && (!year.value || String(item.year) === year.value) && (!tag.value || (item.tags || []).includes(tag.value));
  });
  filtered.sort((a, b) => a.title.localeCompare(b.title, undefined, { sensitivity: "base" }) * (sort.value === "desc" ? -1 : 1));
  count.textContent = `${presentations.length} ${presentations.length === 1 ? "presentation" : "presentations"}${filtered.length !== presentations.length ? ` · ${filtered.length} shown` : ""}`;
  const groups = new Map();
  filtered.forEach(item => {
    const key = item.year !== undefined && item.year !== null && String(item.year).trim() ? String(item.year) : "Year not specified";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(item);
  });
  const orderedGroups = [...groups].sort(([a], [b]) => {
    if (a === "Year not specified") return 1;
    if (b === "Year not specified") return -1;
    return b.localeCompare(a, undefined, { numeric: true });
  });
  let index = 0;
  grid.replaceChildren(...orderedGroups.map(([label, items]) => {
    const section = document.createElement("section");
    section.className = "year-group";
    section.append(textElement("h3", "year-heading", label));
    const cards = document.createElement("div");
    cards.className = "grid";
    cards.append(...items.map(item => cardFor(item, index++)));
    section.append(cards);
    return section;
  }));
  status.textContent = filtered.length ? "" : (presentations.length ? "No presentations match your search. Try another term or filter." : "The library is empty. Check back soon.");
}

function addOptions(select, values) {
  values.forEach(value => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.append(option);
  });
}

[search, year, tag, sort].forEach(control => control.addEventListener("input", render));
fetch("catalog.json")
  .then(response => {
    if (!response.ok) throw new Error(`Catalog request failed (${response.status})`);
    return response.json();
  })
  .then(data => {
    if (!Array.isArray(data)) throw new Error("Catalog is not an array");
    presentations = data;
    addOptions(year, [...new Set(data.filter(item => item.year !== undefined && String(item.year).trim()).map(item => String(item.year)))].sort((a, b) => b.localeCompare(a, undefined, { numeric: true })));
    addOptions(tag, [...new Set(data.flatMap(item => item.tags || []).filter(Boolean))].sort((a, b) => a.localeCompare(b)));
    render();
  })
  .catch(error => {
    console.error(error);
    count.textContent = "Collection unavailable";
    status.textContent = "The presentation catalog could not be loaded. Please try again later.";
  });
