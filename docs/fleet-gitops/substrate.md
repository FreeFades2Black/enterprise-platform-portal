# Lakehouse Substrate Specs

The core data plane installed across the fleet is defined in the Helm chart `helm/lakehouse-substrate`. It coordinates three primary engines:

---

## Substrate Components

### 1. Strimzi Kafka Cluster (KRaft Mode)
* **Zero Zookeeper Dependencies**: Utilizes native Kafka Raft (KRaft) metadata quorum for reduced operational surface area.
* **Persistent Storage**: Individual 250Gi volumes mounted with Ceph RBD or AWS EBS gp3 via `WaitForFirstConsumer` binding.
* **Mutual TLS (mTLS)**: End-to-end cryptographic encryption between producers, brokers, and consumers.

### 2. Trino 435 Distributed Query Engine
* **Memory Pool Architecture**: 75% heap reserved for query execution, 25% reserved for native off-heap netty buffers and metaspace.
* **Local NVMe Spill Mounts**: Dedicated hostPath `/mnt/nvme-spill` attached to Trino worker StatefulSets, reducing query spill latencies by 230x ([ADR 0001](file:///C:/Users/FreeF/projects/platform-resilience-fieldguide/docs/adr/0001-nvme-spill-mounts-for-trino.md)).

### 3. Project Nessie & Apache Iceberg REST Catalog
* **ACID Transaction Isolation**: Multi-table transactional commits with Git-like branch/merge semantics for data lakes.
* **Object Store Layer**: Distributed MinIO S3 cluster provisioned locally with S3 Select capability.

---

## Helm Manifest Architecture

```
helm/lakehouse-substrate/
├── Chart.yaml                  # Chart metadata and dependencies
├── values.yaml                 # Baseline fleet production defaults
├── values-canary.yaml          # Lightweight overrides for ephemeral KinD test
└── templates/
    ├── kafka/
    │   └── kafka-cluster.yaml  # Strimzi KafkaNodePools & Kafka CRD
    ├── compute/
    │   └── trino.yaml          # Trino Coordinator & Worker StatefulSets
    └── catalog/
        └── nessie.yaml         # Project Nessie REST Service & Deployment
```
