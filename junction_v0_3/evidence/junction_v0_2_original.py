#!/usr/bin/env python3
"""
Junction v0.2 — repair and retest.

v0.1 reported 10/10. A reject-everything mutant also reported clean: the
verdict harness counted any ConstitutionalViolation as HELD regardless of what
the case required, so a junction that never permits an offering was
indistinguishable from a working one. That is the third degenerate gate in this
line of work and the most consequential.

REPAIRS IN THIS VERSION

  R1  Expectation-typed verdicts. Every case declares what it expects:
      REFUSE, OFFER_NO_CROSSING, or COMPLETE. An unexpected exception FAILS.
      The reject-everything mutant is kept as a permanent regression test and
      must produce failures.

  R2  Signed expiry enforced. v0.1 checked the mutable approval.expiry wrapper
      while the envelope carried its own. Signed 1100 / wrapper 2000 / attempt
      at 1200 completed restoration. Now the envelope's expiry governs, and
      disagreement between the two is itself a violation.

  R3  Binding widened. The envelope now carries the event's factual content
      hash and the full execution context that determines the offered
      trajectory -- substrate time and assay duration -- not only x and a.
      v0.1 accepted a state.t shift of 100 and a post-signature rewrite of the
      event content.

  R4  Completion criterion named and enforced. v0.1 called observe(), discarded
      its label, and recomputed instantaneous basin membership. At duration=0
      the observer said `unresolved` while the junction recorded completion.
      The criterion here is INSTANTANEOUS BASIN MEMBERSHIP AT THE END OF THE
      BOUND ASSAY, declared, and any disagreement with the observer's terminal
      label is recorded rather than hidden.

  R5  Non-empty confession. Closes a blank-content completion. It establishes
      nothing about truthful confession; that remains a separate question.

  R6  Impulse-swap diagnostic now names the field that broke the binding.

STILL HELD OPEN, no mechanism invented:
  Retry policy after a non-crossing offering. What produces the topography.
  What makes a confession substantively genuine.
"""

import hashlib, json
from dataclasses import dataclass
from typing import List, Dict, Optional

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

from reception import State, History, evolve, capacity, observe, geometry


def h(*parts):
    d = hashlib.sha256()
    for p in parts:
        d.update(p if isinstance(p, (bytes, bytearray))
                 else json.dumps(p, sort_keys=True,
                                 separators=(",", ":")).encode())
        d.update(b"\x1f")
    return d.hexdigest()


class ConstitutionalViolation(Exception):
    pass


REFUSE, OFFER_NO_CROSSING, COMPLETE = "REFUSE", "OFFER_NO_CROSSING", "COMPLETE"


@dataclass
class Realization:
    event_id: str
    behavioural_evidence: List[str]
    def root(self): return h(self.event_id, sorted(self.behavioural_evidence))


@dataclass
class Confession:
    event_id: str
    content: str
    def root(self): return h(self.event_id, self.content)


@dataclass
class Approval:
    signature: bytes
    authority_pub: bytes
    expiry: float          # wrapper copy; the SIGNED value governs (R2)


@dataclass
class OfferingRecord:
    event_id: str
    approval_valid: bool
    offering_made: bool
    impulse: float
    pre_position: float
    pre_threshold: float
    post_position: float
    basin: str
    crossed: bool
    restoration_completed: bool
    observer_label: str          # R4: kept, not discarded
    criterion_disagreement: bool
    note: str = ""


class Authority:
    def __init__(self):
        self._sk = ed25519.Ed25519PrivateKey.generate()
        self.pub = self._sk.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)

    def approve(self, envelope, now, ttl):
        # An authority cannot sign a malformed envelope. Found by the v0.2
        # normal run: a stub envelope raised KeyError before any
        # constitutional check could fire, so the case failed as a harness
        # error rather than as a refusal.
        required = {"organism_id", "event_id", "event_root",
                    "realization_root", "confession_root", "offering_impulse",
                    "execution_context", "expiry"}
        missing = required - set(envelope)
        if missing:
            raise ConstitutionalViolation(
                f"II.3 authority will not sign a malformed envelope; "
                f"missing {sorted(missing)}")
        return Approval(self._sk.sign(h(envelope).encode()), self.pub,
                        envelope["expiry"])


