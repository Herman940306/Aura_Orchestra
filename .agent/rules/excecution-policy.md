---
trigger: always_on
---

# infra/policies/policy.yaml
version: "1.0"
name: "Aura_Orchestra_Core_Policy"
description: >
  Governance, roles, and immutable rules for Aura_Orchestra.
  This file is authoritative for policy enforcement.
immutable_rules:
  - "Do not skip steps"
  - "Do not assume missing inputs"
  - "Do not hardcode secrets"
  - "Do not bypass governance"
  - "Do not proceed after failed tests"
  - "All work must be reproducible"
human_authority:
  director_required: true
  director_constraints:
    - "Director has absolute override"
    - "Director presence is required for production deploy"
roles:
  director:
    capabilities: ["override", "pause_org", "approve_merge", "purge_archive"]
  manager:
    capabilities: ["task_distribution", "execution_control", "assign_models"]
  accountant:
    capabilities: ["scoring", "ranking"]
  auditor:
    capabilities: ["log_review", "incident_flagging"]
  hr:
    capabilities: ["penalties", "promotion", "termination"]
  employee:
    capabilities: ["sandbox_execution_only"]
known_inputs:
  dev_machine:
    name: "Wolf-PC"
    os: ["Windows","WSL2","Ubuntu"]
    cpu: "i7-9700K"
    ram_gb: 16
    gpu: "GTX 1080 Ti"
  infra:
    db: "PostgreSQL"
    container_runtime: "Docker"
    max_model_containers: 3
  models_supported:
    - "ollama_local"
    - "openai_cloud"
    - "gemini_cloud"
    - "cli_adapters"
  project:
    name: "Aura_Orchestra"
    retention_days: 365
policy_enforcement:
  must_not_disable:
    - "hr"
    - "auditor"
    - "accountant"
  refusal_behavior:
    on_bypass_attempt: "refuse_and_log_and_alert_director"
  auditability:
    require_execution_snapshots: true
    snapshot_schema: "infra/policies/snapshot_schema.yaml"
secrets:
  storage_policy: "env_or_vault_only"
  do_not_commit: true
  redaction_required: true
# infra/policies/execution.yaml
version: "1.0"
name: "Aura_Orchestra_Execution_Policy"
description: "Batch execution flow, git, snapshot, testing and CI expectations."

batch_policy:
  order_enforced: true
  parallel_execution: false
  rollback_on_failure: true

per_batch_steps:
  - plan
  - implementation
  - unit_testing
  - integration_testing
  - security_checks
  - snapshot_creation
  - state_update
  - director_notification

plan_requirements:
  path: "docs/plans"
  required_fields:
    - scope
    - files_to_create
    - commands
    - test_plan
    - risk_assessment

git:
  branch_naming: "feat/batch<N>-short-description"
  commit_rules:
    atomic: true
    message_prefix_required: true
  pr_required: true
  merge_strategy: "no-ff"
  tag_strategy: "v0.x.y-batch<N>"

testing:
  unit_tests:
    framework: "pytest"
    required: true
  integration_tests:
    path: "tests/integration"
    naming: "test_batch<N>.sh"
    mandatory: true
  retries:
    max_retries: 2
    on_failure: "create_incident_and_pause"

snapshot:
  required: true
  locations:
    sandbox: "/sandbox/snapshots/"
  naming: "batch<N>-<timestamp>"
  include:
    - repo_commit_sha
    - docker_images_list
    - env_snapshot_file (with placeholders only)
    - test_logs

state_document:
  path: "docs/project_state.md"
  required_after_steps:
    - plan
    - implementation
    - testing
    - deployment
  template_path: "infra/policies/project_state_template.md"

ci:
  required_checks:
    - unit_tests
    - integration_tests
    - flake8_mypy
    - security_scan
  gating: "protect_main_branch_if_requested"

(Add complianr.yaml to this rule) CRITICAL

