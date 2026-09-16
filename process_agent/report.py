"""Génération d'un rapport lisible à partir des processus identifiés."""

from __future__ import annotations

import json

from .models import ProcessRecord


def to_json(records: list[ProcessRecord]) -> str:
    return json.dumps([r.to_dict() for r in records], ensure_ascii=False, indent=2)


def to_markdown(records: list[ProcessRecord]) -> str:
    lines = ["# Processus identifiés dans l'équipe", ""]

    if not records:
        lines.append("Aucun processus n'a été identifié dans les documents fournis.")
        return "\n".join(lines)

    lines.append(f"{len(records)} processus identifié(s).")
    lines.append("")
    lines.append("| Processus | Responsable | Déclencheur | Fréquence | Sources |")
    lines.append("|---|---|---|---|---|")
    for record in records:
        lines.append(
            "| {name} | {owner} | {trigger} | {frequency} | {sources} |".format(
                name=record.name,
                owner=record.owner or "—",
                trigger=record.trigger or "—",
                frequency=record.frequency or "—",
                sources=", ".join(record.sources) or "—",
            )
        )
    lines.append("")

    for record in records:
        lines.append(f"## {record.name}")
        if record.description:
            lines.append(record.description)
        lines.append("")
        if record.trigger:
            lines.append(f"- **Déclencheur** : {record.trigger}")
        if record.owner:
            lines.append(f"- **Responsable** : {record.owner}")
        if record.frequency:
            lines.append(f"- **Fréquence** : {record.frequency}")
        if record.tools:
            lines.append(f"- **Outils** : {', '.join(record.tools)}")
        lines.append(f"- **Sources** : {', '.join(record.sources)}")
        lines.append(f"- **Confiance** : {record.confidence:.0%}")
        if record.steps:
            lines.append("")
            lines.append("**Étapes :**")
            for i, step in enumerate(record.steps, start=1):
                lines.append(f"{i}. {step}")
        lines.append("")

    return "\n".join(lines)


def to_html(records: list[ProcessRecord], team_label: str = "Équipe") -> str:
    """Génère un tableau de bord HTML autonome (une page, sans dépendance externe)."""
    payload = json.dumps(
        [r.to_dict() for r in records], ensure_ascii=False
    ).replace("</", "<\\/")
    return _HTML_TEMPLATE.replace("__PROCESS_DATA__", payload).replace(
        "__TEAM_LABEL__", team_label
    )


