from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse
import webbrowser

from .intake import normalize_row
from .people import PeopleStore


HR_ACTIONS: tuple[dict[str, str], ...] = (
    {"id": "new-person", "title": "Nuevo ingreso", "description": "Dar de alta a una persona y preparar su expediente.", "status": "available"},
    {"id": "people", "title": "Buscar persona", "description": "Encontrar y consultar a alguien del equipo.", "status": "available"},
    {"id": "vacations", "title": "Vacaciones y permisos", "description": "Revisar solicitudes, saldos y calendario.", "status": "planned"},
    {"id": "documents", "title": "Documentos", "description": "Detectar faltantes, vencimientos y renovaciones.", "status": "planned"},
    {"id": "recruiting", "title": "Reclutamiento", "description": "Vacantes, candidatos, entrevistas y seguimiento.", "status": "planned"},
    {"id": "incidents", "title": "Incidencias", "description": "Faltas, retardos, permisos e incapacidades.", "status": "planned"},
    {"id": "approvals", "title": "Aprobaciones", "description": "Ver sólo lo que requiere una decisión humana.", "status": "planned"},
    {"id": "reports", "title": "Reportes", "description": "Resumen de plantilla y calidad de datos.", "status": "available"},
)


def build_dashboard(store: PeopleStore) -> dict[str, Any]:
    people = store.list(limit=500)
    incomplete = 0
    active = 0
    for person in people:
        if str(person.get("status") or "").strip().lower() in {"active", "activo", "activa"}:
            active += 1
        required = ("full_name", "department", "position", "start_date", "status")
        if any(not str(person.get(field) or "").strip() for field in required):
            incomplete += 1

    return {
        "summary": {
            "people": len(people),
            "active": active,
            "incomplete_records": incomplete,
            "approvals_pending": 0,
        },
        "actions": list(HR_ACTIONS),
    }


