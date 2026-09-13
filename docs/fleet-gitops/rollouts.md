# Argo CD ApplicationSet Rollout Engine & Waves

To manage 50 distinct Kubernetes clusters without configuration drift or manual cluster credentials management, the fleet utilizes an Argo CD **ApplicationSet with a Matrix Generator**.

---

## Matrix Generator Architecture

The generator crosses a **Cluster Generator** (selecting targets based on labels like `ring: ring-1-core`) with a **Git Directory Generator** (pulling cluster-specific resource overrides from `argocd/clusters/*.json`):

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: fleet-lakehouse-applicationset
  namespace: argocd
spec:
  strategy:
    type: RollingSync
    rollingSync:
      steps:
        # Step 1: Ring 0 Canary (site01 - site02)
        - matchExpressions:
            - key: ring
              operator: In
              values: ["ring-0-canary"]
          maxUpdate: 100%
        # Step 2: Ring 1 Core GovCloud (site03 - site25)
        - matchExpressions:
            - key: ring
              operator: In
              values: ["ring-1-core"]
          maxUpdate: 25%
        # Step 3: Ring 2 Air-Gapped (site26 - site50)
        - matchExpressions:
            - key: ring
              operator: In
              values: ["ring-2-airgap"]
          maxUpdate: 20%
```

---

## Phased Progression & Gating Mechanics

```
+---------------------------------------------------------------------------------------+
|  WAVE 0: CANARY RING (100% maxUpdate)                                                 |
|  Targets: site01, site02                                                              |
|  Action: Argo CD applies new manifests --> Triggers delivery-cli in-cluster probe     |
|  Gate Condition: synthetic_query_duration_s < 2.0s & pvc_bind_latency_ms < 100ms      |
+---------------------------------------------------------------------------------------+
                                        │ PASS
                                        ▼
+---------------------------------------------------------------------------------------+
|  WAVE 1: GOVCLOUD EAST BATCH (25% maxUpdate)                                          |
|  Targets: site03 - site08                                                             |
|  Gate Condition: Zero alerts on PrometheusRule LakehouseKafkaConsumerLagCritical      |
+---------------------------------------------------------------------------------------+
                                        │ PASS
                                        ▼
+---------------------------------------------------------------------------------------+
|  WAVE 2: GOVCLOUD WEST BATCH (25% maxUpdate)                                          |
|  Targets: site09 - site14                                                             |
+---------------------------------------------------------------------------------------+
```
