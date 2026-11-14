# S1 environment / 环境

Checked on 2026-11-12. Exact machine output: `reports/evidence/environment-versions.json`.

| Component | Observed version and path | Decision |
|---|---|---|
| OS | Windows 11 Home, 10.0.26200, x64 | Native user-level tools |
| Base Python | 3.12.7, `D:\devtools\Anaconda3-CodeTou\python.exe` | Reused without changing Anaconda packages |
| Project Python | `.venv\Scripts\python.exe`, 3.12.7 | Isolated project dependencies |
| Git | 2.55.0.windows.5, `C:\Program Files\Git\cmd\git.exe` | Independent repository on `codex/s1-source-environment` |
| PostgreSQL | 17.12, `%LOCALAPPDATA%\PortfolioTools\postgresql-17.12\pgsql\bin` | Official EDB Windows binary archive |
| Database | `127.0.0.1:55432/energy`, role `energy_app` | SCRAM authentication; application role is not a superuser |
| Docker | Not on PATH; no Docker installation/service found in checked locations | Documented native PostgreSQL path |
| Packaging tools | pip 24.2, pip-tools 7.6.2, setuptools 84.2.1 | Hash-checked `requirements.lock`; pinned build backend |

`python` and `python3` on PATH initially resolved to Windows Store aliases. Use the explicit
project interpreter. No activation or system PATH change is required.
Windows aliases are not evidence of a working Python installation.

Selected application/test versions: FastAPI 0.162.5; SQLAlchemy 2.1.8; psycopg and
psycopg-binary 3.3.9; Alembic 1.20.1; httpx 0.28.1; pytest 9.2.0; Ruff 0.17.5;
python-dotenv 1.2.4; tzdata 2026.6. The lock records transitive dependencies and SHA-256 hashes.
Only the S1 paths are functionally verified; installing FastAPI/Alembic does not verify later tasks.

## PostgreSQL provenance and scope

- [PostgreSQL Windows downloads](https://www.postgresql.org/download/windows/)
  links to [EDB binary archives](https://www.enterprisedb.com/download-postgresql-binaries).
- Archive selected from EDB's 17.12 Windows x64 entry:
  `https://sbp.enterprisedb.com/getfile.jsp?fileid=1260667`.
- Downloaded archive size: 386263884 bytes.
- Locally calculated SHA-256:
  `a2cd8a774389347b70be7748ac4a37ef43cb6ee539c5fc3e85ae264b15e4a04c`.
  This records the downloaded artifact; no publisher checksum comparison is claimed.
- Project data and logs live under ignored `.local/`. No Windows service, firewall rule,
  BIOS setting, OS feature, global pip configuration or existing environment was changed.
- Only IPv4 loopback is configured. `.env` and the local admin password are ignored.
  `.env.example` contains no credentials.

## Commands / 命令

Run PowerShell from this repository root:

```powershell
& 'D:\devtools\Anaconda3-CodeTou\python.exe' -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --index-url https://pypi.org/simple --require-hashes -r requirements.lock
& .\.venv\Scripts\python.exe -m pip install --index-url https://pypi.org/simple --no-deps -e .
# First use only, after extracting the PostgreSQL binaries to the documented path:
& .\scripts\setup-local-db.ps1
# Subsequent sessions:
& .\scripts\start-local-db.ps1
& .\.venv\Scripts\python.exe -m pytest -v --tb=short
& .\.venv\Scripts\python.exe -m ruff check .
# Stop this project's instance when finished:
& .\scripts\stop-local-db.ps1
```

The setup script refuses to overwrite an existing cluster or `.env`. For an alternative
binary location pass `-PgBin 'absolute\path\to\pgsql\bin'` to the database scripts.
PowerShell scripts require the user's normal script execution policy; no persistent
policy change was made here.

## Reproduction boundary / 复现边界

A separate `.local/fresh-s1/` copy received a new venv, dependencies installed using
`--require-hashes`, a newly initialised PostgreSQL cluster on port 55433 and a separately
generated application password. Its six tests passed; the extra server was stopped.
The original Anaconda Python, this Windows OS and the downloaded PostgreSQL binaries
were reused. This is a fresh project environment, not a clean Windows machine or remote CI run.

## Embedded prerequisites inspected, not installed

The checked .NET installation is runtime 8.0.21 only, with no SDK. Renode, CMake,
host GCC and GNU Arm tools were not found on PATH. The full E1 platform/tool search
and supported .NET 10 setup remain NOT_STARTED. No embedded execution is claimed.

中文：先复用现有 Python，依赖只装到本项目虚拟环境。PostgreSQL 是真实本地进程；
端口为 55432，密码只保留在忽略文件中。第二个干净项目环境也实际验证了相同六项测试。
