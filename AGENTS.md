# AGENTS.md

This is a document repository, **not a software project**. It holds insurance policy PDFs and a client master spreadsheet. There is no code, no package manager, no build/test/lint tooling, and no CI.

## Contents

- `polizas/` — single-page insurance policy PDFs.
  - Naming convention: `Poliza_<TYPE>-2026-<NNNN>.pdf`
  - `<TYPE>` is one of `AIS`, `PCS`, `SPC`; `<NNNN>` is sequential per type.
  - Current range: AIS 0001–0005, PCS 0001–0009, SPC 0001–0006.
- `Maestro_Clientes.xlsx` — client master file at repository root.
- `.DS_Store` — macOS metadata; ignore it.

## Guidance for agents

- Do not run `npm install`, `pip install`, `make`, `pytest`, etc. Nothing is configured and those commands will fail.
- If adding a new policy PDF, put it in `polizas/` and follow the existing naming convention (`Poliza_<TYPE>-2026-<NNNN>.pdf`, one page). Do not invent new type prefixes without confirming with the team.
- No README, manifests, or instruction files exist beyond this one.
