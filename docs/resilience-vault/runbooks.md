# Deterministic Triage Runbooks

Runbooks provide step-by-step guidance for SRE on-call engineers to restore service within the 30-minute fleet MTTR target.

---

## Runbook Catalog

### 1. [RB-LAKEHOUSE-001: Triaging Lakehouse Ingest Lag](file:///C:/Users/FreeF/projects/platform-resilience-fieldguide/runbooks/01-triage-lakehouse-ingest-lag.md)
* **Target Trigger**: Kafka consumer lag exceeding 50,000 messages.
* **Key Steps**:
  1. Inspect partition lag via PromQL: `topk(5, sum by (partition, topic) (kafka_consumergroup_lag{topic=~"lakehouse-.*"}))`
  2. Detect partition rebalance storms: `bin/kafka-consumer-groups.sh --describe`
  3. Validate MinIO/S3 ingest throughput and expand consumer deployment replicas.

### 2. [RB-COMPUTE-002: Recovering Stuck Spark Driver Pods](file:///C:/Users/FreeF/projects/platform-resilience-fieldguide/runbooks/02-recovering-stuck-spark-driver-pods.md)
* **Target Trigger**: Pods stuck in `Terminating` for > 10 minutes.
* **Key Steps**:
  1. Verify application status in Spark History Server API: `GET /api/v1/applications`
  2. Run `lease_pruner.py --namespace lakehouse-compute --check-only`
  3. Execute safe patch removing lingering finalizers: `kubectl patch pod <pod-name> -p '{"metadata":{"finalizers":[]}}'`

### 3. [RB-AIRGAP-003: Disconnected Registry Mirroring](file:///C:/Users/FreeF/projects/platform-resilience-fieldguide/runbooks/03-disconnected-registry-mirroring.md)
* **Target Trigger**: Image pull errors (`ImagePullBackOff`) in Ring 2 classified clusters.
* **Key Steps**:
  1. Export signed container images using `skopeo copy dir:/opt/airgap/images/`
  2. Verify Platform One Cosign signature with public key `/etc/pki/platform-one-pubkey.pem`
  3. Mirror into local Harbor registry and verify cryptographic SHA256 digest with `crane`.
