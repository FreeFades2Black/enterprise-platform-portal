# Multi-Site Governance & DoD Iron Bank Compliance

All container workloads across the 50 clusters operate under strict DoD Platform One STIG (Security Technical Implementation Guide) baselines enforced at admission time via Kyverno and Gatekeeper.

---

## Iron Bank Admission Control Policies

ワークロード specifications must adhere to `security/kyverno/dod-ironbank-baseline.yaml`. Any pod manifest violating these requirements is rejected at the API server admission webhook stage:

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: dod-ironbank-baseline
spec:
  validationFailureAction: Enforce
  background: true
  rules:
    - name: require-run-as-non-root
      match:
        any:
          - resources:
              kinds: ["Pod"]
      validate:
        message: "STIG V-242415: Containers must run as non-root (runAsNonRoot: true)."
        pattern:
          spec:
            securityContext:
              runAsNonRoot: true

    - name: require-read-only-rootfs
      match:
        any:
          - resources:
              kinds: ["Pod"]
      validate:
        message: "STIG V-242417: Container root filesystem must be read-only."
        pattern:
          spec:
            containers:
              - securityContext:
                  readOnlyRootFilesystem: true
```

---

## Supply Chain Integrity & Attestation Flow

```mermaid
sequenceDiagram
    autonumber
    participant Dev as Platform Engineer
    participant CI as GitHub Actions CI
    participant IronBank as DoD Iron Bank VAT
    participant Cosign as Sigstore Cosign
    participant K8s as Cluster Admission (Kyverno)

    Dev->>CI: Push Git commit to main
    CI->>IronBank: Pull hardened Chainguard base image
    CI->>CI: Build multi-stage distroless binary
    CI->>CI: Execute Trivy / Grype Vulnerability Scan
    CI->>Cosign: Cryptographically sign image digest
    CI->>K8s: Submit deployment manifest
    K8s->>K8s: Kyverno validates Cosign signature against Platform One PKI
    K8s-->>Dev: Pod admitted & scheduled (Zero Trust verified)
```
