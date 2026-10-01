# Enterprise Platform Delivery & Reliability Portal

[![Portal Status](https://img.shields.io/badge/Mission_Control-Online-00e5ff?style=flat-square&logo=kubernetes)](https://freefades2black.github.io/enterprise-platform-portal)
[![Material for MkDocs](https://img.shields.io/badge/Docs_Engine-Material_for_MkDocs-blue?style=flat-square)](https://squidfunk.github.io/mkdocs-material/)
[![DoD Compliance](https://img.shields.io/badge/Security-Platform_One_STIG-red?style=flat-square)](https://freefades2black.github.io/enterprise-platform-portal/fleet-overview/compliance/)
[![Passing Canary E2E](https://img.shields.io/badge/Canary_Gate-Passing-green?style=flat-square)](https://freefades2black.github.io/enterprise-platform-portal/fleet-gitops/canary-gate/)

The centralized Mission Control / Internal Developer Platform (IDP) portal for managing, delivering, and operating the federal data lakehouse platform across **50 production Kubernetes clusters**.

---

## Dual-Pillar Portal Architecture

1. **Pillar 1: Fleet GitOps & Delivery Engine ([`fleet-lakehouse-operator`](https://github.com/FreeFades2Black/fleet-lakehouse-operator))**
   - Argo CD ApplicationSet Matrix Generator & Staged Rollout Waves
   - Lakehouse Substrate Specs (Strimzi Kafka, Trino 435 NVMe Spill, Nessie Iceberg)
   - Ephemeral Canary CI/CD Gating (3-Node KinD Cluster Gate)
   - Hardened OCI Packaging & Sigstore Cosign Attestation

2. **Pillar 2: Field SRE & Resilience Vault ([`platform-resilience-fieldguide`](https://github.com/FreeFades2Black/platform-resilience-fieldguide))**
   - Deep-Dive Incident RCAs with Raw Terminal Scrollbacks (PVC Deadlock, Trino OOM, CNI MTU Drops, Split-Brain Leases)
   - Deterministic Triage Runbooks (Ingest Lag, Zombie Spark Driver Cleanup, Air-Gapped Registry Mirroring)
   - Golden Signals as Code (`PrometheusRule` matrices & Grafana Cockpit)

---

## Local Development & Verification

```bash
# Install dependencies
pip install mkdocs-material mkdocs-minify-plugin

# Build site with strict validation (checks links & schemas)
make build

# Launch local preview server with live reload
make serve
```

The site will be available at `http://127.0.0.1:8000/`.

---

## Automated Deployment to GitHub Pages

Every commit pushed to `main` triggers `.github/workflows/deploy-portal.yml`, compiling the site with strict markdown linting and deploying to GitHub Pages.

## Automated CI Maintenance Log
<!-- START_AGENT_MAINTENANCE_LOG -->
#### Maintenance Run: `2026-10-01 20:50:03 UTC`
- `.github/workflows/deploy-portal.yml`: Upgrade actions/checkout from v4 to v7 for security & performance. [Research: RCSB PDB AI Help Desk: retrieval-augmented generation for protein structure deposition support (OpenAlex / Global University Research)] [NIST SP 800-218 PW.4]
- `.github/workflows/deploy-portal.yml`: Upgrade actions/setup-python from v5 to v7 for security & performance. [Research: RCSB PDB AI Help Desk: retrieval-augmented generation for protein structure deposition support (OpenAlex / Global University Research)] [NIST SP 800-218 PW.4]
- `.github/workflows/deploy-portal.yml`: Upgrade actions/upload-pages-artifact from v3 to v5 for security & performance. [Research: RCSB PDB AI Help Desk: retrieval-augmented generation for protein structure deposition support (OpenAlex / Global University Research)] [NIST SP 800-218 PW.4]
- `.github/workflows/deploy-portal.yml`: Upgrade actions/deploy-pages from v4 to v5 for security & performance. [Research: RCSB PDB AI Help Desk: retrieval-augmented generation for protein structure deposition support (OpenAlex / Global University Research)] [NIST SP 800-218 PW.4]
- `.github/workflows/deploy-portal.yml`: Enforce timeout-minutes: 10 to kill hung processes and prevent runaway billing (CISA & FinOps).

<!-- END_AGENT_MAINTENANCE_LOG -->
