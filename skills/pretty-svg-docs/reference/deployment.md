# DEPLOYMENT spec

How to stand this project up in a real environment and recover it when a deploy goes
wrong. Audience: operators and engineers deploying it, who may not have written it.
Like ARCHITECTURE this is **fabrication-prone** — a plausible deploy guide is worse
than none, because someone will follow it at 2am — so every environment, command,
variable, endpoint, workflow, and rollback step must be verifiable in the repo. Apply
[house-style.md](house-style.md) throughout.

## The deployability rule

**DEPLOYMENT is written only for a project that actually deploys somewhere.** It is
Tier 1, but signal-gated: the evidence pass decides whether it exists at all. Write it
when phase 1 finds at least one of:

- a hosting/platform config — `railway.toml`, `vercel.json`, `netlify.toml`,
  `fly.toml`, `app.yaml`, `Procfile`, `render.yaml`, `*.tfvars`
- container or orchestration artefacts — `Dockerfile`, `compose*.yml`, `k8s/`,
  Helm charts
- infrastructure as code — Terraform, Pulumi, CDK, CloudFormation, SAM
- a CI workflow that deploys, releases to an environment, or promotes a branch or tag
- database migrations **plus** a runtime service — deploy ordering exists to document
- an existing `DEPLOYMENT.md` or `docs/deploy*` — then this is an UPDATE, not a CREATE

**No signal → don't write the doc.** Report it in the phase 8 table as
`N/A — no deploy target` and leave publish/release mechanics where they already live,
in DEVELOPMENT and CONTRIBUTING. A library, a CLI published to a package registry, a
docs site with no build step, and a skill collection all correctly get no
DEPLOYMENT.md. Naming `deployment` explicitly as a target on a repo with no signal
asks **once** whether to write it anyway rather than inventing a deploy story.

Within the doc the same rule applies section by section. Never invent an environment
tier the repo doesn't have, a health endpoint no route serves, a rollback capability
the platform doesn't offer, or a secret the code never reads. Where the design intent
isn't recoverable, leave a `<!-- TODO -->` — an operator can act on a gap, not on a
confident fiction (house-style → Anti-fabrication).

## The DEVELOPMENT boundary

The two docs split on *where the code runs*, not on subject matter:

| Belongs in DEVELOPMENT | Belongs here |
| --- | --- |
| Local prerequisites, install, run, dev-server ports | Accounts, CLIs, and access needed to deploy |
| Local env vars and `.env` files | Deploy-time configuration per environment |
| Local build/seed/reset scripts | Provisioning, first deploy, promotion |
| Local troubleshooting (port in use, stale lockfile) | Deploy-time troubleshooting (failed migration, crash-loop, bad rollout) |
| How tests run | Health checks and post-deploy verification |

Cross-link rather than duplicate: this doc's intro points at DEVELOPMENT for getting
it running locally, and DEVELOPMENT carries a one-line pointer back. A variable that
matters in both places is documented once, here, with DEVELOPMENT noting the local
default.

Where a repo has exactly one environment, **say that plainly** — "there is one
environment; there is no staging" — instead of inventing a tier to fill the matrix.
A deliberate absence documented is worth more than a column of `n/a`.

## Section order

| Section | Required? | Drawn from |
| --- | --- | --- |
| Intro (what deploying this means, one line, link ARCHITECTURE; state the environment count) | required | manifest, configs |
| Prerequisites (accounts, CLIs, access) | required | platform configs, CI |
| Environment matrix (property × dev/staging/prod) | required | configs, CI, env files |
| Deploy-time configuration and env vars | required | code, `.env.example`, platform config |
| Secrets management | conditional — when any secret exists | CI secrets, platform vars |
| First deploy / provisioning | required | platform config, IaC |
| Database migration and pre-deploy ordering | conditional — when migrations exist | migration dir, CI |
| Promotion path (diagram + enforcement layers) | conditional — when >1 environment | branch protection, CI |
| Deployment checklist (pre-deploy / environment / security / data / post-deploy) | required | the above |
| Health checks and verification | conditional — when an endpoint or probe exists | routes, platform config |
| Scheduled jobs / background work | conditional | cron config, workers |
| Monitoring and alerting | conditional — link-out unless owned here | observability config |
| Deploy-time troubleshooting | conditional — when the platform has known failure modes | platform config, restart policy, logs |
| Rollback and recovery | required | platform capabilities, migrations |
| Supported versions / runtime floor | conditional | `engines`, `.nvmrc`, compose |
| Out of scope | conditional | the doc set |
| References | required | sibling docs |