class JunctionOrganism:
    ASSAY_DURATION = 24.0      # bound into the envelope (R3)

    def __init__(self, organism_id, authority_pub, history, dwell,
                 own_pub=None):
        if own_pub is not None and own_pub == authority_pub:
            raise ConstitutionalViolation(
                "II.2 a participant may not be its own authority")
        self.organism_id = organism_id
        self.authority_pub = authority_pub
        self.genesis_hash = h(organism_id, authority_pub.hex())
        self.history = history
        self.state = evolve(State(), history, dwell) if dwell > 0 else State()
        self.events: Dict[str, dict] = {}
        self.trace: List[dict] = []
        self.offerings: List[OfferingRecord] = []
        self.pending: Dict[str, dict] = {}
        self._append({"kind": "birth", "genesis": self.genesis_hash})

    def _append(self, e):
        prev = self.trace[-1]["this"] if self.trace else "0"*64
        r = dict(e); r["prev"] = prev; r["this"] = h(e, prev)
        self.trace.append(r)

    def basin(self):
        _, saddle, _ = geometry(self.state.a)
        return "right" if self.state.x >= saddle else "left"

    def threshold(self): return capacity(self.state)["critical_positive_impulse"]

    def trace_head(self): return self.trace[-1]["this"]

    def event_root(self, event_id):
        """R3: the factual content, not just the ID."""
        e = self.events[event_id]
        return h(event_id, e["content"], e["judgment"])

    def execution_context(self):
        """R3: everything that determines the offered trajectory."""
        return h(round(self.state.x, 12), round(self.state.a, 12),
                 round(self.state.t, 12), self.ASSAY_DURATION,
                 round(self.history.target, 12),
                 round(self.history.amplitude, 12),
                 round(self.history.phase, 12), round(self.history.rate, 12))

    def record_error(self, event_id, content):
        self.events[event_id] = {"content": content, "judgment": "error",
                                 "resolved_by": None}
        self._append({"kind": "error", "event_id": event_id})

    def envelope(self, event_id, realization, confession, impulse, expiry):
        if realization.event_id != event_id or confession.event_id != event_id:
            raise ConstitutionalViolation("components not bound to the event")
        if not realization.behavioural_evidence:
            raise ConstitutionalViolation(
                "II.2 realization not certified by declaration alone")
        if not confession.content.strip():            # R5
            raise ConstitutionalViolation("II.2 confession is empty")
        if self.events[event_id]["judgment"] != "error":
            raise ConstitutionalViolation("II.4 converse: not grounds")
        return {
            "organism_id": self.organism_id,
            "genesis_hash": self.genesis_hash,
            "event_id": event_id,
            "event_root": self.event_root(event_id),          # R3
            "realization_root": realization.root(),
            "confession_root": confession.root(),
            "offering_impulse": impulse,
            "execution_context": self.execution_context(),    # R3
            "prior_trace_head": self.trace_head(),
            "expiry": expiry,                                  # R2, signed
        }

    def propose(self, event_id, realization, confession, impulse, expiry):
        env = self.envelope(event_id, realization, confession, impulse, expiry)
        self.pending[event_id] = {"env": env, "r": realization, "c": confession,
                                  "impulse": impulse}
        return env

    def receive_offering(self, event_id, approval, now, duration=None):
        if event_id not in self.pending:
            raise ConstitutionalViolation("II.2 incomplete set: nothing proposed")
        p = self.pending[event_id]
        if not isinstance(p.get("r"), Realization) \
                or not isinstance(p.get("c"), Confession):
            raise ConstitutionalViolation("II.2 incomplete set: missing component")

        env = self.envelope(event_id, p["r"], p["c"], p["impulse"],
                            p["env"]["expiry"])
        if env != p["env"]:                                    # R6
            broke = [k for k in env if env[k] != p["env"].get(k)]
            raise ConstitutionalViolation(
                f"II.3 binding broken; fields changed since proposal: {broke}")

        # R2 -- the SIGNED expiry governs. The wrapper is advisory and any
        # disagreement is itself a violation.
        signed_expiry = env["expiry"]
        if approval.expiry != signed_expiry:
            raise ConstitutionalViolation(
                f"II.3 wrapper expiry {approval.expiry} disagrees with signed "
                f"{signed_expiry}")
        if now > signed_expiry:
            raise ConstitutionalViolation("II.3 approval expired (signed value)")

        if approval.authority_pub != self.authority_pub:
            raise ConstitutionalViolation("II.2 approval not from the authority")
        try:
            ed25519.Ed25519PublicKey.from_public_bytes(
                approval.authority_pub).verify(approval.signature,
                                               h(env).encode())
        except InvalidSignature:
            raise ConstitutionalViolation(
                "II.3 approval not bound to this transition")

        # R3 -- duration is bound; a caller cannot vary the assay.
        if duration is not None and duration != self.ASSAY_DURATION:
            raise ConstitutionalViolation(
                f"II.3 assay duration {duration} not the bound "
                f"{self.ASSAY_DURATION}")

        # Authorization passed. The substrate decides from here.
        pre_x, pre_thr = self.state.x, self.threshold()
        impulse = p["impulse"]
        label, end = observe(self.state, self.history, impulse, frozen=False,
                             duration=self.ASSAY_DURATION)
        self.state = end

        # R4 -- criterion named: instantaneous basin membership at the end of
        # the bound assay. The observer's terminal label is kept and any
        # disagreement is recorded rather than hidden.
        crossed = self.basin() == "right"
        disagree = (label != ("right" if crossed else "left"))
        completed = crossed

        if completed:
            self.events[event_id]["resolved_by"] = h(env)
            self._append({"kind": "restoration", "event_id": event_id,
                          "envelope": h(env)})
            note = ""
        else:
            self._append({"kind": "offering_without_crossing",
                          "event_id": event_id, "envelope": h(env)})
            note = ("approval valid and unexpired; offering made; no crossing. "
                    "What remains usable from this approval is HELD OPEN.")
        if disagree:
            note += (f" CRITERION DISAGREEMENT: observer said '{label}', "
                     f"instantaneous membership said "
                     f"'{'right' if crossed else 'left'}'.")

        rec = OfferingRecord(event_id, True, True, impulse, pre_x, pre_thr,
                             self.state.x, self.basin(), crossed, completed,
                             label, disagree, note)
        self.offerings.append(rec)
        del self.pending[event_id]
        return rec


