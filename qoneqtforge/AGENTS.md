# Agent Rules

1. Follow QONEQTFORGE_MASTER_SPEC.md exactly. Structure in §4 is mandatory.
2. Only free services. Never add paid dependencies or require credit cards.
3. Every provider call: timeout, retry, fallback, logging. No bare requests.
4. Every stage: idempotent, writes outputs to data/jobs/<id>/, emits SSE events.
5. Type hints everywhere, Pydantic validation at boundaries, ruff-clean.
6. Write a test for every util + a compose smoke test. Run tests before saying "done".
7. Secrets only via .env. Never print keys.
8. After each phase: run it, show the output file/screenshot, fix errors, then commit.
9. Keep docs/DECISIONS.md updated. Small, meaningful commits (conventional commits).
10. If unsure, choose the simplest reliable option and note it. Never silently stub: mark TODOs explicitly.