## Section guidance

- **Environment matrix.** The single most reusable artefact in the doc, and usually
  the first thing an operator reads. One row per *property*, one column per
  environment: branch, substrate/host, public hostname, datastore, identity provider,
  health path, auto-deploy trigger, telemetry destination. Rows come from real config
  — a `railway.toml` healthcheck path, a workflow's `on.push.branches`, a compose
  service. Fewer, true rows beat a full grid with guesses in it.
- **Deploy-time configuration and env vars.** A table of `Variable` · `Required?` ·
  `Purpose`, restricted to variables the deployed code actually reads. Note which
  differ per environment and point at the matrix rather than repeating values.
- **Secrets management.** Name the store (CI secrets, platform variables, a vault) and
  the rotation expectation. **Never a real secret value** — names and purposes only,
  and never an example that looks like a live credential. If secrets are managed
  manually, say so; that is a finding an operator needs.
- **First deploy / provisioning.** The ordered steps that take an empty account to a
  serving instance: create the project/service, attach datastores, set variables,
  first deploy, first migration, verify. This is the section a reader follows
  literally, so every command must be real and every step must be in order.
- **Database migration and pre-deploy ordering.** State **this project's** ordering
  and give the reason. **Migrate first, then deploy** is the canonical invariant — an
  old application version never sees a new column missing, and a new version never
  sees the old schema — but it is not every project's, and asserting it where it isn't
  true is the most damaging sentence this document can contain. A schema step inside
  the container's start command, or a migration applied by hand, is a different model:
  describe the real one and name what enforces the order, or say plainly that nothing
  does. Say whether migrations are forward-only, and if they are, say what a
  "rollback" actually means (restore, or a compensating forward migration).
- **Promotion path.** The branch-and-environment flow plus a table of **enforcement
  layers** — for each: the layer, the file that implements it, and what it prevents.
  Branch protection, a CI guard workflow, and the documentation itself are three
  different layers; listing them separately is what makes the model auditable. Only
  list protection that exists — check it, don't assume it.
- **Deployment checklist.** Each item is an **assertion of desired state**, phrased so
  it can be confirmed, and cites the workflow, file, or endpoint that establishes it.
  "CI is green on the head commit (`ci.yml`)" is checkable; "make sure everything
  works" is not. Group into pre-deploy / environment / security / data / post-deploy;
  drop a group the project has nothing true to put in.
- **Health checks and verification.** The real path, the real expected status, and
  what a degraded-but-acceptable response looks like. If the platform is configured to
  probe it, say which config sets that.
- **Monitoring and alerting.** A link-out by default. Own it here only when this repo
  configures the dashboards and routes.
- **Deploy-time troubleshooting.** Only the failures that happen *because* it is
  deployed: a container that crash-loops, a schema step that fails at start, a health
  check that never goes green, a variable missing in the platform but present locally.
  Local failure modes stay in DEVELOPMENT. Each entry names the symptom, where the
  evidence is (which log, which panel), and the action.
- **Rollback and recovery.** Lead with a **decision table** — one column of failure
  class, one of `Roll back` vs `Fix forward` — before any runbook. Then the numbered
  runbooks for the paths that exist: traffic-cut/redeploy-previous, schema recovery,
  and restore-from-backup. Each step must be an action the operator can actually take
  on this platform.
- **Supported versions / runtime floor.** Major/LTS granularity from `engines`,
  `.nvmrc`, or the compose images — `Node 24 LTS`, not `24.13.0` (house-style → No
  volatile facts).
- **Out of scope.** Document deliberate absences rather than omitting them silently:
  no preview environments, no multi-region failover, no blue-green. A reader who can't
  find a section can't tell "missing" from "not applicable"; this section tells them.

## Visuals

Budget: **1–2 flagship animated SVG diagrams** for this doc. Where the project has
more than one environment, spend the first on the **promotion path** — branch →
environment, with the gates between them — because that is the model everything else
in the doc assumes. **On a single-environment project there is no promotion path to
draw**, and drawing one is exactly the fabrication this spec forbids; there the first
flagship goes to the **deploy ordering** instead. The remaining candidates, in order:
deploy/migration ordering (the pipeline from a green commit through the schema step to
a healthy container) and the **rollback decision path**. A deploy is genuinely a
sequence, which is why motion pays here; a diagram that wouldn't earn a place in a
printed operations runbook stays static.