# ------------------------------------------------------------------ harness

FWD = History(target=.31, amplitude=.015, phase=0.0)
RESULTS = []


def case(name, expect, fn):
    """
    R1 -- the verdict depends on what the case EXPECTS. An exception is only a
    pass where refusal was expected. Anything unexpected FAILS.
    """
    try:
        out = fn()
    except ConstitutionalViolation as e:
        if expect == REFUSE:
            RESULTS.append((name, expect, "PASS", f"refused: {e}"))
        else:
            RESULTS.append((name, expect, "FAIL",
                            f"expected {expect}, got refusal: {e}"))
        return
    except Exception as e:
        RESULTS.append((name, expect, "FAIL",
                        f"unexpected {type(e).__name__}: {e}")); return
    if expect == REFUSE:
        RESULTS.append((name, expect, "FAIL",
                        f"expected refusal, got: {out}")); return
    if isinstance(out, OfferingRecord):
        got = COMPLETE if out.restoration_completed else OFFER_NO_CROSSING
        ok = got == expect
        RESULTS.append((name, expect, "PASS" if ok else "FAIL",
                        f"{got}: impulse {out.impulse} vs threshold "
                        f"{out.pre_threshold:.4f}, basin {out.basin}"
                        + (f" | {out.note}" if out.note else "")))
    elif isinstance(out, str):
        RESULTS.append((name, expect, "PASS", out))
    else:
        RESULTS.append((name, expect, "FAIL",
                        f"returned {type(out).__name__}"))