_HTML_TEMPLATE = r"""<title>Registre des processus</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root{
    --bg:#F4F5F2; --surface:#FFFFFF; --surface-alt:#ECEFEA; --line:#DBDFD7;
    --ink:#1B2420; --ink-dim:#5B665F;
    --accent:#1E7A67; --accent-strong:#145C4E; --accent-soft:#E1F0EA;
    --amber:#A9720F; --amber-soft:#FAF0DC;
    --rose:#A6402C; --rose-soft:#F7E6E0;
    --radius:14px;
  }
  @media (prefers-color-scheme: dark){
    :root:not([data-theme="light"]){
      --bg:#10161A; --surface:#17211D; --surface-alt:#1E2A25; --line:#2B3A33;
      --ink:#EAF1EC; --ink-dim:#9BAFA5;
      --accent:#4FD3AE; --accent-strong:#8FE9CE; --accent-soft:#1B3B32;
      --amber:#E8B95B; --amber-soft:#3A2F14;
      --rose:#E38268; --rose-soft:#3A2018;
    }
  }
  :root[data-theme="dark"]{
    --bg:#10161A; --surface:#17211D; --surface-alt:#1E2A25; --line:#2B3A33;
    --ink:#EAF1EC; --ink-dim:#9BAFA5;
    --accent:#4FD3AE; --accent-strong:#8FE9CE; --accent-soft:#1B3B32;
    --amber:#E8B95B; --amber-soft:#3A2F14;
    --rose:#E38268; --rose-soft:#3A2018;
  }

  *{box-sizing:border-box;}
  body{
    margin:0; background:var(--bg); color:var(--ink);
    font-family:"IBM Plex Sans",system-ui,sans-serif;
    padding-inline:20px; padding-block:28px 60px;
  }
  .wrap{max-width:1080px; margin:0 auto;}
  .mono{font-family:"IBM Plex Mono",ui-monospace,monospace;}

  header.top{display:flex; flex-wrap:wrap; gap:16px 24px; align-items:flex-end; justify-content:space-between; margin-bottom:28px;}
  .title-block h1{
    margin:0 0 6px; font-size:1.9rem; font-weight:700; letter-spacing:-0.01em;
    text-wrap:balance;
  }
  .title-block p{margin:0; color:var(--ink-dim); font-size:0.95rem; max-width:52ch;}
  .badge-sample{
    display:inline-flex; align-items:center; gap:6px;
    background:var(--surface-alt); border:1px solid var(--line); color:var(--ink-dim);
    font-family:"IBM Plex Mono",monospace; font-size:0.72rem; letter-spacing:.04em;
    text-transform:uppercase; padding:5px 10px; border-radius:999px; white-space:nowrap;
  }
  .badge-sample::before{content:"●"; color:var(--amber); font-size:0.6rem;}

  .stats{
    display:grid; grid-template-columns:repeat(auto-fit, minmax(150px,1fr));
    gap:12px; margin-bottom:24px;
  }
  .stat{
    background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
    padding:14px 16px;
  }
  .stat .num{font-family:"IBM Plex Mono",monospace; font-size:1.7rem; font-weight:600; font-variant-numeric:tabular-nums; color:var(--accent-strong);}
  .stat .lbl{font-size:0.78rem; color:var(--ink-dim); margin-top:2px;}

  .controls{
    display:flex; flex-wrap:wrap; gap:10px; align-items:center;
    margin-bottom:20px; position:sticky; top:env(safe-area-inset-top, 0px);
    background:var(--bg); padding-block:8px; z-index:5;
  }
  #search{
    flex:1 1 220px; min-width:0; padding:10px 14px; border-radius:10px;
    border:1px solid var(--line); background:var(--surface); color:var(--ink);
    font-size:0.92rem; font-family:inherit;
  }
  #search:focus{outline:2px solid var(--accent); outline-offset:1px;}
  .chipbar{display:flex; flex-wrap:wrap; gap:6px;}
  .chip{
    border:1px solid var(--line); background:var(--surface); color:var(--ink-dim);
    border-radius:999px; padding:6px 12px; font-size:0.8rem; cursor:pointer;
    font-family:inherit; transition:background .12s, color .12s, border-color .12s;
  }
  .chip:hover{border-color:var(--accent);}
  .chip.active{background:var(--accent-soft); color:var(--accent-strong); border-color:var(--accent); font-weight:500;}
  .chip:focus-visible{outline:2px solid var(--accent); outline-offset:1px;}
  #clear{
    border:none; background:none; color:var(--ink-dim); font-size:0.8rem; cursor:pointer;
    text-decoration:underline; padding:6px 2px; font-family:inherit;
  }
  #clear:hover{color:var(--ink);}

  #count{font-size:0.85rem; color:var(--ink-dim); margin-bottom:14px;}
  #count strong{color:var(--ink); font-weight:600;}

  .grid{display:grid; grid-template-columns:repeat(auto-fill, minmax(300px,1fr)); gap:14px;}
  .card{
    background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
    padding:18px; display:flex; flex-direction:column; gap:10px;
  }
  .card h2{margin:0; font-size:1.08rem; font-weight:600; text-wrap:balance;}
  .card .desc{font-size:0.88rem; color:var(--ink-dim); margin:0; line-height:1.45;}

  .meta{display:flex; flex-wrap:wrap; gap:6px 14px; font-size:0.8rem; color:var(--ink-dim);}
  .meta .item{display:flex; gap:5px; align-items:baseline;}
  .meta .k{font-family:"IBM Plex Mono",monospace; font-size:0.68rem; text-transform:uppercase; letter-spacing:.04em; color:var(--ink-dim); opacity:.85;}
  .meta .v{color:var(--ink);}

  .tools{display:flex; flex-wrap:wrap; gap:6px;}
  .tool{
    background:var(--surface-alt); border:1px solid var(--line); color:var(--ink-dim);
    font-size:0.74rem; padding:3px 9px; border-radius:999px; font-family:"IBM Plex Mono",monospace;
  }

  .conf{display:flex; align-items:center; gap:8px; font-size:0.78rem; color:var(--ink-dim);}
  .conf .bar{flex:1; max-width:90px; height:6px; border-radius:4px; background:var(--surface-alt); overflow:hidden;}
  .conf .fill{height:100%; border-radius:4px;}
  .conf .pct{font-family:"IBM Plex Mono",monospace; font-variant-numeric:tabular-nums;}
  .conf.good .fill{background:var(--accent);}
  .conf.good .pct{color:var(--accent-strong);}
  .conf.mid .fill{background:var(--amber);}
  .conf.mid .pct{color:var(--amber);}
  .conf.low .fill{background:var(--rose);}
  .conf.low .pct{color:var(--rose);}

  .toggle{
    align-self:flex-start; border:none; background:none; color:var(--accent-strong);
    font-size:0.82rem; font-weight:500; cursor:pointer; padding:2px 0; font-family:inherit;
    display:flex; align-items:center; gap:5px;
  }
  .toggle::after{content:"→"; transition:transform .15s;}
  .card.open .toggle::after{transform:rotate(90deg);}
  .toggle:hover{text-decoration:underline;}

  .steps{display:none; flex-direction:column; gap:0; margin-top:2px; border-top:1px dashed var(--line); padding-top:12px;}
  .card.open .steps{display:flex;}
  .step{display:flex; gap:12px; padding-block:6px;}
  .step .n{
    font-family:"IBM Plex Mono",monospace; font-size:0.76rem; color:var(--accent-strong);
    background:var(--accent-soft); border-radius:50%; width:22px; height:22px; flex:none;
    display:flex; align-items:center; justify-content:center; font-weight:600;
  }
  .step .t{font-size:0.86rem; padding-top:2px; line-height:1.4;}
  .sources{font-size:0.76rem; color:var(--ink-dim); margin-top:4px;}
  .sources span{font-family:"IBM Plex Mono",monospace;}

  .empty{
    text-align:center; padding:60px 20px; color:var(--ink-dim);
    border:1px dashed var(--line); border-radius:var(--radius);
  }

  footer{margin-top:36px; font-size:0.78rem; color:var(--ink-dim); text-align:center;}
</style>

<div class="wrap">
  <header class="top">
    <div class="title-block">
      <h1>Registre des processus — __TEAM_LABEL__</h1>
      <p>Extrait automatiquement des documents internes de l'équipe (notes de workflow, post-mortems, documentation d'onboarding) par l'agent d'identification de processus.</p>
    </div>
    <span class="badge-sample">Données d'exemple</span>
  </header>

  <div class="stats" id="stats"></div>

  <div class="controls">
    <input id="search" type="text" placeholder="Rechercher un processus, un outil, un responsable…" autocomplete="off">
    <button id="clear" type="button" hidden>Réinitialiser</button>
  </div>
  <div class="chipbar" id="ownerChips"></div>

  <p id="count"></p>
  <div class="grid" id="grid"></div>
  <div class="empty" id="empty" hidden>Aucun processus ne correspond à ce filtre.</div>

  <footer>Généré par le prototype d'agent d'identification de processus · moteur heuristique local</footer>
</div>

<script>
(function(){
  var DATA = __PROCESS_DATA__;
  var state = { query: "", owner: null };

  function confClass(c){ return c >= 0.75 ? "good" : c >= 0.5 ? "mid" : "low"; }

  function escapeHtml(s){
    return String(s || "").replace(/[&<>"']/g, function(ch){
      return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[ch];
    });
  }

  function renderStats(list){
    var docs = new Set();
    var tools = new Set();
    list.forEach(function(p){
      (p.sources || []).forEach(function(s){ docs.add(s); });
      (p.tools || []).forEach(function(t){ tools.add(t); });
    });
    var avgConf = list.length
      ? list.reduce(function(a, p){ return a + (p.confidence || 0); }, 0) / list.length
      : 0;
    var stats = [
      { num: list.length, lbl: "Processus identifiés" },
      { num: docs.size, lbl: "Documents source" },
      { num: tools.size, lbl: "Outils distincts" },
      { num: Math.round(avgConf * 100) + "%", lbl: "Confiance moyenne" }
    ];
    document.getElementById("stats").innerHTML = stats.map(function(s){
      return '<div class="stat"><div class="num">' + s.num + '</div><div class="lbl">' + s.lbl + '</div></div>';
    }).join("");
  }

  function renderChips(){
    var owners = Array.from(new Set(DATA.map(function(p){ return p.owner; }).filter(Boolean)));
    var html = owners.map(function(o){
      var active = state.owner === o;
      return '<button class="chip' + (active ? ' active' : '') + '" data-owner="' + escapeHtml(o) + '">' + escapeHtml(o) + '</button>';
    }).join("");
    document.getElementById("ownerChips").innerHTML = html;
    document.querySelectorAll("#ownerChips .chip").forEach(function(btn){
      btn.addEventListener("click", function(){
        var owner = btn.getAttribute("data-owner");
        state.owner = state.owner === owner ? null : owner;
        render();
      });
    });
  }

  function matches(p){
    var q = state.query.trim().toLowerCase();
    if (state.owner && p.owner !== state.owner) return false;
    if (!q) return true;
    var haystack = [p.name, p.description, p.owner, p.trigger, (p.tools || []).join(" ")]
      .join(" ").toLowerCase();
    return haystack.indexOf(q) !== -1;
  }

  function cardHtml(p, idx){
    var cls = confClass(p.confidence || 0);
    var tools = (p.tools || []).map(function(t){ return '<span class="tool">' + escapeHtml(t) + '</span>'; }).join("");
    var steps = (p.steps || []).map(function(s, i){
      return '<div class="step"><span class="n">' + (i + 1) + '</span><span class="t">' + escapeHtml(s) + '</span></div>';
    }).join("");
    var meta = [];
    if (p.trigger) meta.push('<span class="item"><span class="k">Déclencheur</span><span class="v">' + escapeHtml(p.trigger) + '</span></span>');
    if (p.owner) meta.push('<span class="item"><span class="k">Responsable</span><span class="v">' + escapeHtml(p.owner) + '</span></span>');
    if (p.frequency) meta.push('<span class="item"><span class="k">Fréquence</span><span class="v">' + escapeHtml(p.frequency) + '</span></span>');

    return (
      '<article class="card" data-idx="' + idx + '">' +
        '<h2>' + escapeHtml(p.name) + '</h2>' +
        (p.description ? '<p class="desc">' + escapeHtml(p.description) + '</p>' : '') +
        '<div class="meta">' + meta.join("") + '</div>' +
        (tools ? '<div class="tools">' + tools + '</div>' : '') +
        '<div class="conf ' + cls + '"><span>Confiance</span><span class="bar"><span class="fill" style="width:' + Math.round((p.confidence || 0) * 100) + '%"></span></span><span class="pct">' + Math.round((p.confidence || 0) * 100) + '%</span></div>' +
        (steps ? '<button class="toggle" type="button">Voir les étapes (' + (p.steps || []).length + ')</button>' : '') +
        (steps ? '<div class="steps">' + steps + '<div class="sources">Sources : <span>' + escapeHtml((p.sources || []).join(", ")) + '</span></div></div>' : '') +
      '</article>'
    );
  }

  function render(){
    var filtered = DATA.filter(matches);
    renderStats(filtered);
    renderChips();
    document.getElementById("count").innerHTML = filtered.length === DATA.length
      ? '<strong>' + DATA.length + '</strong> processus au total'
      : '<strong>' + filtered.length + '</strong> sur ' + DATA.length + ' processus';
    document.getElementById("clear").hidden = !(state.query || state.owner);

    var grid = document.getElementById("grid");
    var empty = document.getElementById("empty");
    if (!filtered.length){
      grid.innerHTML = "";
      empty.hidden = false;
      return;
    }
    empty.hidden = true;
    grid.innerHTML = filtered.map(cardHtml).join("");
    grid.querySelectorAll(".toggle").forEach(function(btn){
      btn.addEventListener("click", function(){
        btn.closest(".card").classList.toggle("open");
      });
    });
  }

  document.getElementById("search").addEventListener("input", function(e){
    state.query = e.target.value;
    render();
  });
  document.getElementById("clear").addEventListener("click", function(){
    state.query = ""; state.owner = null;
    document.getElementById("search").value = "";
    render();
  });

  render();
})();
</script>
"""
