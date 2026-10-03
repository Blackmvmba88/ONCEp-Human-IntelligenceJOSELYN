# JOSELYN App — Executive HR surface

JOSELYN App is the non-technical surface for the person leading HR operations.

## Product rule

The app must speak in HR intentions, not implementation concepts.

Joselin should see actions such as:

- Nuevo ingreso
- Buscar persona
- Vacaciones y permisos
- Documentos
- Reclutamiento
- Incidencias
- Aprobaciones
- Reportes

She should not need to understand event buses, RBAC internals, SQLite, correlation IDs or CLI flags to operate the product.

## Same core, two surfaces

```text
                 PONCE / JOSELYN CORE
                        |
             +----------+----------+
             |                     |
        JOSELYN CLI           JOSELYN App
        technical              executive
```

Both surfaces use the same People Core and authorization boundaries. The app is not a separate source of truth.

## v0 vertical slice

Run:

```bash
joselyn app
```

Optional:

```bash
joselyn app --db joselyn.db --host 127.0.0.1 --port 8765 --no-browser
```

Implemented in this slice:

- executive dashboard
- HR action catalog
- People Core totals and incomplete-record signal
- people search
- new-person capture
- local browser UI
- no new runtime dependencies

Planned actions remain visible as the product map, but are labelled as not yet connected.

## Design boundary

Sensitive employment decisions are not automated by this surface. JOSELYN can prepare, explain and route work, while authorized humans make final decisions where required.
