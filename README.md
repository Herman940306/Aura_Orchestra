# Aura Orchestra: Multi-Agent Systems Orchestration & Operational Integrity

> *Drawing on a decade of experience as a Technical Supervisor, I built this platform to apply the same rigor required for Heavy Systems Oversight to AI-agentic workflows.*

**Aura Orchestra** is a self-governing, auditable, multi-model AI production platform designed to transform product requirements into verified, testable, production-ready software.

---

## Digital Workflow Supervision

Just as a Technical Supervisor assists artisans in solving complex mechanical problems, Aura Orchestra provides **Digital Workflow Supervision** for AI agents—ensuring every action is guided, validated, and traceable.

### Deterministic State Management

Mirroring **Standardized Mechanical Procedures** used in heavy systems oversight:
- Every state transition is explicit and logged
- No implicit mutations or hidden side effects
- Full audit trail for compliance and debugging
- Predictable, reproducible workflow execution

---

## HNSC: Hybrid Neuro-Symbolic Control

The **System Governor** that ensures AI agents operate within safe, auditable boundaries.

| Component | Function |
|-----------|----------|
| **Neural Layer** | LLM-powered reasoning and task decomposition |
| **Symbolic Layer** | Rule-based validation, policy enforcement |
| **Control Bridge** | Mediates between neural outputs and symbolic constraints |
| **Audit Core** | Immutable logging of all decisions and actions |

HNSC prevents:
- Unauthorized task execution
- Policy violations
- Unaudited state changes
- Agent self-assignment

---

## Core Principles

- **Director has absolute visibility**: All actions are logged and auditable
- **Manager controls all execution**: Central orchestration prevents chaos
- **Agents cannot self-assign work**: Strict task routing via HNSC
- **Every action is logged**: 1-year retention for full traceability
- **Every failure is measurable**: Scoring and accountability
- **No silent overrides**: Governance is enforced, not suggested

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    DIRECTOR (Human)                      │
│                   Final Authority                        │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                 HNSC SYSTEM GOVERNOR                     │
│    ┌──────────────┬──────────────┬──────────────┐       │
│    │ Neural Layer │ Control Bridge│ Symbolic Layer│      │
│    └──────────────┴──────────────┴──────────────┘       │
│                      Audit Core                          │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                    MANAGER                               │
│         Task Decomposition & Routing                     │
└───────┬─────────────┬─────────────┬─────────────────────┘
        │             │             │
   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
   │ Employee │   │ Employee │   │ Employee │
   │ (Ollama) │   │ (OpenAI) │   │ (Gemini) │
   └─────────┘   └─────────┘   └─────────┘
        │             │             │
   ┌────▼─────────────▼─────────────▼────┐
   │     AUDITOR & HR & ACCOUNTANT        │
   │  Evidence │ Policy │ Scoring         │
   └─────────────────────────────────────┘
```

---

## System Roles

| Role | Responsibility |
|------|---------------|
| **Director (Human)** | Final authority, policy override |
| **HNSC Governor** | Neuro-symbolic control, safe boundaries |
| **Manager (Orchestrator)** | Task decomposition, deterministic routing |
| **Employees (Models)** | Task execution (Ollama, OpenAI, Gemini) |
| **Accountant** | Scoring, promotion, penalties |
| **Auditor** | Evidence gathering, anomaly detection |
| **HR** | Rule enforcement, lifecycle control |

---

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Git
- (Optional) Ollama for local models

### Quick Start
```bash
git clone https://github.com/Herman940306/Aura_Orchestra.git
cd Aura_Orchestra
cp .env.example .env
# Edit .env with your configuration

docker compose up -d
```

### Verify Installation
```bash
docker compose ps
docker compose exec postgres psql -U aura_admin -d aura_orchestra -c "\dt"
```

### Access Manager API
```
http://localhost:8000
```

---

## Project Status

🚧 **Active Development** — Batch 1 Complete

### Completed
✅ Repository skeleton  
✅ Database schema  
✅ Environment configuration  
✅ Docker Compose foundation

### Roadmap
- **Batch 2**: Manager service (orchestration, job queue, leader election)
- **Batch 3**: MCP & Sandbox layer
- **Batch 4-6**: Multi-model adapters, routing, scoring
- **Batch 7-8**: Web UI, real-time streaming
- **Batch 9-12**: Production hardening, RBAC, backups

---

## Directory Structure

```
aura_orchestra/
├── db/migrations/          # Database schema
├── services/               # Microservices (manager, workers, etc.)
├── docs/                   # Documentation
├── docker-compose.yml      # Container orchestration
└── .env.example            # Configuration template
```

---

## License

See `LICENSE` file for details.

## Contributing

This is a governed system. All changes must follow the established batch plan and governance rules.
