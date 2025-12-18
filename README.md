# Aura_Orchestra

**Aura_Orchestra** is a governed, auditable, production-grade AI orchestration system designed to transform product requirements into verified, testable, production-ready software.

## Core Principles
- **Director has absolute visibility**: All actions are logged and auditable
- **Manager controls all execution**: Central orchestration prevents chaos
- **Agents cannot self-assign work**: Strict task routing
- **Every action is logged**: 1-year retention for full traceability
- **Every failure is measurable**: Scoring and accountability
- **No silent overrides**: Governance is enforced, not suggested

## Architecture
```
Director → Manager → Employees (Models)
           ↓
    Auditor & HR enforce correctness and policy
```

## System Roles
| Role | Responsibility |
|------|---------------|
| **Director (Human)** | Final authority, policy override |
| **Manager (Orchestrator)** | Task decomposition, routing |
| **Employees (Models)** | Task execution (Ollama, OpenAI, Gemini) |
| **Accountant** | Scoring, promotion, penalties |
| **Auditor** | Evidence gathering, anomaly detection |
| **HR** | Rule enforcement, lifecycle control |

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Git
- (Optional) Ollama for local models

### Quick Start
1. **Clone and configure**:
   ```bash
   git clone https://github.com/Herman940306/Aura_Orchestra.git
   cd Aura_Orchestra
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start the system**:
   ```bash
   docker compose up -d
   ```

3. **Verify Postgres**:
   ```bash
   docker compose ps
   docker compose exec postgres psql -U aura_admin -d aura_orchestra -c "\dt"
   ```

4. **Access Manager API** (when implemented):
   ```
   http://localhost:8000
   ```

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

## Development

### Directory Structure
```
aura_orchestra/
├── db/migrations/          # Database schema
├── services/               # Microservices (manager, workers, etc.)
├── docs/                   # Documentation
├── docker-compose.yml      # Container orchestration
└── .env.example            # Configuration template
```

### Database Migrations
Migrations are automatically applied on Postgres container startup from `db/migrations/`.

## License
See `LICENSE` file for details.

## Contributing
This is a governed system. All changes must follow the established batch plan and governance rules.
