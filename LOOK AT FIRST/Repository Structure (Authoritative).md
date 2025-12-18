aura\_orchestra/

│

├─ README.md

├─ .env.example

├─ docker-compose.yml

│

├─ docs/

│   ├─ architecture.md

│   ├─ roles.md

│   └─ lifecycle.md

│

├─ infra/

│   ├─ postgres/

│   │   ├─ init/

│   │   │   ├─ 001\_schema.sql

│   │   │   └─ 002\_indexes.sql

│   │   └─ README.md

│   │

│   └─ healthchecks/

│       └─ postgres.sh

│

├─ services/

│   ├─ manager/

│   │   ├─ Dockerfile

│   │   ├─ app/

│   │   │   └─ placeholder.py

│   │   └─ requirements.txt

│   │

│   ├─ worker/

│   │   ├─ Dockerfile

│   │   └─ app/

│   │       └─ placeholder.py

│   │

│   └─ auditor/

│       ├─ Dockerfile

│       └─ app/

│           └─ placeholder.py

│

└─ scripts/

&nbsp;   ├─ dev\_up.sh

&nbsp;   └─ dev\_down.sh





**This structure will not change later — everything else builds on it.**





