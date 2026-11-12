# Pyodide packaging for Bondwise `simulate`

Research ticket: [WSm-77/bondwise#26](https://github.com/WSm-77/bondwise/issues/26) (map [#25](https://github.com/WSm-77/bondwise/issues/25)).

**Verdict:** No hard blocker. Ship a **stdlib-only** package tree (`__init__.py`, `params.py`, `simulator.py`) as one zip (or a `deps=False` pure wheel), load Pyodide from a **pinned jsDelivr** URL, `unpackArchive` into the Emscripten FS, `importlib.invalidate_caches()`, then `from bondwise import simulate`. Do **not** install project deps (`streamlit` / `matplotlib`) in the browser path. Pin **Pyodide `v314.0.7`** (Python 3.14.2) or any ≥0.27 release (Python ≥3.12). Latest desktop Firefox / Chromium / Safari meet Pyodide’s published floors.

---

## What was done

1. Read issue #26 / #25 and Bondwise sources: `src/bondwise/simulator.py`, `params.py`, `__init__.py`, `pyproject.toml`, ADR-0001.
2. Read Pyodide primary docs (stable): loading custom code, loading packages, accessing files, downloading/deploying, usage/browser support, FAQ, changelog/release notes.
3. Built a minimal `bondwise/` zip (3 modules) and the normal project wheel; smoked both under Node `pyodide@314.0.7` against host `simulate(10000, 5, 0.03, True)`.

---

## Bondwise seam (evidence)

| File | Role in browser path | Imports |
|------|----------------------|---------|
| `src/bondwise/params.py` | Offer constants + `ProductParams` | `dataclasses` only |
| `src/bondwise/simulator.py` | Pure `simulate` | `dataclasses`, `__future__`, `bondwise.params` |
| `src/bondwise/__init__.py` | Re-exports `simulate` | `bondwise.simulator` only |
| `src/bondwise/app.py` | Streamlit adapter | **exclude** |
| `src/bondwise/chart.py` | matplotlib adapter | **exclude** |

AST of the three keep files yields top-level imports: `__future__`, `bondwise`, `dataclasses` — no third-party runtime deps.

ADR-0001 already locks bond math in pure Python with thin UI adapters; Pages shell is another adapter, not a JS port of the math ([#25](https://github.com/WSm-77/bondwise/issues/25)).

`pyproject.toml` declares `requires-python = ">=3.12"` and runtime deps `matplotlib>=3.9`, `streamlit>=1.40`. Those deps apply to the desktop Streamlit product, **not** to the simulate seam.

---

## Minimal file / package set

### Runtime files to serve under Pages (Pyodide path)

Minimal archive contents (proven):

```
bondwise/__init__.py
bondwise/params.py
bondwise/simulator.py
```

Zip size in this lab: **3242 bytes** (`/tmp/bondwise-sim.zip`).

**Do not** put in the browser package tree:

- `app.py` (Streamlit)
- `chart.py` (matplotlib) — destination already requires a JS chart from simulator numbers (#25)

### Pyodide itself

Prefer CDN (official recommendation), not vendoring the full distribution:

- Pin: `https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.js` (or `.mjs`)
- Default `indexURL` becomes that directory when the script is loaded from the CDN ([JS API / deploying docs](https://pyodide.org/en/stable/usage/downloading-and-deploying.html))
- Core needs only the runtime + stdlib zip; **no** numpy/matplotlib/streamlit wheels

Contrast (non-goal): **stlite** embeds Streamlit-in-browser. Destination retires Streamlit as product UI; stlite would fight the locked architecture.

---

## Recommended mount / load pattern

Pyodide’s documented best practice for multi-file custom code ([Loading custom Python code](https://pyodide.org/en/stable/usage/loading-custom-python-code.html), [Accessing files](https://pyodide.org/en/stable/usage/accessing-files.html)):

1. Create a package
2. Load it into the Emscripten VFS (prefer **one archive**, not per-file fetches)
3. `pyimport` / `from bondwise import simulate`
4. Call from JS; convert results for the chart UI

### Preferred (minimal, no micropip)

```js
const pyodide = await loadPyodide(); // script src = pinned CDN pyodide.js
const zip = await (await fetch(new URL("pkg/bondwise-sim.zip", document.baseURI))).arrayBuffer();
pyodide.unpackArchive(zip, "zip");
pyodide.runPython("import importlib; importlib.invalidate_caches()");
const simulate = pyodide.pyimport("bondwise").simulate;
// call simulate(...); map dataclasses → plain JS/JSON for charts
```

FAQ note: after writing new `.py` files into the FS, call `importlib.invalidate_caches()` before import ([FAQ](https://pyodide.org/en/stable/usage/faq.html)).

### Acceptable alternative: pure wheel + micropip **with `deps=False`**

Full `uv build --wheel` today produces `bondwise-0.1.0-py3-none-any.whl` that:

- Includes `app.py` and `chart.py` (dead weight / footgun if imported)
- Declares `Requires-Dist: matplotlib`, `streamlit`

Evidence:

- `micropip.install(wheel)` **without** `deps=False` → fails resolving Streamlit’s `watchdog` (no pure Python wheel):  
  `ValueError: Can't find a pure Python 3 wheel for: 'watchdog<8,>=2.1.5; ...'`
- `await micropip.install("emfs:/…/bondwise-0.1.0-py3-none-any.whl", deps=False)` → succeeds and runs `simulate`

So: if CI builds a wheel for Pages, either strip adapters + drop deps in a Pages-only build, or always `deps=False`. The **zip of three files** stays simpler and matches the docs’ archive guidance without needing micropip at all.

### JS ↔ Python results

`simulate` returns nested frozen dataclasses (`SimulationResult` → `ProductPath` → `YearPoint` / `ExitSnapshot`). Treat conversion to chart-ready JS (dict/JSON) as shell work; not a packaging blocker. Prefer a thin Python helper that returns plain dicts if interop gets noisy.

---

## `/bondwise/` base-path caveats

Project Pages URL: `https://wsm-77.github.io/bondwise/` (#25).

| Risk | Mitigation |
|------|------------|
| Root-absolute paths (`/pkg/...`, `/assets/...`) resolve to `github.io`, **not** `/bondwise/` | Use paths under `/bondwise/…`, or relative URLs resolved from `document.baseURI` / `<base href="/bondwise/">` |
| `fetch("pkg/bondwise-sim.zip")` depends on the HTML URL | Prefer `new URL("pkg/bondwise-sim.zip", document.baseURI)` so both `/bondwise/` and `/bondwise/index.html` work |
| Pyodide `indexURL` | Keep Pyodide on **absolute jsDelivr**; do not make `indexURL` relative to the project site unless you vendor the full matching build under `/bondwise/…` and point `indexURL` there |
| Same-origin package zip | Serving the zip from the Pages artifact avoids CORS; remote wheels need CORS ([Loading packages](https://pyodide.org/en/stable/usage/loading-packages.html)) |
| MIME / WASM | GitHub Pages is explicitly listed as a viable static host for Pyodide ([Downloading and deploying](https://pyodide.org/en/stable/usage/downloading-and-deploying.html)); CDN `.wasm` already has correct CORS/`cross-origin` headers in practice |

---

## Hard blockers and version pins

### Hard blockers

**None** for the locked destination (pure `simulate` under Pyodide, no Streamlit/matplotlib in browser, no JS bond math).

Soft traps (implementation, not research blockers):

1. Installing the **full project wheel with dependency resolution** pulls Streamlit → fails (watchdog; also matplotlib is the wrong stack for this UI).
2. Importing `bondwise.chart` / `bondwise.app` in the browser path.
3. CSP without `wasm-unsafe-eval` (and historically Safari needing `unsafe-eval` for WASM) — only matters if Pages/custom headers tighten CSP later ([changelog note](https://pyodide.org/en/latest/project/changelog.html)).
4. Main-thread jank on large horizons — optional Web Worker later ([Using Pyodide](https://pyodide.org/en/stable/usage/index.html)); not required for correctness.

### Version pins (recommend)

| Component | Pin | Why |
|-----------|-----|-----|
| Pyodide CDN | **`v314.0.7`** | Current stable docs / jsDelivr “latest release”; `pyodide-lock.json` reports `python: 3.14.2` |
| Fallback if wanting CPython 3.12 ABI closer to local `uv` | `v0.27.7` (Python 3.12.7 per 0.27 changelog) | Still satisfies `requires-python >=3.12` |
| Also fine | `v0.28.x` (Python 3.13.2) | Same reason |
| Browsers | Latest desktop Firefox + Chromium + Safari | Pyodide tests floors: Firefox 112+, Chrome 112+, Safari 16.4+ ([Using Pyodide](https://pyodide.org/en/stable/usage/index.html)) — latest desktop exceeds these |
| Bondwise browser package | The three files above only | Stdlib-only; no pin of matplotlib/streamlit |

Avoid floating `cdn.jsdelivr.net/pyodide/dev/full/` (no browser caching; for testing only).

---

## Lab evidence (commands / outputs)

### Import graph

```text
top-level imports: ['__future__', 'bondwise', 'dataclasses']
```

### Minimal zip

```text
bondwise/__init__.py
bondwise/params.py
bondwise/simulator.py
# zip 3242 bytes
```

### Host reference

```text
HOST {'coi_final': 11810.97, 'edo_final': 12029.34, 'delta': 218.37, 'coi_years': 5, 'edo_years': 5}
```

(`PYTHONPATH=src python3` → `simulate(10000, 5, 0.03, True)`.)

### Pyodide zip unpack (Node `pyodide@314.0.7`)

```text
loaded 3.14.2
SUMMARY {"coi_final":11810.97,"edo_final":12029.34,"delta":218.37,"coi_years":5,"edo_years":5}
```

(`Uint8Array` required for `unpackArchive` under Node; browsers’ `arrayBuffer()` is fine.)

### Full wheel + micropip

```text
# deps=True (default): fails
ValueError: Can't find a pure Python 3 wheel for: 'watchdog<8,>=2.1.5; platform_system != "Darwin"'

# deps=False:
WHEEL_OK 11810.97 12029.34 218.37
```

Wheel listing includes `app.py` / `chart.py` and METADATA `Requires-Dist: matplotlib`, `streamlit`.

---

## Recommendation for later implement tickets (#25 map)

1. Build Pages artifact with static shell + `pkg/bondwise-sim.zip` (three files only).
2. Load pinned `https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.js`.
3. `fetch` zip via `document.baseURI`-aware URL → `unpackArchive` → invalidate caches → `simulate`.
4. Never call `micropip.install("bondwise")` against the Streamlit-era project metadata without `deps=False` / a Pages-only package.
5. Keep charting in JS; keep `app.py` / `chart.py` out of the browser tree.
6. No new ADR required solely for packaging; ADR-0001 already owns the pure-Python seam. A short “static shell + Pyodide adapter” note can wait for the shell ticket if desired.

**Out of scope here (per brief):** static shell implementation, Actions workflow, edits to `main`.

---

## Sources

- https://pyodide.org/en/stable/usage/loading-custom-python-code.html
- https://pyodide.org/en/stable/usage/loading-packages.html
- https://pyodide.org/en/stable/usage/accessing-files.html
- https://pyodide.org/en/stable/usage/downloading-and-deploying.html
- https://pyodide.org/en/stable/usage/index.html (browser support table)
- https://pyodide.org/en/stable/usage/faq.html
- https://pyodide.org/en/stable/usage/quickstart.html
- https://pyodide.org/en/0.27.0/project/changelog.html (Python 3.12.7)
- https://pyodide.org/en/0.28.0/project/changelog.html (Python 3.13.2; Safari iPad fix)
- https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide-lock.json (`python: 3.14.2`)
- Bondwise: `src/bondwise/{params,simulator,__init__}.py`, `pyproject.toml`, `docs/adr/0001-pure-simulator-seam.md`
- Issues: https://github.com/WSm-77/bondwise/issues/26 , https://github.com/WSm-77/bondwise/issues/25
