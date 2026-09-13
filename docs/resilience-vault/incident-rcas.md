# Incident Root Cause Analyses (RCAs)

The incident archive reflects real failure dynamics encountered in field operations, complete with unfiltered terminal outputs, kernel `dmesg` traces, and causal analysis.

---

## Interactive Incident Triage Console

=== "Incident 1: Cross-Site PVC Deadlock (INC-001)"
    ### Symptom & Volume Status
    ```console
    $ kubectl describe pvc data-kafka-broker-0 -n lakehouse-infra
    Name:          data-kafka-broker-0
    Namespace:     lakehouse-infra
    StorageClass:  ceph-block-fast
    Status:        Bound
    Volume:        pvc-c189b4f2-9811-4f77-88ab-44101e9d2981
    Events:
      Type     Reason              Age                From                     Message
      ----     ------              ----               ----                     -------
      Warning  FailedAttachVolume  2m (x12 over 14m)  attachdetach-controller  AttachVolume.Attach failed for volume "pvc-c189b4f2-9811-4f77-88ab-44101e9d2981" : Ceph CSI request timed out after 30s (context deadline exceeded)
      Warning  FailedMount         1m (x5 over 10m)   kubelet                  Unable to attach or mount volumes: timed out waiting for the condition
    ```

    ### Kernel Dmesg Traces
    ```console
    # dmesg -T | grep -E "rbd|ceph|blk"
    [Fri Aug 14 03:16:55 2026] libceph: osd32 10.240.12.89:6804 connection reset
    [Fri Aug 14 03:17:02 2026] rbd: rbd0: block request 0xffff9a88c0 expired after 120000ms
    [Fri Aug 14 03:17:03 2026] rbd: rbd0: exclusive-lock release timed out, retaining lock
    [Fri Aug 14 03:18:22 2026] rbd: rbd0: aborting I/O requests due to lock transition deadlock
    ```

    ### Root Cause & Mitigation
    * **Root Cause**: CSI attacher connection pool starved during simultaneous broker failover; `attachdetach-controller` entered 6-minute exponential backoff.
    * **Remediation**: Tuned CSI driver concurrency to 16 threads; switched StorageClass to `volumeBindingMode: WaitForFirstConsumer`.

=== "Incident 2: Trino Coordinator OOM (INC-002)"
    ### JVM GC Pause & Evacuation Failure
    ```console
    [2026-08-22T14:26:15.102+0000] GC(142) Pause Full (G1 Evacuation Pause) (G1 Compaction Pause)
    [2026-08-22T14:26:15.114+0000] GC(142) Evacuate Collection Set: 14120.3ms
    [2026-08-22T14:26:29.890+0000] GC(142) Heap: 61440.0M(61440.0M)->60912.4M(61440.0M)
    [2026-08-22T14:26:29.891+0000] GC(142) Total pause time: 14789.2ms
    ```

    ### Thread Contention & Kernel OOM-Killer
    ```console
    $ jstack -l 184920 | grep -A 10 "io.trino.spiller"
    "query-execution-481" #192 daemon prio=5 os_prio=0 cpu=14812.11ms elapsed=420.12s tid=0x00007f98b4109000
       java.lang.Thread.State: WAITING (parking)
       at io.trino.spiller.FileSingleStreamSpiller.flushSpillBuffer(FileSingleStreamSpiller.java:188)

    $ dmesg -T | grep -E "Out of memory|Killed process"
    [Sat Aug 22 14:27:40 2026] Out of memory: Kill process 184920 (java) score 982 or sacrifice child
    [Sat Aug 22 14:27:40 2026] Killed process 184920 (java) total-vm:68412896kB, anon-rss:62914560kB
    ```

    ### Root Cause & Mitigation
    * **Root Cause**: 180,000+ tiny spill files (avg 1.2MB) exhausted coordinator heap pointer tracking; off-heap allocations exceeded cgroup headroom.
    * **Remediation**: Set minimum spill chunk size to 64MB; adopted direct-attached NVMe PCIe SSDs ([ADR 0001](file:///C:/Users/FreeF/projects/platform-resilience-fieldguide/docs/adr/0001-nvme-spill-mounts-for-trino.md)).

=== "Incident 3: CNI MTU Asymmetry & Mesh Drops (INC-003)"
    ### Live Tcpdump MTU Bottleneck Capture
    ```console
    # tcpdump -nnvv -i eth0 'tcp port 7077 or icmp'
    14:02:11.109283 IP 10.244.2.14.7077 > 10.244.5.22.42100: Flags [.], seq 1:1440, ack 1, win 502, length 1440
    14:02:11.109312 IP 10.244.2.14 > 10.244.5.22: ICMP 10.244.2.14 unreachable - need to frag (mtu 1420), length 556
    14:02:11.109350 IP 10.244.2.14.7077 > 10.244.5.22.42100: Flags [F.], seq 1441, ack 1, win 502, length 0
    ```

    ### Cilium eBPF Drop Monitor Trace
    ```console
    # cilium monitor --type drop -v
    xx drop (Invalid packet size) flow 0x98f4b to-endpoint 812, identity 4819->1204, cpu 3: 10.244.8.42:7337 -> 10.244.3.18:48922 tcp ACK, length 1472
       Packet size 1522 exceeds device MTU 1450
       Drop reason: Packet size exceeds MTU and DF flag is set

    # cilium-dbg bpf tunnel list
    TUNNEL          ENDPOINT   PREFIX      ENCAP   MTU
    10.244.8.42     ep-812     10.244.8/24 geneve  1450  [MISMATCH: Transit Path=1420]
    ```

    ### Root Cause & Mitigation
    * **Root Cause**: Mesh Geneve encapsulation header (50 bytes) exceeded 1420-byte WireGuard transit MTU; perimeter firewalls silently dropped ICMP Type 3 Code 4 PMTUD packets.
    * **Remediation**: Clamped fleetwide CNI pod MTU to 1350 bytes; deployed `validate_cni_mtu.py` in CI.

=== "Incident 4: Stale Leases & Split-Brain Partition (INC-004)"
    ### Etcd Cluster Partition State
    ```console
    $ etcdctl endpoint status --cluster -w table
    +---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
    |         ENDPOINT          |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX | ERRORS |
    +---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
    | https://10.240.0.11:2379  | 8e9e05c52164694d | 3.5.12  |   42 MB |      true |      false |         8 |    1429810 |            1429810 |        |
    | https://10.240.0.12:2379  | 6f4208a12b4e819a | 3.5.12  |   42 MB |     false |      false |         8 |    1429810 |            1429810 |        |
    | https://10.240.0.21:2379  | c1890bf23a0194bc | 3.5.12  |   41 MB |     false |      false |         6 |    1419200 |            1419200 | [PART] |
    +---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
    ```

    ### Automated Recovery Execution
    ```console
    $ docker run --rm --net=host -v ~/.kube/config:/home/nonroot/.kube/config:ro         ghcr.io/freefades2black/platform-sre-tools:latest --namespace lakehouse-compute --prune-finalizers --confirm
    [+] Scanned namespace 'lakehouse-compute': 3 deadlocked pods identified.
    [+] Successfully dislodged 'sparkoperator.k8s.io/submission-finalizer' from pod spark-driver-01.
    [+] Controller lease acquired by cp-01; queue reconciliation resumed.
    ```
