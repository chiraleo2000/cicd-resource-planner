## Kiro outputs

```
reports/cicd-analysis-report.md
reports/resource-tables.md
docs/diagrams/pipeline.mmd
.gitlab-ci.yml | .github/workflows/cicd.yml | Jenkinsfile
Dockerfile | docker-compose.yml
terraform/ | ansible/ | k8s/
```

Validate with yamllint, hadolint, `terraform validate`, and `python scripts/check_compliance.py plans/*.json`.
