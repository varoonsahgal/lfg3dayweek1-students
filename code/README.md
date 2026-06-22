# TaskFlow Course Code

Runnable, classroom-friendly example, starter, and test files for the 3-day
**TaskFlow** backend course. Each module has up to three files:

- `module-0X-example.py` — clean reference implementation.
- `module-0X-starter.py` — intentionally incomplete/buggy code for the labs.
- `module-0X-tests.py` — a pytest suite (modules 03, 05, 06, 07).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install sqlalchemy flask pytest pytest-cov "psycopg[binary]"
```

| Dependency | Used by |
|---|---|
| `pytest`, `pytest-cov` | all test files; coverage in modules 03 & 07 |
| `sqlalchemy` | modules 04, 05, 06, 07 |
| `flask` | modules 06, 07 |
| `psycopg[binary]` | only the PostgreSQL `__main__` demos in modules 04 & 05 |

Modules 01–03 are pure standard library and need no installs to run. The
**Python Crash Lab bridge** files (`module-01.5-*`, `module-01.6-*`,
`module-01.7-*`) are also pure standard library — run them with plain `python`.

## Run the test suites (no PostgreSQL needed)

All test files use an in-memory SQLite database, so they pass without a running
database server. From this `code/` directory:

```bash
pytest -v                          # runs every *-tests.py suite
pytest code/module-06-tests.py -v  # or run one suite
```

`pytest.ini` configures discovery of the `*-tests.py` filenames and the
`importlib` import mode (needed because the filenames contain hyphens).

## Run the example apps

```bash
python module-01-example.py        # stdlib demo
python module-01.7-example.py       # stdlib demo: full TaskFlow triage report
python module-04-example.py        # needs PostgreSQL + DATABASE_URL
python module-06-example.py        # Flask dev server on http://127.0.0.1:5000
python module-07-example.py        # integrated service + capstone feature
```

The Flask apps default to a local SQLite file, so they run without PostgreSQL.
Set `DATABASE_URL` (e.g. `postgresql+psycopg://user:pass@localhost:5432/taskflow`)
to point at Postgres instead. Credentials belong in `.env`, never in source.
