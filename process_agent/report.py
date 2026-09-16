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
        if record.assignees:
            lines.append(f"- **Assigné à** : {', '.join(record.assignees)}")
        lines.append(f"- **Sources** : {', '.join(record.sources)}")
        lines.append(f"- **Confiance** : {record.confidence:.0%}")
        if record.steps:
            lines.append("")
            lines.append("**Étapes :**")
            for i, step in enumerate(record.steps, start=1):
                lines.append(f"{i}. {step}")
        lines.append("")

    return "\n".join(lines)


def to_html(
    records: list[ProcessRecord],
    team_label: str = "Équipe",
    roster: list[str] | None = None,
) -> str:
    """Génère un tableau de bord HTML autonome (une page, sans dépendance externe).

    ``roster`` liste optionnellement des membres de l'équipe qui doivent être
    proposables dans les assignations même s'ils ne sont, pour l'instant,
    assignés à aucun processus. Le tableau de bord permet en plus d'ajouter
    manuellement de nouveaux processus et de gérer les assignations
    directement dans le navigateur (persisté en local via ``localStorage``).
    """
    full_roster = sorted(
        {*(roster or []), *(a for r in records for a in r.assignees)},
        key=lambda n: n.lower(),
    )

    def _embed(value) -> str:
        return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")

    return (
        _HTML_TEMPLATE.replace("__PROCESS_DATA__", _embed([r.to_dict() for r in records]))
        .replace("__ROSTER_DATA__", _embed(full_roster))
        .replace("__TEAM_LABEL__", team_label)
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

  .toolbar{
    display:flex; flex-wrap:wrap; gap:10px; align-items:center;
    margin-bottom:16px; position:sticky; top:env(safe-area-inset-top, 0px);
    background:var(--bg); padding-block:8px; z-index:5;
  }
  #search{
    flex:1 1 220px; min-width:0; padding:10px 14px; border-radius:10px;
    border:1px solid var(--line); background:var(--surface); color:var(--ink);
    font-size:0.92rem; font-family:inherit;
  }
  #search:focus{outline:2px solid var(--accent); outline-offset:1px;}
  #clear{
    border:none; background:none; color:var(--ink-dim); font-size:0.8rem; cursor:pointer;
    text-decoration:underline; padding:6px 2px; font-family:inherit;
  }
  #clear:hover{color:var(--ink);}

  .btn{
    border-radius:10px; padding:9px 16px; font-size:0.86rem; font-weight:500; cursor:pointer;
    font-family:inherit; border:1px solid transparent; transition:background .12s, border-color .12s, color .12s;
    white-space:nowrap;
  }
  .btn-primary{background:var(--accent); color:#fff; border-color:var(--accent);}
  .btn-primary:hover{background:var(--accent-strong); border-color:var(--accent-strong);}
  .btn-ghost{background:var(--surface); color:var(--ink); border-color:var(--line);}
  .btn-ghost:hover{border-color:var(--accent);}
  .btn:focus-visible{outline:2px solid var(--accent); outline-offset:1px;}

  .filter-row{display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-bottom:8px;}
  .filter-row:last-of-type{margin-bottom:18px;}
  .chipbar-label{
    font-size:0.72rem; color:var(--ink-dim); font-family:"IBM Plex Mono",monospace;
    text-transform:uppercase; letter-spacing:.04em; flex:none;
  }
  .chipbar{display:flex; flex-wrap:wrap; gap:6px;}
  .chip{
    border:1px solid var(--line); background:var(--surface); color:var(--ink-dim);
    border-radius:999px; padding:6px 12px; font-size:0.8rem; cursor:pointer;
    font-family:inherit; transition:background .12s, color .12s, border-color .12s;
  }
  .chip:hover{border-color:var(--accent);}
  .chip.active{background:var(--accent-soft); color:var(--accent-strong); border-color:var(--accent); font-weight:500;}
  .chip:focus-visible{outline:2px solid var(--accent); outline-offset:1px;}
  .chip.empty-hint{color:var(--ink-dim); border-style:dashed; cursor:default;}

  #count{font-size:0.85rem; color:var(--ink-dim); margin-bottom:14px;}
  #count strong{color:var(--ink); font-weight:600;}

  .panel{
    background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
    padding:20px; margin-bottom:22px; display:flex; flex-direction:column; gap:14px;
  }
  .panel h3{margin:0; font-size:1.02rem; font-weight:600;}
  .grid2{display:grid; grid-template-columns:repeat(auto-fit, minmax(200px,1fr)); gap:12px;}
  .field{display:flex; flex-direction:column; gap:5px;}
  .field label{
    font-size:0.72rem; color:var(--ink-dim); font-family:"IBM Plex Mono",monospace;
    text-transform:uppercase; letter-spacing:.03em;
  }
  .field input, .field textarea{
    padding:9px 12px; border-radius:8px; border:1px solid var(--line); background:var(--bg);
    color:var(--ink); font-family:inherit; font-size:0.88rem; resize:vertical;
  }
  .field input:focus, .field textarea:focus{outline:2px solid var(--accent); outline-offset:1px;}
  .checklist{
    display:flex; flex-wrap:wrap; gap:8px; padding:10px; border:1px solid var(--line);
    border-radius:10px; background:var(--bg);
  }
  .checklist label{
    display:flex; align-items:center; gap:6px; font-size:0.84rem; cursor:pointer;
    background:var(--surface); border:1px solid var(--line); border-radius:999px; padding:5px 10px 5px 8px;
  }
  .checklist input[type="checkbox"]{accent-color:var(--accent); width:14px; height:14px;}
  .add-member{display:flex; gap:8px; margin-top:8px;}
  .add-member input{flex:1; min-width:0;}
  .form-actions{display:flex; gap:10px; justify-content:flex-end;}

  .grid{display:grid; grid-template-columns:repeat(auto-fill, minmax(300px,1fr)); gap:14px;}
  .card{
    background:var(--surface); border:1px solid var(--line); border-radius:var(--radius);
    padding:18px; display:flex; flex-direction:column; gap:10px;
  }
  .card-head{display:flex; align-items:flex-start; justify-content:space-between; gap:10px;}
  .card-head h2{margin:0; font-size:1.08rem; font-weight:600; text-wrap:balance;}
  .card-head-actions{display:flex; align-items:center; gap:6px; flex:none;}
  .manual-badge{
    font-family:"IBM Plex Mono",monospace; font-size:0.64rem; text-transform:uppercase; letter-spacing:.04em;
    background:var(--amber-soft); color:var(--amber); border-radius:999px; padding:3px 8px; white-space:nowrap;
  }
  .icon-btn{
    border:none; background:none; color:var(--ink-dim); cursor:pointer; font-size:0.9rem;
    padding:2px 6px; line-height:1.6; border-radius:6px; font-family:inherit;
  }
  .icon-btn:hover{color:var(--rose); background:var(--rose-soft);}
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

  .assign-block{display:flex; flex-direction:column; gap:8px; border-top:1px dashed var(--line); padding-top:10px;}
  .assign-row{display:flex; flex-wrap:wrap; align-items:center; gap:6px;}
  .assign-label{
    font-family:"IBM Plex Mono",monospace; font-size:0.68rem; text-transform:uppercase;
    letter-spacing:.04em; color:var(--ink-dim); flex:none;
  }
  .person{
    display:inline-flex; align-items:center; gap:6px; background:var(--accent-soft); color:var(--accent-strong);
    border-radius:999px; padding:3px 10px 3px 4px; font-size:0.78rem; font-weight:500;
  }
  .person .avatar{
    width:18px; height:18px; border-radius:50%; background:var(--accent); color:#fff;
    display:flex; align-items:center; justify-content:center; font-size:0.6rem; font-weight:700;
    font-family:"IBM Plex Mono",monospace; flex:none;
  }
  .unassigned{color:var(--ink-dim); font-size:0.82rem; font-style:italic;}
  .assign-toggle{
    align-self:flex-start; border:none; background:none; color:var(--accent-strong); font-size:0.78rem;
    cursor:pointer; text-decoration:underline; padding:0; font-family:inherit;
  }
  .assign-toggle:hover{color:var(--accent);}
  .assign-editor{display:none; flex-direction:column; gap:8px;}
  .card.assign-open .assign-editor{display:flex;}

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
      <p>Extrait automatiquement des documents internes de l'équipe, complété à la main, et assigné aux membres qui les font tourner.</p>
    </div>
    <span class="badge-sample">Données d'exemple</span>
  </header>

  <div class="stats" id="stats"></div>

  <div class="toolbar">
    <input id="search" type="text" placeholder="Rechercher un processus, un outil, un responsable…" autocomplete="off">
    <button id="clear" type="button" hidden>Réinitialiser</button>
    <button id="newProcessBtn" class="btn btn-primary" type="button">+ Nouveau processus</button>
  </div>

  <div class="filter-row">
    <span class="chipbar-label">Responsable</span>
    <div class="chipbar" id="ownerChips"></div>
  </div>
  <div class="filter-row">
    <span class="chipbar-label">Assigné à</span>
    <div class="chipbar" id="memberChips"></div>
  </div>

  <form class="panel" id="newProcessPanel" hidden>
    <h3>Déclarer un processus manuellement</h3>
    <div class="grid2">
      <div class="field"><label for="mp-name">Nom *</label><input id="mp-name" required></div>
      <div class="field"><label for="mp-trigger">Déclencheur</label><input id="mp-trigger"></div>
      <div class="field"><label for="mp-freq">Fréquence</label><input id="mp-freq"></div>
      <div class="field"><label for="mp-tools">Outils (séparés par des virgules)</label><input id="mp-tools"></div>
    </div>
    <div class="field"><label for="mp-desc">Description</label><textarea id="mp-desc" rows="2"></textarea></div>
    <div class="field"><label for="mp-steps">Étapes (une par ligne)</label><textarea id="mp-steps" rows="3"></textarea></div>
    <div class="field">
      <label>Assigné à</label>
      <div class="checklist" id="mp-assignees"></div>
      <div class="add-member">
        <input id="mp-newmember" type="text" placeholder="Ajouter un nouveau membre…">
        <button type="button" class="btn btn-ghost" id="mp-addmember">Ajouter au registre</button>
      </div>
    </div>
    <div class="form-actions">
      <button type="button" class="btn btn-ghost" id="mp-cancel">Annuler</button>
      <button type="submit" class="btn btn-primary">Ajouter le processus</button>
    </div>
  </form>

  <p id="count"></p>
  <div class="grid" id="grid"></div>
  <div class="empty" id="empty" hidden>Aucun processus ne correspond à ce filtre.</div>

  <footer>Généré par le prototype d'agent d'identification de processus · les ajouts manuels et assignations sont conservés dans ce navigateur</footer>
</div>

<script>
(function(){
  var DATA = __PROCESS_DATA__;
  var ROSTER = __ROSTER_DATA__;
  var LS_MANUAL = "pa_manual_processes_v1";
  var LS_ASSIGN = "pa_assign_overrides_v1";
  var LS_ROSTER = "pa_roster_extra_v1";

  var state = { query: "", owner: null, member: null };
  var openSteps = new Set();
  var openAssign = new Set();

  function loadLS(key){
    try { var raw = localStorage.getItem(key); return raw ? JSON.parse(raw) : null; } catch (e) { return null; }
  }
  function saveLS(key, value){
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) {}
  }
  function loadManual(){ return loadLS(LS_MANUAL) || []; }
  function saveManual(list){ saveLS(LS_MANUAL, list); }
  function loadAssignOverrides(){ return loadLS(LS_ASSIGN) || {}; }
  function saveAssignOverride(uid, assignees){
    var overrides = loadAssignOverrides();
    overrides[uid] = assignees;
    saveLS(LS_ASSIGN, overrides);
  }
  function removeAssignOverride(uid){
    var overrides = loadAssignOverrides();
    delete overrides[uid];
    saveLS(LS_ASSIGN, overrides);
  }
  function loadRosterExtra(){ return loadLS(LS_ROSTER) || []; }
  function addRosterExtra(name){
    var extra = loadRosterExtra();
    if (extra.indexOf(name) === -1) { extra.push(name); saveLS(LS_ROSTER, extra); }
  }

  function keyOf(name){ return String(name || "").toLowerCase().trim().replace(/\s+/g, " "); }

  function confClass(c){ return c >= 0.75 ? "good" : c >= 0.5 ? "mid" : "low"; }

  function initials(name){
    var parts = String(name || "").trim().split(/\s+/).filter(Boolean);
    if (!parts.length) return "?";
    return (parts[0][0] + (parts[1] ? parts[1][0] : "")).toUpperCase();
  }

  function escapeHtml(s){
    return String(s || "").replace(/[&<>"']/g, function(ch){
      return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[ch];
    });
  }

  function combinedRecords(){
    var overrides = loadAssignOverrides();
    var base = DATA.map(function(p){
      var uid = "auto:" + keyOf(p.name);
      var rec = Object.assign({}, p);
      rec._uid = uid;
      rec._manual = false;
      rec.assignees = overrides.hasOwnProperty(uid) ? overrides[uid] : (p.assignees || []);
      return rec;
    });
    var manual = loadManual().map(function(p){
      var rec = Object.assign({}, p);
      rec._uid = p.id;
      rec._manual = true;
      rec.assignees = overrides.hasOwnProperty(p.id) ? overrides[p.id] : (p.assignees || []);
      return rec;
    });
    return base.concat(manual);
  }

  function fullRoster(){
    var set = new Set(ROSTER.concat(loadRosterExtra()));
    combinedRecords().forEach(function(p){ (p.assignees || []).forEach(function(a){ set.add(a); }); });
    return Array.from(set).filter(Boolean).sort(function(a, b){ return a.localeCompare(b, "fr"); });
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

  function renderOwnerChips(all){
    var owners = Array.from(new Set(all.map(function(p){ return p.owner; }).filter(Boolean)));
    var html = owners.map(function(o){
      var active = state.owner === o;
      return '<button class="chip' + (active ? ' active' : '') + '" data-owner="' + escapeHtml(o) + '">' + escapeHtml(o) + '</button>';
    }).join("");
    var el = document.getElementById("ownerChips");
    el.innerHTML = html || '<span class="chip empty-hint">Aucun responsable renseigné</span>';
    el.querySelectorAll(".chip[data-owner]").forEach(function(btn){
      btn.addEventListener("click", function(){
        var owner = btn.getAttribute("data-owner");
        state.owner = state.owner === owner ? null : owner;
        render();
      });
    });
  }

  function renderMemberChips(all){
    var members = Array.from(new Set(all.reduce(function(acc, p){ return acc.concat(p.assignees || []); }, [])));
    members.sort(function(a, b){ return a.localeCompare(b, "fr"); });
    var html = members.map(function(m){
      var active = state.member === m;
      return '<button class="chip' + (active ? ' active' : '') + '" data-member="' + escapeHtml(m) + '">' + escapeHtml(m) + '</button>';
    }).join("");
    var el = document.getElementById("memberChips");
    el.innerHTML = html || '<span class="chip empty-hint">Aucune assignation pour l\'instant</span>';
    el.querySelectorAll(".chip[data-member]").forEach(function(btn){
      btn.addEventListener("click", function(){
        var member = btn.getAttribute("data-member");
        state.member = state.member === member ? null : member;
        render();
      });
    });
  }

  function matches(p){
    var q = state.query.trim().toLowerCase();
    if (state.owner && p.owner !== state.owner) return false;
    if (state.member && (p.assignees || []).indexOf(state.member) === -1) return false;
    if (!q) return true;
    var haystack = [p.name, p.description, p.owner, p.trigger, (p.tools || []).join(" "), (p.assignees || []).join(" ")]
      .join(" ").toLowerCase();
    return haystack.indexOf(q) !== -1;
  }

  function personChip(name){
    return '<span class="person"><span class="avatar">' + escapeHtml(initials(name)) + '</span>' + escapeHtml(name) + '</span>';
  }

  function assignEditorHtml(p, roster){
    var checks = roster.map(function(name){
      var checked = (p.assignees || []).indexOf(name) !== -1;
      return '<label><input type="checkbox" data-uid="' + escapeHtml(p._uid) + '" data-name="' + escapeHtml(name) + '"' + (checked ? " checked" : "") + '>' + escapeHtml(name) + '</label>';
    }).join("");
    return (
      '<div class="checklist">' + (checks || '<span class="unassigned">Aucun membre au registre — ajoutez-en un.</span>') + '</div>' +
      '<div class="add-member">' +
        '<input type="text" class="new-assignee" placeholder="Ajouter un membre…" data-uid="' + escapeHtml(p._uid) + '">' +
        '<button type="button" class="btn btn-ghost add-assignee-btn" data-uid="' + escapeHtml(p._uid) + '">Ajouter</button>' +
      '</div>'
    );
  }

  function cardHtml(p, roster){
    var cls = confClass(p.confidence || 0);
    var tools = (p.tools || []).map(function(t){ return '<span class="tool">' + escapeHtml(t) + '</span>'; }).join("");
    var stepsHtml = (p.steps || []).map(function(s, i){
      return '<div class="step"><span class="n">' + (i + 1) + '</span><span class="t">' + escapeHtml(s) + '</span></div>';
    }).join("");
    var meta = [];
    if (p.trigger) meta.push('<span class="item"><span class="k">Déclencheur</span><span class="v">' + escapeHtml(p.trigger) + '</span></span>');
    if (p.owner) meta.push('<span class="item"><span class="k">Responsable</span><span class="v">' + escapeHtml(p.owner) + '</span></span>');
    if (p.frequency) meta.push('<span class="item"><span class="k">Fréquence</span><span class="v">' + escapeHtml(p.frequency) + '</span></span>');

    var isOpenSteps = openSteps.has(p._uid);
    var isOpenAssign = openAssign.has(p._uid);
    var assignees = p.assignees || [];

    return (
      '<article class="card' + (isOpenSteps ? " open" : "") + (isOpenAssign ? " assign-open" : "") + '" data-uid="' + escapeHtml(p._uid) + '">' +
        '<div class="card-head">' +
          '<h2>' + escapeHtml(p.name) + '</h2>' +
          (p._manual
            ? '<div class="card-head-actions"><span class="manual-badge">Manuel</span><button class="icon-btn delete-btn" type="button" data-uid="' + escapeHtml(p._uid) + '" aria-label="Supprimer ce processus">✕</button></div>'
            : "") +
        '</div>' +
        (p.description ? '<p class="desc">' + escapeHtml(p.description) + '</p>' : "") +
        '<div class="meta">' + meta.join("") + '</div>' +
        (tools ? '<div class="tools">' + tools + '</div>' : "") +
        '<div class="conf ' + cls + '"><span>Confiance</span><span class="bar"><span class="fill" style="width:' + Math.round((p.confidence || 0) * 100) + '%"></span></span><span class="pct">' + Math.round((p.confidence || 0) * 100) + '%</span></div>' +
        '<div class="assign-block">' +
          '<div class="assign-row"><span class="assign-label">Assigné à</span>' +
            (assignees.length ? assignees.map(personChip).join("") : '<span class="unassigned">Non assigné</span>') +
          '</div>' +
          '<button class="assign-toggle" type="button" data-uid="' + escapeHtml(p._uid) + '">' + (isOpenAssign ? "Fermer l'assignation" : "Gérer l'assignation") + '</button>' +
          '<div class="assign-editor">' + assignEditorHtml(p, roster) + '</div>' +
        '</div>' +
        (stepsHtml ? '<button class="toggle" type="button" data-uid="' + escapeHtml(p._uid) + '">Voir les étapes (' + (p.steps || []).length + ')</button>' : "") +
        (stepsHtml ? '<div class="steps">' + stepsHtml + '<div class="sources">Sources : <span>' + escapeHtml((p.sources || []).join(", ")) + '</span></div></div>' : "") +
      '</article>'
    );
  }

  function attachCardListeners(grid){
    grid.querySelectorAll(".toggle").forEach(function(btn){
      btn.addEventListener("click", function(){
        var uid = btn.getAttribute("data-uid");
        if (openSteps.has(uid)) openSteps.delete(uid); else openSteps.add(uid);
        render();
      });
    });
    grid.querySelectorAll(".assign-toggle").forEach(function(btn){
      btn.addEventListener("click", function(){
        var uid = btn.getAttribute("data-uid");
        if (openAssign.has(uid)) openAssign.delete(uid); else openAssign.add(uid);
        render();
      });
    });
    grid.querySelectorAll(".assign-editor input[type=checkbox]").forEach(function(cb){
      cb.addEventListener("change", function(){
        var uid = cb.getAttribute("data-uid");
        var card = cb.closest(".card");
        var checked = Array.from(card.querySelectorAll(".assign-editor input[type=checkbox]:checked"))
          .map(function(c){ return c.getAttribute("data-name"); });
        saveAssignOverride(uid, checked);
        render();
      });
    });
    grid.querySelectorAll(".add-assignee-btn").forEach(function(btn){
      btn.addEventListener("click", function(){
        var uid = btn.getAttribute("data-uid");
        var input = btn.parentElement.querySelector(".new-assignee");
        var name = input.value.trim();
        if (!name) return;
        addRosterExtra(name);
        var current = combinedRecords().find(function(r){ return r._uid === uid; });
        var assignees = (current ? current.assignees : []).slice();
        if (assignees.indexOf(name) === -1) assignees.push(name);
        saveAssignOverride(uid, assignees);
        render();
      });
    });
    grid.querySelectorAll(".delete-btn").forEach(function(btn){
      btn.addEventListener("click", function(){
        var uid = btn.getAttribute("data-uid");
        if (!window.confirm("Supprimer ce processus ajouté manuellement ?")) return;
        saveManual(loadManual().filter(function(p){ return p.id !== uid; }));
        removeAssignOverride(uid);
        openSteps.delete(uid);
        openAssign.delete(uid);
        render();
      });
    });
  }

  function render(){
    var all = combinedRecords();
    var filtered = all.filter(matches);
    var roster = fullRoster();

    renderStats(filtered);
    renderOwnerChips(all);
    renderMemberChips(all);

    document.getElementById("count").innerHTML = filtered.length === all.length
      ? "<strong>" + all.length + "</strong> processus au total"
      : "<strong>" + filtered.length + "</strong> sur " + all.length + " processus";
    document.getElementById("clear").hidden = !(state.query || state.owner || state.member);

    var grid = document.getElementById("grid");
    var empty = document.getElementById("empty");
    if (!filtered.length){
      grid.innerHTML = "";
      empty.hidden = false;
      return;
    }
    empty.hidden = true;
    grid.innerHTML = filtered.map(function(p){ return cardHtml(p, roster); }).join("");
    attachCardListeners(grid);
  }

  document.getElementById("search").addEventListener("input", function(e){
    state.query = e.target.value;
    render();
  });
  document.getElementById("clear").addEventListener("click", function(){
    state.query = ""; state.owner = null; state.member = null;
    document.getElementById("search").value = "";
    render();
  });

  var panel = document.getElementById("newProcessPanel");
  function populateAssigneeChecklist(){
    var roster = fullRoster();
    document.getElementById("mp-assignees").innerHTML = roster.length
      ? roster.map(function(name){
          return '<label><input type="checkbox" value="' + escapeHtml(name) + '">' + escapeHtml(name) + '</label>';
        }).join("")
      : '<span class="unassigned">Aucun membre au registre — ajoutez-en un ci-dessous.</span>';
  }
  document.getElementById("newProcessBtn").addEventListener("click", function(){
    panel.hidden = !panel.hidden;
    if (!panel.hidden){
      populateAssigneeChecklist();
      document.getElementById("mp-name").focus();
    }
  });
  document.getElementById("mp-cancel").addEventListener("click", function(){
    panel.reset();
    panel.hidden = true;
  });
  document.getElementById("mp-addmember").addEventListener("click", function(){
    var input = document.getElementById("mp-newmember");
    var name = input.value.trim();
    if (!name) return;
    addRosterExtra(name);
    var list = document.getElementById("mp-assignees");
    var label = document.createElement("label");
    var checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = name;
    checkbox.checked = true;
    label.appendChild(checkbox);
    label.appendChild(document.createTextNode(name));
    list.appendChild(label);
    input.value = "";
  });
  panel.addEventListener("submit", function(e){
    e.preventDefault();
    var nameInput = document.getElementById("mp-name");
    var name = nameInput.value.trim();
    if (!name){ nameInput.focus(); return; }

    var steps = document.getElementById("mp-steps").value.split("\n").map(function(s){ return s.trim(); }).filter(Boolean);
    var tools = document.getElementById("mp-tools").value.split(",").map(function(s){ return s.trim(); }).filter(Boolean);
    var assignees = Array.from(document.querySelectorAll("#mp-assignees input:checked")).map(function(cb){ return cb.value; });

    var record = {
      id: "manual:" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7),
      name: name,
      description: document.getElementById("mp-desc").value.trim(),
      trigger: document.getElementById("mp-trigger").value.trim(),
      frequency: document.getElementById("mp-freq").value.trim(),
      owner: "",
      tools: tools,
      steps: steps,
      assignees: assignees,
      confidence: 1.0,
      sources: ["Ajouté manuellement"]
    };

    var manual = loadManual();
    manual.push(record);
    saveManual(manual);

    panel.reset();
    panel.hidden = true;
    render();
  });

  render();
})();
</script>
"""
