# Actions Pages deploy contract for Bondwise

**Ticket:** [WSm-77/bondwise#27](https://github.com/WSm-77/bondwise/issues/27) (map [#25](https://github.com/WSm-77/bondwise/issues/25))  
**Researched:** 2026-11-12  
**Scope:** GitHub Pages + Actions primary docs only. No workflow implemented on `main`. No PR.

## Verdict

Publish Bondwise as a **project site** at `https://wsm-77.github.io/bondwise/` by selecting **Settings → Pages → Source: GitHub Actions**, then shipping a workflow that: runs `pytest` → builds the static tree → `actions/upload-pages-artifact` → (on `main` only) `actions/deploy-pages` with `permissions: pages: write` + `id-token: write` and environment `github-pages`. Wire every asset URL to base path `/bondwise` (from `actions/configure-pages` output `base_path`). Repo is currently **private** and `has_pages: false`; Pages for this URL also needs the visibility/plan prerequisite below before Settings can stick.

## What I did

1. Read wayfinder ticket #27 and map #25 via `gh-axi`.
2. Read primary GitHub Docs (Pages publishing source, custom workflows, site types, environments, 404 troubleshooting, limits) and confirmed the custom-workflows page in Chrome via `chrome-devtools-axi`.
3. Read first-party action sources: `actions/starter-workflows` `pages/static.yml` + `pages/jekyll.yml`, `actions/deploy-pages` README, `actions/upload-pages-artifact` README, `actions/configure-pages` `action.yml`.
4. Inspected existing `.github/workflows/ci.yml` (pytest on `main` / PR) and repo metadata (`visibility: private`, `has_pages: false`, `default_branch: main`).

## Findings (answers to the ticket Question)

### 1. Site type and URL

| Fact | Source |
|------|--------|
| Project site default URL is `https://<owner>.github.io/<repositoryname>` | [What is GitHub Pages?](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages) |
| Locked destination `https://wsm-77.github.io/bondwise/` matches owner `WSm-77` + repo `bondwise` | Map #25; repo metadata |

Artifact root **is** the site root under that URL. Do **not** nest an extra `bondwise/` folder inside the uploaded artifact unless you intentionally want `/bondwise/bondwise/`.

### 2. Required `GITHUB_TOKEN` permissions

Official starter and `deploy-pages` both require:

```yaml
permissions:
  contents: read
  pages: write      # create Pages deployments
  id-token: write   # mint OIDC JWT so Pages can verify the workflow/ref
```

Sources: [starter `pages/static.yml`](https://raw.githubusercontent.com/actions/starter-workflows/main/pages/static.yml); [deploy-pages README — Security / OIDC](https://raw.githubusercontent.com/actions/deploy-pages/main/README.md); [Using custom workflows with GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

`pages: write` authorizes the deployment API call; `id-token: write` is required so OIDC claims (including branch/ref) can be validated against environment/branch protection. Deploy job may set these at job scope; workflow-level grant (as in starters) is the common pattern.

### 3. Workflow shape (build → test → upload → deploy)

GitHub’s documented custom-workflow flow ([Configuring a publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)):

1. Trigger on push to default branch (and optionally `workflow_dispatch`).
2. `actions/checkout`
3. Build static files if needed
4. `actions/upload-pages-artifact`
5. On default-branch push, `actions/deploy-pages` (skip for pull_request)

Bondwise adds a hard **pytest gate** before any Pages artifact is uploaded. Recommended job graph (do not ship in this research ticket):

| Job | `needs` | Role |
|-----|---------|------|
| `test` | — | Mirror current CI: `astral-sh/setup-uv` + `uv sync --extra dev && uv run pytest` (see `.github/workflows/ci.yml`) |
| `build` | `test` | `configure-pages` → assemble static site → `upload-pages-artifact` with `path:` = site output dir |
| `deploy` | `build` | `environment: github-pages` + `actions/deploy-pages`; **only** when `github.ref == 'refs/heads/main'` and event is `push` or `workflow_dispatch` |

Also from starters:

```yaml
concurrency:
  group: "pages"
  cancel-in-progress: false
```

Deploy job must `needs:` the job that uploaded the artifact ([custom workflows docs](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)). Default environment name: `github-pages`. Capture `url: ${{ steps.deployment.outputs.page_url }}`.

**Artifact contract** ([upload-pages-artifact README](https://raw.githubusercontent.com/actions/upload-pages-artifact/main/README.md); custom workflows docs):

- Prefer `actions/upload-pages-artifact` (packages correctly).
- Else: artifact named `github-pages`, single gzip-of-tar, &lt;10GB (official Pages site limit 1GB), no symlinks/hard links.
- Deployed artifact must include `index.html` (case-sensitive) at **artifact top level** ([Creating a GitHub Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site); [404 troubleshooting](https://docs.github.com/en/pages/getting-started-with-github-pages/troubleshooting-404-errors-for-github-pages-sites)).

**Action versions observed 2026-11-12** (prefer starter tags when shipping; docs examples lag):

| Action | Starter `static.yml` / `jekyll.yml` | Custom-workflows doc snippets |
|--------|-------------------------------------|-------------------------------|
| `actions/configure-pages` | `@v5` | `@v5` |
| `actions/upload-pages-artifact` | `@v3` | `@v4` |
| `actions/deploy-pages` | `@v5` | `@v4` |

Pin whatever majors are current at implementation time; re-check `actions/starter-workflows/pages/`.

**Relation to existing CI:** Keep pytest as a required predecessor of upload (same workflow `needs:`, or a reusable workflow called by both). Do not deploy from a job that can run after a failed test.

### 4. Base-href / asset path implications

`actions/configure-pages` outputs ([action.yml](https://raw.githubusercontent.com/actions/configure-pages/main/action.yml)):

| Output | Example for Bondwise |
|--------|----------------------|
| `base_url` | `https://wsm-77.github.io/bondwise` |
| `base_path` | `/bondwise` |
| `origin` | `https://wsm-77.github.io` |

Jekyll starter wires this explicitly: `jekyll build --baseurl "${{ steps.pages.outputs.base_path }}"` ([`pages/jekyll.yml`](https://raw.githubusercontent.com/actions/starter-workflows/main/pages/jekyll.yml)).

For a hand-written HTML/JS + Pyodide shell under `/bondwise/`:

- Root-absolute URLs (`/app.js`, `/assets/...`, `/pyodide/...`) resolve to `https://wsm-77.github.io/...` and **404** — they omit `/bondwise`.
- Use one of: relative URLs from the page; `<base href="${{ base_path }}/">` (trailing slash matters); or inject `base_path` / `base_url` at build time into script/CSS/fetch/import paths.
- Same prefix for Pyodide `indexURL`, worker scripts, WASM, and any client router.
- Local file:// or `python -m http.server` at `/` will not match production unless you serve under a `/bondwise` prefix or inject a different base for local.
- Map #25 still owns the exact static file tree; this ticket only locks the **URL prefix contract**: production base path is `/bondwise`.

### 5. One-time repo Settings (human clicks)

**A. Enable Actions as Pages source** ([Configuring a publishing source — Publishing with a custom GitHub Actions workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)):

1. Open `https://github.com/WSm-77/bondwise`
2. **Settings**
3. Sidebar **Pages** (under “Code, planning, and automation”)
4. **Build and deployment → Source** → select **GitHub Actions**
5. Optionally pick a suggested workflow template, or skip if a custom workflow will be added later

GitHub does not bind Settings to one workflow file; Settings links to the **most recent successful Pages deploy** run.

**B. Protect `github-pages` environment (recommended)**  
Same doc: templates use environment `github-pages`; if missing it is created on first run. Add a deployment protection rule so **only the default branch (`main`) can deploy**. Configure under **Settings → Environments → github-pages** (deployment branches / protection rules) — [Managing environments for deployment](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment). `deploy-pages` README also highly recommends protecting the environment when source is Actions.

**C. Visibility / plan prerequisite (blocking today)**  
Evidence from this worktree’s API check:

- `visibility: private`, `has_pages: false`
- `GET /repos/WSm-77/bondwise/pages` → HTTP 404 (Pages not configured)

Docs: on GitHub Free, the repository for a Pages site **must be public** ([Creating a GitHub Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)). Private Pages need a paid plan that allows it. Before or as part of enabling Pages, either make `bondwise` public or confirm the account plan supports private Pages. Custom domain remains out of scope (map #25).

### 6. What not to do in the follow-on implement ticket

- Do not use “Deploy from a branch” / `docs/` or `gh-pages` as the primary source — destination already locked to Actions artifact.
- Do not implement the workflow on default branch inside this research ticket (already honored).
- Soft “10 builds/hour” limit does **not** apply to custom Actions workflows ([GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)).

## Evidence index

| Evidence | How obtained |
|----------|----------------|
| Ticket Question | `gh-axi issue view 27 -R WSm-77/bondwise` |
| Map destination | `gh-axi` / `gh issue view 25` |
| Publishing source + Actions steps | docs.github.com …/configuring-a-publishing-source… (also opened in Chrome) |
| Permissions + job linkage | docs …/using-custom-workflows… + deploy-pages README |
| Starter workflow shape | raw `actions/starter-workflows` `pages/static.yml`, `pages/jekyll.yml` |
| `base_path` output | raw `actions/configure-pages` `action.yml` |
| Artifact format | upload-pages-artifact README + custom workflows doc |
| Existing pytest CI | `.github/workflows/ci.yml` lines 1–16 |
| Repo Pages off / private | `gh-axi api repos/WSm-77/bondwise` → `private: true`, `has_pages: false` |

## Recommendation (for later ship work)

1. Human: satisfy visibility/plan, then Settings → Pages → **GitHub Actions**; optionally lock `github-pages` env to `main`.
2. Implementer: add a Pages workflow (new file or extend CI) with `test → build (upload artifact) → deploy` as above; gate deploy to `main`; consume `steps.pages.outputs.base_path` when emitting the static shell.
3. Keep pure simulator in Python (ADR 0001); only the static adapter + Pyodide load paths need the base-href contract.
4. No captain product fork opened by this research: destination and gate (`pytest` then artifact deploy) were already locked on map #25.

## Deliverables

| Artifact | Location |
|----------|----------|
| This report | `/home/wiktor/firstmate/data/bondwise-pages-actions-research/report.md` |
| Same Markdown on throwaway branch | `research/actions-pages-bondwise` → `docs/research/actions-pages-bondwise.md` |
