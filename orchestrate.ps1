# Aura_Orchestra – Single Bootstrap Orchestrator
# PowerShell 7+

$ErrorActionPreference = "Stop"

function Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "$ts | $msg"
}

Log "=== Aura_Orchestra Bootstrap START ==="

# ─────────────────────────────────────────────
# Batch 01 – Repo Structure
# ─────────────────────────────────────────────
Log "Batch 01 – Initializing repository structure"

$dirs = @(
    "docs",
    "db",
    "prompts",
    "ops",
    "services"
)

foreach ($d in $dirs) {
    if (-not (Test-Path $d)) {
        New-Item -ItemType Directory -Path $d | Out-Null
    }
}

".env.example" | ForEach-Object {
    if (-not (Test-Path $_)) {
        Set-Content $_ "# environment variables"
    }
}

# ─────────────────────────────────────────────
# Batch 02 – Postgres Schema
# ─────────────────────────────────────────────
Log "Batch 02 – Creating Postgres schema"

$schema = @"
CREATE TABLE IF NOT EXISTS project_state (
    id SERIAL PRIMARY KEY,
    phase TEXT NOT NULL,
    status TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    event TEXT NOT NULL,
    actor TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
"@

Set-Content "db/schema.sql" $schema

# ─────────────────────────────────────────────
# Batch 03 – Manager Meta‑Prompt
# ─────────────────────────────────────────────
Log "Batch 03 – Manager meta‑prompt"

$managerPrompt = @"
You are the Aura_Orchestra Manager Agent.

RULES:
- Follow IMPLEMENTATION_ROADMAP.md exactly
- Never skip tests
- Never generate mock-only code
- Update ops/project_state.yaml after EACH phase
- Ask for missing paths or secrets BEFORE implementation
- Enforce enterprise-level correctness

You coordinate sub-agents.
You do not write production code directly.
"@

Set-Content "prompts/manager_meta_prompt.md" $managerPrompt

# ─────────────────────────────────────────────
# Project State Initialization
# ─────────────────────────────────────────────
$state = @"
phase: bootstrap
status: complete
last_updated: $(Get-Date -Format o)
"@

Set-Content "ops/project_state.yaml" $state

Log "✅ Aura_Orchestra Bootstrap COMPLETE"
