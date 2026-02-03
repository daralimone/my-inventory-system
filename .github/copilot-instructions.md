# Copilot instructions for this repo

This repo is a small Streamlit-based inventory and sales demo that stores data in a local SQLite file (`business.db`). Below are the minimal, actionable notes an AI coding agent needs to be productive here.

## Big picture
- **Front-end:** [webapp.py](webapp.py#L1) is a Streamlit app that displays the `products` table and contains login logic (uses `extra_streamlit_components.CookieManager`).
- **Persistence:** All code reads/writes a single SQLite file `business.db` (created/initialized by `database_engine.py` and by `webapp.py`'s `init_db()` function).
- **Utility scripts:** `add_data.py`, `update_data.py`, `delete_data.py`, and `view_data.py` are small scripts that perform direct CRUD operations against `business.db`. Note: these scripts call example functions at file bottom (they execute when run/imported).
- **Data flow:** UI (Streamlit) -> direct SQLite reads/writes; there is no HTTP API or separate backend service.

## Project-specific conventions & gotchas
- The DB file `business.db` lives in the repo root and is accessed with `sqlite3.connect('business.db')` across modules.
- Several scripts contain sample calls at the bottom (e.g., `add_product(...)`) which execute on import. Avoid importing these modules from other code unless you expect those sample actions to run. Prefer invoking them via the CLI (e.g., `python add_data.py`). See [add_data.py](add_data.py#L1).
- `webapp.py` includes hardcoded credentials: username `daralim.one` and password `aSd.12345678` (search around the file to find them). Treat these as sensitive during edits and tests.
- `webapp.py` creates two DB tables: `products` and `sales_history`. Example table creation is in `init_db()`; see [webapp.py](webapp.py#L1-L40).

## Integration points & dependencies
- Python packages listed in [requirements.txt](requirements.txt#L1) must be installed: `streamlit`, `pandas`, `extra-streamlit-components`.
- To run UI locally: install requirements and run `streamlit run webapp.py` in the repo root.
- All cross-component communication is via the shared SQLite file; there are no external APIs.

## Common developer workflows (explicit commands)
- Install deps:

```bash
python -m pip install -r requirements.txt
```

- Run Streamlit UI:

```bash
streamlit run webapp.py
```

- Initialize or re-create DB (either):

```bash
python database_engine.py
# or simply open the Streamlit app; webapp.py calls init_db() on start
```

- Run a CRUD script directly (these scripts contain example calls):

```bash
python add_data.py
python update_data.py
python delete_data.py
python view_data.py
```

## Patterns & examples an AI should use
- When modifying DB logic, follow the existing `sqlite3` usage pattern: open connection, run parameterized SQL (`?` placeholders), `conn.commit()`, then `conn.close()`. Example: [update_data.py](update_data.py#L1-L30).
- For UI changes, follow Streamlit patterns already used in [webapp.py](webapp.py#L1): set page config, use `st.session_state` for login state, and use `pd.read_sql_query(...)` to populate dataframes.
- Cookie usage is done via `CookieManager` from `extra_streamlit_components`; login state is synchronized with a cookie named `is_logged_in` (see [webapp.py](webapp.py#L20-L60)).

## Safety and editing notes for AI agents
- Do NOT import `add_data.py`, `delete_data.py`, `update_data.py`, or `view_data.py` to inspect functions unless you want the example calls to execute. Instead, read the file text or refactor those scripts to wrap runnable examples in an `if __name__ == '__main__':` guard.
- Be careful changing credentials in `webapp.py`; they're hardcoded and used in tests/manual flows.
- The DB schema is minimal. If adding migrations, ensure existing data in `business.db` is preserved or document a destructive change.

## Where to look first when adding features
- UI changes: [webapp.py](webapp.py#L1)
- DB schema / initialization: [database_engine.py](database_engine.py#L1) and the `init_db()` in [webapp.py](webapp.py#L20-L40)
- CRUD examples and patterns: [add_data.py](add_data.py#L1), [update_data.py](update_data.py#L1), [delete_data.py](delete_data.py#L1)

---
If anything above is unclear or you'd like me to expand examples (e.g., refactor scripts to avoid side-effects on import, or to add a small test harness), tell me which sections to improve and I'll iterate.
