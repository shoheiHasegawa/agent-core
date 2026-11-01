.PHONY: secrets-encrypt secrets-decrypt ws-new ws-harvest ws-list validate-skills validate-orphans validate-cleanliness validate-links check-all

EPIC ?=
REPOS ?= core-service
ISSUE ?=

# ---------------------------------------------------------
# Workspace & Worktree Harness (方式A)
# ---------------------------------------------------------
ws-new:
	@if [ -z "$(EPIC)" ]; then echo "Usage: make ws-new EPIC=<name> [REPOS=core-service,agent-core] [ISSUE=123]"; exit 1; fi
	@uv run python tools/workspace_manager.py new --epic "$(EPIC)" --repos "$(REPOS)" $(if $(ISSUE),--issue "$(ISSUE)",)

ws-harvest:
	@if [ -z "$(EPIC)" ]; then echo "Usage: make ws-harvest EPIC=<name>"; exit 1; fi
	@uv run python tools/workspace_manager.py harvest --epic "$(EPIC)"

ws-list:
	@uv run python tools/workspace_manager.py list

# ---------------------------------------------------------
# Secrets Management (sops)
# ---------------------------------------------------------
secrets-encrypt:
	@echo "Encrypting secrets..."
	@sops --encrypt --in-place .env || echo "Failed to encrypt. Check if .sops.yaml is configured and .env exists."

secrets-decrypt:
	@echo "Decrypting secrets..."
	@sops --decrypt --in-place .env || echo "Failed to decrypt. Check if you have the correct PGP/AGE keys."

# ---------------------------------------------------------
# Quality Gate & Architecture Validation
# ---------------------------------------------------------
validate-skills:
	@echo "Auditing skills..."
	@uv run python tools/audit_skills.py

validate-orphans:
	@echo "Auditing orphan scripts..."
	@uv run python tools/audit_orphan_scripts.py

validate-cleanliness:
	@echo "Validating cleanliness..."
	@uv run python tools/verify_cleanliness.py

validate-links:
	@echo "Validating markdown links..."
	@uv run python tools/check_markdown_links.py

check-all: validate-skills validate-orphans validate-cleanliness validate-links
	@echo "✅ All agent-core Quality Gates passed!"