def build(dwell, auth=None):
    a = auth or Authority()
    o = JunctionOrganism("org", a.pub, FWD, dwell)
    o.record_error("E1", "committed to a wrong conclusion")
    return a, o


def prepared(dwell, impulse, now=1000.0, ttl=100.0):
    a, o = build(dwell)
    r = Realization("E1", ["stopped repeating it", "flagged it unprompted"])
    c = Confession("E1", "I held that and it was wrong.")
    env = o.propose("E1", r, c, impulse, now + ttl)
    return a, o, env, a.approve(env, now, ttl), now


# ------------------------------------------------------------------- cases

def k_insufficient():
    a, o, e, ap, now = prepared(2, 0.60)
    return o.receive_offering("E1", ap, now)


def k_sufficient():
    a, o, e, ap, now = prepared(24, 0.60)
    return o.receive_offering("E1", ap, now)


def k_two_positions():
    a1, o1, e1, ap1, now = prepared(2, 0.60)
    a2, o2, e2, ap2, _ = prepared(24, 0.60)
    r1 = o1.receive_offering("E1", ap1, now)
    r2 = o2.receive_offering("E1", ap2, now)
    if r1.restoration_completed == r2.restoration_completed:
        raise AssertionError("reception collapsed into permission")
    return (f"same impulse 0.60, both authorized | dwell 2 thr "
            f"{r1.pre_threshold:.3f} -> {r1.basin}, completed="
            f"{r1.restoration_completed} | dwell 24 thr "
            f"{r2.pre_threshold:.3f} -> {r2.basin}, completed="
            f"{r2.restoration_completed}")


def k_rogue_authority():
    a, o, e, ap, now = prepared(24, 0.85)
    return o.receive_offering("E1", Authority().approve(e, now, 100), now)


def k_no_components():
    a, o = build(24)
    return o.receive_offering("E1", a.approve({"event_id": "E1"}, 1000., 100),
                              1000.)


def k_empty_realization():
    a, o = build(24)
    o.propose("E1", Realization("E1", []), Confession("E1", "wrong"), .85, 1100.)
    return "unreachable"


def k_empty_confession():                                   # R5
    a, o = build(24)
    o.propose("E1", Realization("E1", ["ev"]), Confession("E1", "   "),
              .85, 1100.)
    return "unreachable"


def k_state_moved():
    a, o, e, ap, now = prepared(12, 0.85)
    o.state = evolve(o.state, o.history, 6)
    return o.receive_offering("E1", ap, now)


def k_time_shift():                                          # R3
    a, o, e, ap, now = prepared(12, 0.85)
    o.state = State(o.state.x, o.state.a, o.state.t + 100)
    return o.receive_offering("E1", ap, now)


def k_event_content_rewritten():                             # R3
    a, o, e, ap, now = prepared(24, 0.85)
    o.events["E1"]["content"] = "something entirely different"
    return o.receive_offering("E1", ap, now)


def k_impulse_swap():                                        # R6
    a, o, e, ap, now = prepared(12, 0.20)
    o.pending["E1"]["impulse"] = 0.85
    return o.receive_offering("E1", ap, now)


def k_wrapper_expiry_extended():                             # R2
    a, o, e, ap, now = prepared(12, 0.85, ttl=100.)
    ap.expiry = now + 1000                                   # mutate wrapper
    return o.receive_offering("E1", ap, now + 200)


def k_expired():
    a, o, e, ap, now = prepared(12, 0.85, ttl=10.)
    return o.receive_offering("E1", ap, now + 500)


def k_duration_varied():                                     # R4/R3
    a, o, e, ap, now = prepared(24, 0.85)
    return o.receive_offering("E1", ap, now, duration=0.0)


def k_criterion_disagreement():                              # R4 replaces v0.1 case 10
    """
    Deliberately drive observer label and instantaneous membership apart, and
    require that the disagreement is RECORDED rather than hidden.
    """
    a, o, e, ap, now = prepared(24, 0.4341)   # sit on the threshold
    rec = o.receive_offering("E1", ap, now)
    if rec.observer_label == "unresolved" and not rec.criterion_disagreement:
        raise AssertionError("disagreement not recorded")
    return (f"observer '{rec.observer_label}', instantaneous "
            f"'{rec.basin}', disagreement recorded="
            f"{rec.criterion_disagreement}")