Every animated DEPLOYMENT diagram is **immediately followed by a collapsed
`<details><summary>Diagram source (Mermaid)</summary>` block** holding the equivalent
Mermaid. It must parse (validate it — house-style → Diagrams) and it must **agree**
with the animation node for node. An operator reading with images off gets the
Mermaid; if the two disagree, the doc is wrong.

All remaining diagrams — the environment topology, a jobs schedule, a recovery
sequence — are **static SVG in the frozen design system** or **plain Mermaid**. Ground
every depicted environment, branch, gate, and endpoint in real config and record the
fact list in the visual's `viz.json`. Keep hostnames that rotate, versions, and dates
out of the rendered pixels (house-style → No volatile facts), and **never draw a
secret, token, or credential** into a visual.

Marker format and hash mechanics live in [embedding.md](embedding.md); production in
[viz-production.md](viz-production.md); styling in [design-system.md](design-system.md).
Don't restate those here.

## Neutral exemplar (shape only)

```markdown
# Deployment

How to deploy <project> to <environment(s)> and recover it if a deploy goes wrong. For
how the pieces fit together see [ARCHITECTURE.md](ARCHITECTURE.md); for running it
locally see [DEVELOPMENT.md](DEVELOPMENT.md).

## Prerequisites

- <account or platform access needed>
- <CLI and how it authenticates>

## Environments

| Property | <Staging> | <Production> |
| --- | --- | --- |
| Branch | `<branch>` | `<branch>` |
| Host | <substrate> | <substrate> |
| Public hostname | `<url>` | `<url>` |
| Datastore | <datastore> | <datastore> |
| Health path | `<path>` | `<path>` |
| Deploy trigger | <push / tag / manual> | <push / tag / manual> |

## Deploy-time configuration

| Variable | Required? | Purpose |
| --- | --- | --- |
| `<NAME>` | required | <what the deployed code does with it> |

Values differ per environment — see the matrix above. Secrets are held in
<store>; this file names them and never carries a value.

## Promotion path

<!-- pd:viz name="promotion-path" src=".prettydocs/src/promotion-path/" facts-hash="…" src-hash="…" -->
<div align="center">
<img src="docs/assets/promotion-path.svg" alt="<Promotion path: feature branches merge
to the integration branch which deploys to staging, and the release branch deploys to
production, with the gate on each step.>" width="820" />
</div>
<!-- pd:viz end -->

<details>
<summary>Diagram source (Mermaid)</summary>

​```mermaid
flowchart LR
  feat["<feature branches>"] -->|"<merge gate>"| stage["<integration branch>"]
  stage -->|"<promotion gate>"| main["<release branch>"]
  stage -.->|"<trigger>"| Staging["<staging environment>"]
  main -.->|"<trigger>"| Prod["<production environment>"]
​```

</details>

| Layer | File | What it prevents |
| --- | --- | --- |
| <branch protection> | `<path>` | <what it blocks> |
| <CI guard> | `<path>` | <what it blocks> |

## First deploy

​```bash
<create the service>
<set the variables>
<run migrations>
<deploy>
​```

## Migrations and ordering

The order is **migrate first, then deploy**. <Why, in one sentence, for this schema.>
<What enforces it, or that nothing does.>

## Deployment checklist

**Pre-deploy**

- [ ] <assertion of desired state> (`<workflow or file that establishes it>`)

**Post-deploy**

- [ ] `<health path>` returns `<status>`.
- [ ] <the first real signal that the new version is serving>

## Rollback and recovery

| Class | Action |
| --- | --- |
| <data corruption> | Roll back. |
| <single-component regression caught early> | Fix forward. |

### <Redeploy the previous version>

1. <step>
2. <verify step>

## Out of scope

- <deliberate absence — e.g. no preview environments>.
- <what lives elsewhere> → <link>.

## References

- [ARCHITECTURE.md](ARCHITECTURE.md) — system design.
- [DEVELOPMENT.md](DEVELOPMENT.md) — local setup and workflows.
- [SECURITY.md](SECURITY.md) — security posture and reporting.

<!-- pd:footer start -->
<!-- … shared footer … -->
<!-- pd:footer end -->
```
