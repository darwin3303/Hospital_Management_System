# Hospital Management System — Frontend

React + Vite + TypeScript + Ant Design, themed with your blue palette
(`#F0F9FF → #0284C7`). Talks to the FastAPI backend at `http://localhost:8000`.

## 1. Install

```powershell
cd hms-frontend
npm install
```

## 2. Run

Make sure the backend is running first (`uvicorn app.main:app --reload --port 8000`
in your backend folder), then:

```powershell
npm run dev
```

Open `http://localhost:5173`. Log in with any of the users you created via
Swagger (e.g. `admin` / your current admin password).

## What's implemented

Every role has a working, real (not placeholder) screen wired to your actual
API:

- **Admin** — overview dashboard (aggregate stats), users, departments,
  employees, doctors (combined creation + working hours), reports (tabs per
  report type)
- **Receptionist** — patient search/registration, appointment booking
- **Doctor** — queue of own scheduled appointments, document-visit drawer
  (creates the medical record), mark-completed action
- **Nurse** — read-only patient history search, no edit controls anywhere
  on the screen
- **Lab staff** — queue with inline collect-sample / enter-result /
  generate-report actions matching the state machine
- **Pharmacist** — inventory management, dispense queue
- **Accountant** — load-or-generate invoice by appointment ID, itemized line
  items, payment recording

## Theme system

`src/theme/tokens.ts` holds the raw palette (your five blues plus a neutral
and semantic scale). `src/theme/themeConfig.ts` maps those tokens into Ant
Design's `ConfigProvider` theme, so every AntD component (buttons, tables,
menus) picks up the palette automatically. `src/theme/statusColors.ts` maps
every status value used across the app (appointment, lab, invoice,
admission, prescription) to a consistent badge colour.

To change the palette: edit `tokens.ts` only. Everything else derives from it.

## Known limitations (given the scope of a first pass)

- No automated frontend tests yet (pairs with the backend's `pytest` suite —
  worth adding next)
- Bundle isn't code-split (fine for local/dev use; worth revisiting before
  any real deployment)
- Some secondary flows (medical record amendments, admissions/discharge UI,
  doctor availability editing after creation) don't have dedicated screens
  yet — the API calls exist in `src/api/`, just not yet wired to a page
- No client-side form validation beyond Ant Design's built-in `required`
  rules — matches the backend's Pydantic validation as the source of truth,
  but a production app would want richer inline feedback
