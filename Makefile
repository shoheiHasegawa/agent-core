.PHONY: secrets-encrypt secrets-decrypt

# ---------------------------------------------------------
# Secrets Management (sops)
# ---------------------------------------------------------
# agent-core は、core-service をはじめとする各サービスへの
# 接続情報（APIキー等）を管理するオーケストレーターです。
# 本番環境およびローカル環境でのシークレット管理は sops を使用します。

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

validate-sdd:
	@echo "Validating SDD and architecture..."
	@uv run python tools/validate_sdd.py

validate-orphans:
	@echo "Auditing orphan scripts..."
	@uv run python tools/audit_orphan_scripts.py

check-all: validate-skills validate-sdd validate-orphans
	@echo "✅ All agent-core Quality Gates passed!"

