# Gospel Positional Reception

**Gospel-shaped sealed packs — positional reception v0.1 / v0.2 and junction v0.3**

Public shelf for the Sep 2026 gospel-line harnesses: dwelling/positional reception instruments and the corrected junction harness. Manifests verified (`manifest.json` sha256 maps).

**Org / profile:** [RMac-triadicIntelligence](https://github.com/RMac-triadicIntelligence)

Licensor: [Soulshine](ABOUT_SOULSHINE.md) (501(c)(3)). License: [Apache-2.0](LICENSE). See [NOTICE](NOTICE).

## Packages

| Pack | Path | What |
|---|---|---|
| **positional reception v0.1** | [`positional_reception_v0_1/`](positional_reception_v0_1/) | First executable investigation of Raised, Not Rented §4.5 — dwelling dynamics; results + FINDINGS. |
| **positional reception v0.2** | [`positional_reception_v0_2/`](positional_reception_v0_2/) | Observable-only prediction experiment + movement diagnostic (gospel-only branch); PROTOCOL + FINDINGS + results. |
| **junction v0.3** | [`junction_v0_3/`](junction_v0_3/) | Corrected junction harness and retest (mutant gate); results recorded. |

## Claim boundary

These are **simulation / harness batteries**. Seals (`manifest.json`) attest integrity of these runs — **not** consciousness, AGI, biological life, or moral truth. Read each package README / PROTOCOL / FINDINGS for scored hypotheses and verdicts. Do not invent claims beyond those documents.

## Sibling shelf

- [raised-not-rented](https://github.com/RMac-triadicIntelligence/raised-not-rented) — commons-kernel sealed batteries (v0.10–v0.13)

## Verify a seal

```bash
python3 - <<'PY'
import json, hashlib, pathlib, sys
root = pathlib.Path(".")
ok = True
for pack in ["positional_reception_v0_1", "positional_reception_v0_2", "junction_v0_3"]:
    m = json.loads((root / pack / "manifest.json").read_text())
    for rel, expect in m["sha256"].items():
        p = root / pack / rel
        got = hashlib.sha256(p.read_bytes()).hexdigest()
        status = "OK" if got == expect else "FAIL"
        if status != "OK":
            ok = False
        print(f"{status}  {pack}/{rel}")
sys.exit(0 if ok else 1)
PY
```
