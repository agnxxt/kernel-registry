# Kernel Learning Loop

Per assignment cycle:
1. Execute
2. Collect feedback
3. Introspect
4. Persist notes
5. Propose improvement
6. Policy/human gate
7. Apply (canary first)
8. Measure for regression

## Safety
- Critical policy changes require approval.
- Change frequency is rate-limited.
- Global rollout requires evidence threshold.
- Every improvement event is auditable.

## MLflow Integration
- Track kernel learning loop metrics in MLflow.
- Recommended experiment name: `kernel-learning-loop`.
- Backend store: Postgres.
- Artifact store: MinIO (`s3://mlflow`).
