const $ = (s) => document.querySelector(s),
  esc = (s) =>
    String(s).replace(
      /[&<>"]/g,
      (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c],
    );
let page = "files",
  current = 1,
  next = 0,
  ignored = false,
  photoURL = "";
const files = [],
  pics = [
    { id: "p1", name: "Prise 1", deleted: false },
    { id: "p2", name: "Prise 2", deleted: false },
  ];
function add(name, parent, dir = false, size = "—") {
  const item = { id: ++next, name, parent, dir, size, deleted: false };
  files.push(item);
  return item.id;
}
const docs = add("Documents", 0, true),
  house = add("Maison", docs, true),
  school = add("École", docs, true),
  trip = add("Vacances", docs, true);
add("Assurance habitation.pdf", docs, false, "1,4 Mo");
add("Liste de courses.txt", docs, false, "4 Ko");
add("État des lieux.pdf", house, false, "820 Ko");
add("Calendrier scolaire.pdf", school, false, "310 Ko");
add("Réservations.pdf", trip, false, "150 Ko");
const fallback = "crique.webp";
const photo = () => photoURL || fallback;
const file = (id) => files.find((i) => i.id === Number(id));
const paths = {
  files: "M2 6h7l2 2h11v12H2z",
  photos: "M3 4h18v16H3z M4 18l6-7 5 5 3-3 3 3",
  review:
    "M10 4l2 5 5 2-5 2-2 5-2-5-5-2 5-2z M18 2l1 3 3 1-3 1-1 3-1-3-3-1 3-1z",
  trash: "M3 6h18 M9 6V3h6v3 M6 6l1 15h10l1-15 M10 10v7 M14 10v7",
  doc: "M5 2h9l5 5v15H5z M14 2v6h5 M8 13h8 M8 17h6",
};
function svgIcon(n) {
  return (
    '<svg class="sym" viewBox="0 0 24 24" aria-hidden="true"><path d="' +
    paths[n] +
    '"/></svg>'
  );
}
document
  .querySelectorAll("nav button")
  .forEach((b) => b.insertAdjacentHTML("afterbegin", svgIcon(b.dataset.view)));
function dialog(html) {
  $("#details").innerHTML = html;
  $("#modal").showModal();
}
function note(s) {
  $("#status").textContent = s;
}
function photoTile(p) {
  return (
    '<button data-zoom="' +
    p.id +
    '" aria-label="Agrandir ' +
    p.name +
    '"><img class="' +
    (p.id === "p2" ? "soft" : "") +
    '" src="' +
    photo() +
    '" alt="' +
    p.name +
    '"></button>'
  );
}
function loadControl() {
  return '<label class="pick">Essayer avec ma photo<input type="file" id="photoInput" accept="image/jpeg,image/png,image/webp"></label>';
}
function render() {
  document.title =
    {
      files: "Mes fichiers",
      photos: "Photos",
      review: "Trier mes photos",
      trash: "Corbeille",
    }[page] + " · Maison";
  const v = $("#view");
  note("");
  document.querySelectorAll("nav button").forEach((b) => {
    if (b.dataset.view === page) b.setAttribute("aria-current", "page");
    else b.removeAttribute("aria-current");
  });
  $("#new").hidden = page !== "files";
  if (page === "files") {
    let trail = [];
    for (let n = file(current); n; n = file(n.parent)) trail.unshift(n);
    const path = [{ id: 0, name: "Mes fichiers" }, ...trail]
      .map((n, i) =>
        i === trail.length
          ? esc(n.name)
          : '<button data-dir="' + n.id + '">' + esc(n.name) + "</button>",
      )
      .join(" › ");
    const rows = files
      .filter((n) => !n.deleted && n.parent === current)
      .sort(
        (a, b) =>
          Number(b.dir) - Number(a.dir) || a.name.localeCompare(b.name, "fr"),
      );
    v.innerHTML =
      '<div class="crumb">' +
      path +
      "</div><h1>" +
      esc(file(current)?.name || "Mes fichiers") +
      '</h1><div class="row head"><span>Nom</span><span class="type">Modifié</span><span>Taille</span></div>' +
      rows
        .map(
          (n) =>
            '<div class="row"><button class="name" data-' +
            (n.dir ? "dir" : "info") +
            '="' +
            n.id +
            '"><span class="folder">' +
            svgIcon(n.dir ? "files" : "doc") +
            "</span>" +
            esc(n.name) +
            '</button><span class="type">' +
            "18 juil. 2025" +
            "</span><span>" +
            n.size +
            "</span></div>",
        )
        .join("") +
      (rows.length ? "" : '<p class="empty">Ce dossier est vide.</p>');
    return;
  }
  if (page === "trash") {
    const rows = [...files, ...pics].filter((i) => i.deleted);
    v.innerHTML =
      "<h1>Corbeille</h1>" +
      (rows.length
        ? rows
            .map(
              (n) =>
                "<p>" +
                esc(n.name) +
                '　<button data-restore="' +
                n.id +
                '">Restaurer</button></p>',
            )
            .join("")
        : '<p class="empty">La corbeille est vide.</p>');
    return;
  }
  const active = pics.filter((p) => !p.deleted);
  if (page === "photos") {
    v.innerHTML =
      '<h1>Photos</h1><h2>Juillet 2025</h2><div class="pair">' +
      active.map((p) => "<figure>" + photoTile(p) + "</figure>").join("") +
      "</div>" +
      loadControl();
    return;
  }
  v.innerHTML = "<h1>Trier mes photos</h1>";
  if (ignored || active.length < 2) {
    v.innerHTML +=
      '<p class="empty">Toutes les suggestions ont été examinées.</p>' +
      (ignored ? '<button id="again">Revoir la série</button>' : "");
    return;
  }
  v.innerHTML +=
    '<p>18 juillet 2025 · 2 clichés similaires</p><div class="pair">' +
    pics
      .map(
        (p, i) =>
          "<figure>" +
          photoTile(p) +
          "<figcaption>" +
          (i
            ? "<strong>Flou possible</strong><p>Contours moins nets</p>"
            : '<strong class="keep">À conserver</strong><p>Contours plus nets</p>') +
          '<label><input type="checkbox" value="' +
          p.id +
          '"> Sélectionner</label></figcaption></figure>',
      )
      .join("") +
    '</div><div class="actions"><button id="ignore">Ignorer</button><button class="primary" id="discard" disabled>Mettre à la corbeille</button></div>' +
    loadControl() +
    '<p class="hint">En démo, la seconde prise simule un flou. Votre photo reste dans cet onglet.</p>';
}
function openNew() {
  dialog(
    '<h2>Nouveau</h2><form id="create"><label>Nom du dossier<br><input name="nom" type="text" maxlength="100" required autofocus></label> <button class="primary">Créer</button></form><label class="pick">Importer des fichiers<input type="file" id="import" multiple></label>',
  );
}
document.addEventListener("click", (e) => {
  const b = e.target.closest("button");
  if (!b) return;
  const d = b.dataset;
  if (d.view) {
    page = d.view;
    render();
  } else if (d.dir !== undefined) {
    current = Number(d.dir);
    render();
  } else if (d.info) {
    const n = file(d.info);
    dialog(
      "<h2>" +
        esc(n.name) +
        "</h2><p>" +
        n.size +
        '</p><button data-delete="' +
        n.id +
        '">Mettre à la corbeille</button>',
    );
  } else if (d.zoom) {
    dialog(
      "<h2>" +
        esc(pics.find((p) => p.id === d.zoom).name) +
        '</h2><img class="' +
        (d.zoom === "p2" ? "soft" : "") +
        '" src="' +
        photo() +
        '" alt="Vue agrandie">',
    );
  } else if (d.delete) {
    (file(d.delete) || pics.find((p) => p.id === d.delete)).deleted = true;
    $("#modal").close();
    render();
    note("Élément placé dans la corbeille.");
  } else if (d.restore) {
    (file(d.restore) || pics.find((p) => p.id === d.restore)).deleted = false;
    ignored = false;
    render();
    note("Élément restauré.");
  } else if (b.id === "new") openNew();
  else if (b.id === "close") $("#modal").close();
  else if (b.id === "ignore" || b.id === "again") {
    ignored = b.id === "ignore";
    render();
  } else if (b.id === "discard") {
    const c = $("#view input:checked");
    if (c)
      dialog(
        "<h2>Mettre " +
          (c.value === "p1" ? "la prise 1" : "la prise 2") +
          ' à la corbeille ?</h2><p>Vous pourrez la restaurer dans la corbeille.</p><button class="primary" data-delete="' +
          c.value +
          '">Confirmer</button>',
      );
  }
});
document.addEventListener("submit", (e) => {
  if (e.target.id !== "create") return;
  e.preventDefault();
  const n = e.target.elements.nom.value.trim();
  if (!n) return;
  add(n, current, true);
  $("#modal").close();
  render();
  note("Dossier créé.");
});
document.addEventListener("change", (e) => {
  const el = e.target;
  if (el.type === "checkbox")
    $("#discard").disabled =
      document.querySelectorAll("#view input:checked").length !== 1;
  if (el.id === "import") {
    for (const f of el.files)
      add(
        f.name,
        current,
        false,
        Math.max(1, Math.round(f.size / 1024)) + " Ko",
      );
    $("#modal").close();
    render();
    note("Les noms des fichiers ont été ajoutés à la maquette.");
  }
  if (el.id === "photoInput" && el.files[0]) {
    const url = URL.createObjectURL(el.files[0]),
      img = new Image();
    img.onload = () => {
      if (photoURL) URL.revokeObjectURL(photoURL);
      photoURL = url;
      render();
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      note("Cette image ne peut pas être affichée.");
    };
    img.src = url;
  }
});
render();