def _html() -> str:
    return """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>JOSELYN</title>
<style>
:root{font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#151515;background:#f5f4f0}
*{box-sizing:border-box} body{margin:0}.shell{max-width:1180px;margin:auto;padding:32px 20px 64px}
header{display:flex;justify-content:space-between;gap:24px;align-items:flex-start;margin-bottom:28px}
.brand{font-weight:900;letter-spacing:.12em;font-size:14px}.hello{font-size:38px;line-height:1.05;margin:8px 0}.muted{color:#666}
.badge{background:#161616;color:white;padding:10px 14px;border-radius:999px;font-size:13px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}.metric,.action,.panel{background:white;border:1px solid #e5e2da;border-radius:20px;padding:18px;box-shadow:0 8px 24px rgba(0,0,0,.04)}
.metric b{font-size:32px;display:block;margin-top:8px}.actions{margin-top:28px}.action{cursor:pointer;text-align:left;min-height:145px;transition:.15s}
.action:hover{transform:translateY(-2px);box-shadow:0 12px 30px rgba(0,0,0,.08)}.action h3{margin:0 0 8px}.status{font-size:12px;margin-top:16px;display:inline-block;padding:6px 9px;border-radius:999px;background:#f1f1ee}.available{background:#e9f7ec}
.panel{margin-top:28px}.row{display:flex;gap:10px;flex-wrap:wrap}input,select,button{font:inherit;border-radius:12px;border:1px solid #d8d5ce;padding:11px 12px}input{flex:1;min-width:180px}button{background:#171717;color:#fff;border:none;cursor:pointer}.secondary{background:#eceae4;color:#171717}
.person{padding:12px 0;border-bottom:1px solid #eee}.person:last-child{border-bottom:0}.hidden{display:none}
form{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin-top:14px}form button{grid-column:1/-1}
@media(max-width:620px){.hello{font-size:31px}header{display:block}.badge{display:inline-block;margin-top:12px}}
</style>
</head>
<body><main class="shell">
<header><div><div class="brand">JOSELYN · RH</div><h1 class="hello">Buenos días, Joselin.</h1><div class="muted">¿Qué necesitas hacer hoy?</div></div><div class="badge">Modo dirección</div></header>
<section class="grid" id="metrics"></section>
<section class="actions"><h2>Acciones frecuentes</h2><div class="grid" id="actions"></div></section>
<section class="panel hidden" id="peoplePanel"><h2>Buscar persona</h2><div class="row"><input id="q" placeholder="Nombre, correo, área o puesto"><button onclick="searchPeople()">Buscar</button><button class="secondary" onclick="hidePanels()">Cerrar</button></div><div id="peopleResults"></div></section>
<section class="panel hidden" id="newPanel"><h2>Nuevo ingreso</h2><div class="muted">Captura lo indispensable. JOSELYN guarda la ficha en People Core.</div>
<form id="newForm">
<input name="employee_id" placeholder="ID empleado">
<input name="full_name" placeholder="Nombre completo" required>
<input name="email" placeholder="Correo">
<input name="phone" placeholder="Teléfono">
<input name="department" placeholder="Área / departamento">
<input name="position" placeholder="Puesto">
<input name="start_date" type="date">
<select name="status"><option value="activo">Activo</option><option value="proximo_ingreso">Próximo ingreso</option><option value="inactivo">Inactivo</option></select>
<button type="submit">Guardar persona</button>
</form><div id="newResult"></div></section>
</main>
<script>
const labels={people:"Personas",active:"Activas",incomplete_records:"Expedientes incompletos",approvals_pending:"Aprobaciones pendientes"};
function hidePanels(){document.querySelectorAll(".panel").forEach(x=>x.classList.add("hidden"))}
function openAction(id){
  hidePanels();
  if(id==="people"){document.getElementById("peoplePanel").classList.remove("hidden");searchPeople();return}
  if(id==="new-person"){document.getElementById("newPanel").classList.remove("hidden");return}
  if(id==="reports"){window.scrollTo({top:0,behavior:"smooth"});return}
  alert("Esta función ya está en el mapa de RH y será conectada al core en la siguiente etapa.");
}
async function load(){
 const d=await fetch("/api/dashboard").then(r=>r.json());
 document.getElementById("metrics").innerHTML=Object.entries(d.summary).map(([k,v])=>`<div class="metric"><span class="muted">${labels[k]||k}</span><b>${v}</b></div>`).join("");
 document.getElementById("actions").innerHTML=d.actions.map(a=>`<button class="action" onclick="openAction('${a.id}')"><h3>${a.title}</h3><div class="muted">${a.description}</div><span class="status ${a.status}">${a.status==="available"?"Disponible":"En ruta"}</span></button>`).join("");
}
async function searchPeople(){
 const q=document.getElementById("q").value||"";
 const rows=await fetch("/api/people?q="+encodeURIComponent(q)).then(r=>r.json());
 document.getElementById("peopleResults").innerHTML=rows.length?rows.map(p=>`<div class="person"><b>${p.full_name||"Sin nombre"}</b><div class="muted">${p.position||"Sin puesto"} · ${p.department||"Sin área"} · ${p.email||"Sin correo"}</div></div>`).join(""):"<p class='muted'>No encontré personas.</p>";
}
document.getElementById("newForm").addEventListener("submit",async e=>{
 e.preventDefault(); const payload=Object.fromEntries(new FormData(e.target).entries());
 const r=await fetch("/api/people",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
 const d=await r.json(); document.getElementById("newResult").innerHTML=r.ok?"<p><b>Listo.</b> Persona guardada en People Core.</p>":"<p>"+(d.error||"No se pudo guardar")+"</p>";
 if(r.ok){e.target.reset();load()}
});
load();
</script></body></html>"""


class JoselynHandler(BaseHTTPRequestHandler):
    db_path = "joselyn.db"

    def _send_json(self, payload: Any, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self) -> None:
        body = _html().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send_html()
            return
        if parsed.path == "/api/dashboard":
            with PeopleStore(self.db_path) as store:
                self._send_json(build_dashboard(store))
            return
        if parsed.path == "/api/people":
            query = parse_qs(parsed.query).get("q", [None])[0]
            with PeopleStore(self.db_path) as store:
                self._send_json(store.list(query=query, limit=100))
            return
        self._send_json({"error": "not found"}, 404)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/people":
            self._send_json({"error": "not found"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("payload must be an object")
            record = normalize_row(payload, source="joselyn-app", row_number=None)
            if record.identity_key() is None:
                raise ValueError("Se requiere ID de empleado o correo.")
            with PeopleStore(self.db_path) as store:
                state = store.upsert(record, source="joselyn-app")
                saved = store.get(record.identity_key())
            self._send_json({"state": state, "person": saved}, 201 if state == "created" else 200)
        except (ValueError, json.JSONDecodeError) as exc:
            self._send_json({"error": str(exc)}, 400)

    def log_message(self, format: str, *args: object) -> None:
        return


def serve_app(
    *,
    db_path: str | Path = "joselyn.db",
    host: str = "127.0.0.1",
    port: int = 8765,
    open_browser: bool = True,
) -> None:
    handler = type("ConfiguredJoselynHandler", (JoselynHandler,), {"db_path": str(db_path)})
    server = ThreadingHTTPServer((host, port), handler)
    url = f"http://{host}:{server.server_port}"
    print(f"JOSELYN App: {url}")
    print(f"People Core: {db_path}")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nJOSELYN App cerrada.")
    finally:
        server.server_close()