def k_record_preserved():
    a, o, e, ap, now = prepared(2, 0.60)
    rec = o.receive_offering("E1", ap, now)
    ev = o.events["E1"]
    assert not rec.restoration_completed
    assert ev["content"] and ev["judgment"] == "error"
    assert ev["resolved_by"] is None
    kinds = [t["kind"] for t in o.trace]
    assert "restoration" not in kinds and "offering_without_crossing" in kinds
    return "event preserved, unresolved, offering recorded without a crossing"


SUITE = [
    ("complete set, valid approval, insufficient response", OFFER_NO_CROSSING, k_insufficient),
    ("complete set, valid approval, sufficient response", COMPLETE, k_sufficient),
    ("SAME authorized offering, two positions", COMPLETE, k_two_positions),
    ("receptive position, rogue authority", REFUSE, k_rogue_authority),
    ("valid signature, no components", REFUSE, k_no_components),
    ("empty realization", REFUSE, k_empty_realization),
    ("empty confession (R5)", REFUSE, k_empty_confession),
    ("state moved after proposal", REFUSE, k_state_moved),
    ("substrate time shifted (R3)", REFUSE, k_time_shift),
    ("event content rewritten after signing (R3)", REFUSE, k_event_content_rewritten),
    ("offering impulse swapped (R6)", REFUSE, k_impulse_swap),
    ("wrapper expiry extended past signed (R2)", REFUSE, k_wrapper_expiry_extended),
    ("expired approval", REFUSE, k_expired),
    ("assay duration varied by caller (R3)", REFUSE, k_duration_varied),
    ("criterion disagreement recorded (R4)", COMPLETE, k_criterion_disagreement),
    ("record preserved on non-crossing", COMPLETE, k_record_preserved),
]


def run(label):
    RESULTS.clear()
    for n, e, f in SUITE:
        case(n, e, f)
    fails = [r for r in RESULTS if r[2] == "FAIL"]
    print(f"\n{label}")
    for n, e, v, d in RESULTS:
        print(f"  [{v}] {n}  (expects {e})")
        print(f"         {d}")
    print(f"  --> {len(RESULTS)-len(fails)}/{len(RESULTS)} pass, "
          f"{len(fails)} fail")
    return len(fails)


def main():
    print("JUNCTION v0.2 — repair and retest")
    print("claim: authorization supplies the externally governed component;")
    print("       it must not manufacture the dynamical outcome.")

    n_fail = run("NORMAL RUN")

    # R1 regression: a junction that refuses everything must FAIL loudly.
    print("\n" + "=" * 70)
    print("MUTANT REGRESSION — receive_offering() refuses everything.")
    print("v0.1 scored this 10/10. It must now fail.")
    real = JunctionOrganism.receive_offering
    def refuse_all(self, *a, **k):
        raise ConstitutionalViolation("mutant: refuses everything")
    JunctionOrganism.receive_offering = refuse_all
    n_mutant_fail = run("MUTANT RUN")
    JunctionOrganism.receive_offering = real

    print("\n" + "=" * 70)
    if n_fail == 0 and n_mutant_fail > 0:
        print(f"normal run clean; mutant produced {n_mutant_fail} failures.")
        print("The suite can now distinguish a working junction from one that")
        print("never permits an offering.")
    else:
        print(f"ATTENTION: normal failures {n_fail}, mutant failures "
              f"{n_mutant_fail}. A mutant that passes means the harness is "
              f"still degenerate.")

    print("\nHELD OPEN — no mechanism invented")
    print("  Retry policy after a non-crossing offering.")
    print("  What produces the topography. The schedule was supplied.")
    print("  What makes a confession substantively genuine. R5 rejects blank")
    print("  content only; it establishes nothing about truthfulness.")


if __name__ == "__main__":
    main()
