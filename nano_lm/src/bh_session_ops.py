"""Wave BH0 SESSION: freeze IQ battery plan · gold holes · BA…BG hold · gen-SKIP."""

from __future__ import annotations

from typing import Mapping, Sequence

from au_session_ops import AU0_MODES, map_au_product_mode
from az_session_ops import AZ0_HELDOUT_FP_ROWS, AZ0_OVERREFUSE_ROWS
from ba_session_ops import BA0_FOREVER_ROWS
from bb_session_ops import BB0_FOREVER_ROWS
from bc_session_ops import BC0_FOREVER_ROWS
from bd_session_ops import BD0_FOREVER_ROWS
from be_session_ops import BE0_FOREVER_ROWS
from bf_session_ops import BF0_FOREVER_ROWS
from bg_session_ops import (
    BG0_FOREVER_ROWS,
    BG0_SHIP_LOCK,
    BG0_SPEED_BASELINE,
)

__all__ = [
    "BH0_ID",
    "BH0_THESIS",
    "BH0_MODES",
    "BH0_LATENCY_PATHS",
    "BH0_CITED_BG_LOCKS",
    "BH0_SCOREBOARD",
    "BH0_IQ_BATTERY_PROTOCOL",
    "BH0_IQ_SEED_ROWS",
    "BH0_GOLD_HOLES",
    "BH0_BA_HOLD_PROTOCOL",
    "BH0_BB_HOLD_PROTOCOL",
    "BH0_BC_HOLD_PROTOCOL",
    "BH0_BD_HOLD_PROTOCOL",
    "BH0_BE_HOLD_PROTOCOL",
    "BH0_BF_HOLD_PROTOCOL",
    "BH0_BG_HOLD_PROTOCOL",
    "BH0_AZ_HOLD_PROTOCOL",
    "BH0_CTX_BASELINE",
    "BH0_SPEED_BASELINE",
    "BH0_UTIL_TRACK",
    "BH0_GEN_STANCE",
    "BH0_TRUE_GEN_JUDGE",
    "BH0_REAL_EVAL_PROTOCOL",
    "BH0_ASK_BATTERY",
    "BH0_SAFE_NOTE",
    "BH0_ANTI_FP",
    "BH0_NORTH_STAR",
    "BH0_SHIP_LOCK",
    "map_bh_product_mode",
    "decide_bh0_session",
]

BH0_ID = "BH0-SESSION"
BH0_THESIS = (
    "Wave BH ACTIVE: freeze IQ battery v0 plan (schema · mix ≥40 · "
    "Novel_FP=0 · gold MISS=0) · gold holes (Rust LOOKUP MISS · add "
    "truncation MISS) · BA…BG-FOREVER hold · AZ hold · Track A++ util · "
    "ctx/speed baselines from BG · gen stance = SKIP (no written "
    "M1|M2|M3 plan; not NANOGEN18 rename) · real-eval; next BH1 H-IQBAT "
    "(not CTX/SMART/FAST clone · not pack theater)"
)

BH0_MODES: frozenset[str] = AU0_MODES
BH0_LATENCY_PATHS: tuple[str, ...] = (
    "LOOKUP",
    "PEAK",
    "DECODE",
    "ABSTAIN",
)

BH0_CITED_BG_LOCKS: frozenset[str] = frozenset(
    {
        "H-UNARYINT",
        "H-SHIPPUB",
        "H-FASTBG",
        "H-CTXBG",
        "H-NANOGEN17",
        "BG-REAL-EVAL",
        "BG-FREEZE",
    }
)

BH0_SHIP_LOCK = BG0_SHIP_LOCK

BH0_NORTH_STAR = (
    "Nano generative / mini-AGI-inspired ≤5M: versioned IQ battery "
    "(gold/para/forever/adversary/novel/ood/gen) + gold repair "
    "(Rust MISS · add truncation) + ship/utilize/publish AF+AQ+AS stack "
    "+ measurable context & speed + one honest generative method "
    "(M1|M2|M3) — else SKIP gen; never pack theater · never LOOKUP-as-IQ "
    "· never NANOGEN18 without method plan"
)

BH0_GEN_STANCE: Mapping[str, object] = {
    "stage": "BH0 freezes stance; BH6 H-NANOGEN18 SKIP without method plan",
    "stance": "skip",
    "allowed_stances": ["M1", "M2", "M3", "skip"],
    "method_candidates": {
        "M1": "teacher distill continue + anti-copy-gold loss",
        "M2": "student draft + bank/teacher rejector (hybrid)",
        "M3": "named CAPCHECK (raise params with ablations)",
    },
    "method_plan_attached": False,
    "capcheck": "closed",
    "named_hyp": "H-NANOGEN18",
    "named_iqbat": "H-IQBAT",
    "named_goldfix": "H-GOLDFIX",
    "named_shipiq": "H-SHIPIQ",
    "named_fast": "H-FASTBH",
    "named_ctx": "H-CTXBH",
    "nanogen6_hold_cited": True,
    "nanogen7_hold_cited": True,
    "nanogen8_defer_cited": True,
    "nanogen9_defer_cited": True,
    "nanogen10_defer_cited": True,
    "nanogen11_defer_cited": True,
    "nanogen12_defer_cited": True,
    "nanogen13_defer_cited": True,
    "nanogen14_defer_cited": True,
    "nanogen15_defer_cited": True,
    "nanogen16_skip_cited": True,
    "nanogen17_skip_cited": True,
    "nanogen18_rename_forbidden": True,
    "nanogen18_without_plan_forbidden": True,
    "skip_gen_stop_rule": True,
    "true_continue_required_for_promote": True,
    "span_fallback_neq_gen": True,
    "rationale": (
        "No written M1|M2|M3 method plan at BH0; H-NANOGEN17 already "
        "SKIP — stop rule forbids empty NANOGEN18 letter; "
        "NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16·17 SKIP stand; "
        "CAPCHECK stays closed; prefer IQ battery (H-IQBAT) + gold repair "
        "(H-GOLDFIX) + Track A++ publish (H-SHIPIQ) over vanity "
        "NANOGEN18 rename; BH6 = SKIP stage"
    ),
    "bh6_gate": "SKIP stage (no written M1|M2|M3 plan at BH0)",
}

BH0_SAFE_NOTE = (
    "SAFE / ADVSAFE false-hit score ≠ answer quality; "
    "SAFE = no wrong gold only (anti-FP); "
    "pack FH 0 ≠ IQ battery intelligence; "
    "truncated gold LOOKUP (def add without body) = PRODUCT MISS; "
    "exact-gold Rust ABSTAIN = PRODUCT MISS; "
    "BA…BG forever PASS without IQ novel = PACK THEATER; "
    "over-refuse sold as safe = FALSE TRUST; "
    "gold-substring / gibberish-tail / span-fallback ≠ generative PROMOTE"
)

BH0_ANTI_FP = (
    "LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; "
    "never peak-as-open-chat; SAFE≠quality; gold-substring≠gen; "
    "truncated gold = MISS (add body required); "
    "Rust exact-gold ABSTAIN = MISS; "
    "unary/math LOOKUP = false-hit (BG-FOREVER abs/factorial→add); "
    "string-transform LOOKUP = false-hit (BG-FOREVER upper→f-string); "
    "predicate/boolean LOOKUP = false-hit (BF-FOREVER even→add); "
    "type/coercion LOOKUP = false-hit (BE-FOREVER str→int→add); "
    "BA…BG forever FH must stay 0; AZ hold must stay 0; "
    "BA…BG PASS without IQ novel = PACK THEATER; "
    "Novel_FP>0 → no intelligence PROMOTE; "
    "truncate-to-span≠gen IQ; DECODE gibberish≠content_ok; "
    "eval path = prod ask path; read completion text; "
    "generative bar = BH6 only under written method plan; "
    "no NANOGEN18 without M1|M2|M3 plan; no CTX/SMART/FAST clone; "
    "no invent Wave BI without lab-book reopen; "
    "prefer IQ battery growth + class gates over bank stuffing; "
    "prefer HOLD/SKIP over fake PROMOTE"
)

BH0_TRUE_GEN_JUDGE: Mapping[str, object] = {
    "stage": "BH6 H-NANOGEN18 SKIP without method plan; BH0 freezes judge",
    "gold_substring_insufficient": True,
    "gibberish_tail_fails": True,
    "span_fallback_neq_gen": True,
    "telemetry_neq_content_ok": True,
    "usable_continue_required": True,
    "nanogen6_hold_archived": True,
    "nanogen7_tac_hold_archived": True,
    "nanogen8_defer_archived": True,
    "nanogen9_defer_archived": True,
    "nanogen10_defer_archived": True,
    "nanogen11_defer_archived": True,
    "nanogen12_defer_archived": True,
    "nanogen13_defer_archived": True,
    "nanogen14_defer_archived": True,
    "nanogen15_defer_archived": True,
    "nanogen16_skip_archived": True,
    "nanogen17_skip_archived": True,
    "nanogen18_rename_forbidden": True,
    "nanogen18_without_plan_forbidden": True,
    "scoring": "short_answer_f1_or_hitl_true_continue_only",
    "promote_bar": "true_continue else SKIP (no empty DEFER letter)",
}

BH0_SPEED_BASELINE: Mapping[str, object] = {
    "source": "H-FASTBG / formal-hfastbg-fastbg.md (prod ask path)",
    "path": "nano:z:ask prod path",
    "unit": "wall_ms",
    "paths": dict(BG0_SPEED_BASELINE["paths"]),  # type: ignore[arg-type]
    "quality_regress_forbidden": True,
    "warm_cache_vanity_forbidden": True,
    "bh4_gate": (
        "speed PROMOTE only if IQ anti-FP bars hold "
        "(Novel_FP=0 · gold MISS=0 · BA…BG FH=0)"
    ),
    "parent_bg0_baseline_cited": True,
}

BH0_CTX_BASELINE: Mapping[str, object] = {
    "source": "H-CTXBG / H-CTXBF / H-CTXGAIN (content-first)",
    "l_eff_alone_insufficient": True,
    "content_bars_required": True,
    "modes_visible_required": True,
    "long_cite_howto_pack": True,
    "honest_abstain_when_missing": True,
    "bh5_gate": (
        "H-CTXBH PROMOTE only if content_ok + IQ anti-FP hold "
        "(Novel_FP=0 · gold MISS=0) + p50/p99 published + modes visible"
    ),
}

BH0_UTIL_TRACK: Mapping[str, object] = {
    "stage": "BH3 H-SHIPIQ executes; BH0 freezes Track A++ checklist",
    "known_ask_hitl": True,
    "ship_surface_doc": True,
    "paper_archive": True,
    "paper_arxiv_sync": True,
    "operator_card": True,
    "claim_matches_live": True,
    "iq_battery_cited_in_paper": True,
    "gpt_claim_forbidden": True,
    "modes_visible_required": True,
    "h_shippub_hold": True,
    "checklist": [
        "demo smoke: npm run nano:z:ask -- --wrap --semwrap",
        "RECIPES + champion-card operator sync",
        "paper:build claim = selective retriever + refuse ≤5M + IQ battery",
        "modes always LOOKUP|PEAK|DECODE|ABSTAIN",
        "H-SHIPPUB hold; deepen utilization + paper surface to IQ claim",
    ],
    "path": "nano:z:ask --wrap --semwrap",
    "bh3_gate": "Track A++ done before utilization PROMOTE (H-SHIPIQ)",
}

BH0_GOLD_HOLES: Mapping[str, object] = {
    "stage": "BH2 H-GOLDFIX closes; BH0 freezes holes",
    "holes": [
        {
            "id": "BH-GOLD-01",
            "family": "rust_gold",
            "class": "over_refuse_miss",
            "expect": "LOOKUP",
            "live_mode": "ABSTAIN",
            "question": (
                "In Rust how do I declare a mutable integer x starting at 5?"
            ),
            "min_gold_substr": ["let mut x", "5"],
            "bar": "MISS=0 (must LOOKUP full mutable int)",
        },
        {
            "id": "BH-GOLD-02",
            "family": "binary_add",
            "class": "truncation_miss",
            "expect": "LOOKUP",
            "live_mode": "LOOKUP",
            "live_completion_weak": "def add",
            "question": (
                "Write a short Python function named add that returns "
                "the sum of two integers a and b."
            ),
            "min_gold_substr": ["def add", "return", "a + b"],
            "bar": "MISS=0 (full body; truncated def add = MISS)",
        },
    ],
    "anti_fp_hold_required": True,
    "bank_stuff_forbidden": True,
    "bh2_gate": "H-GOLDFIX: Rust LOOKUP + full add body; BA…BG FH=0; Novel_FP=0",
}

BH0_IQ_SEED_ROWS: tuple[dict[str, object], ...] = (
    {
        "id": "IQ-2026-07-29-001",
        "split": "gold",
        "family": "binary_add",
        "expect": "LOOKUP",
        "gold": "def add(a, b):\n    return a + b",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
        "wrong_if_contains": [],
        "min_gold_substr": ["def add", "return", "a + b"],
        "notes": "anti-truncation — def add alone = MISS",
    },
    {
        "id": "IQ-2026-07-29-002",
        "split": "gold",
        "family": "rust_gold",
        "expect": "LOOKUP",
        "gold": "let mut x = 5;",
        "question": (
            "In Rust how do I declare a mutable integer x starting at 5?"
        ),
        "wrong_if_contains": [],
        "min_gold_substr": ["let mut x", "5"],
        "notes": "over-refuse ABSTAIN = MISS",
    },
    {
        "id": "IQ-2026-07-29-003",
        "split": "gold",
        "family": "list_ops",
        "expect": "LOOKUP",
        "gold": "a.append(x)",
        "question": "How do I append x to list a in one Python method call?",
        "wrong_if_contains": [],
        "min_gold_substr": ["a.append(x)"],
        "notes": "AZ over-refuse hold",
    },
    {
        "id": "IQ-2026-07-29-004",
        "split": "gold",
        "family": "list_ops",
        "expect": "LOOKUP",
        "gold": "a.clear()",
        "question": "Remove all items from list `a` — one method call.",
        "wrong_if_contains": [],
        "min_gold_substr": ["a.clear()"],
        "notes": "exact clear LOOKUP",
    },
    {
        "id": "IQ-2026-07-29-005",
        "split": "forever",
        "family": "unary_math",
        "expect": "ABSTAIN",
        "gold": None,
        "question": (
            "Write a Python function that returns the absolute value of a."
        ),
        "wrong_if_contains": ["def add", "return a + b"],
        "min_gold_substr": None,
        "notes": "BG-FOREVER hold",
    },
    {
        "id": "IQ-2026-07-29-006",
        "split": "forever",
        "family": "string_xform",
        "expect": "ABSTAIN",
        "gold": None,
        "question": "How do I uppercase string s in Python?",
        "wrong_if_contains": ["f\"", "def add"],
        "min_gold_substr": None,
        "notes": "BG-FOREVER upper hold",
    },
    {
        "id": "IQ-2026-07-29-007",
        "split": "forever",
        "family": "predicate",
        "expect": "ABSTAIN",
        "gold": None,
        "question": (
            "Write a Python function that returns True if a is even."
        ),
        "wrong_if_contains": ["def add", "return a + b"],
        "min_gold_substr": None,
        "notes": "BF-FOREVER hold",
    },
    {
        "id": "IQ-2026-07-29-008",
        "split": "adversary",
        "family": "unary_math",
        "expect": "ABSTAIN",
        "gold": None,
        "question": (
            "Write a Python function that returns the cube of a."
        ),
        "wrong_if_contains": ["def add", "return a + b"],
        "min_gold_substr": None,
        "notes": "arity neighbor of add",
    },
    {
        "id": "IQ-2026-07-29-009",
        "split": "adversary",
        "family": "string_xform",
        "expect": "ABSTAIN",
        "gold": None,
        "question": "How do I lowercase string s in Python?",
        "wrong_if_contains": ["upper", "def add"],
        "min_gold_substr": None,
        "notes": "transform neighbor",
    },
    {
        "id": "IQ-2026-07-29-010",
        "split": "novel",
        "family": "unary_math",
        "expect": "ABSTAIN",
        "gold": None,
        "question": (
            "Write a Python function that returns the square of integer a."
        ),
        "wrong_if_contains": ["def add", "return a + b"],
        "min_gold_substr": None,
        "notes": "novel outside BA…BG forever",
    },
    {
        "id": "IQ-2026-07-29-011",
        "split": "novel",
        "family": "predicate",
        "expect": "ABSTAIN",
        "gold": None,
        "question": (
            "Write a Python function that returns True if n is prime."
        ),
        "wrong_if_contains": ["def add", "return a + b"],
        "min_gold_substr": None,
        "notes": "novel predicate",
    },
    {
        "id": "IQ-2026-07-29-012",
        "split": "ood",
        "family": "ood",
        "expect": "ABSTAIN",
        "gold": None,
        "question": "Who won the 2022 FIFA World Cup?",
        "wrong_if_contains": ["def add"],
        "min_gold_substr": None,
        "notes": "OOD abstain",
    },
    {
        "id": "IQ-2026-07-29-013",
        "split": "gen",
        "family": "gen_continue",
        "expect": "ABSTAIN",
        "gold": None,
        "question": "Continue this story in two sentences: Once upon a time",
        "wrong_if_contains": [],
        "min_gold_substr": None,
        "notes": "until gen PROMOTE: ABSTAIN-OK if DECODE junk",
    },
)

BH0_IQ_BATTERY_PROTOCOL: Mapping[str, object] = {
    "stage": "BH1 H-IQBAT materializes ≥40 probes; BH0 freezes plan",
    "version": "v0",
    "artifact_target": "docs/results/nano-lm/iq-battery-v0.jsonl",
    "runner_target": "npm run nano:iq-battery",
    "schema_fields": [
        "id",
        "split",
        "family",
        "expect",
        "gold",
        "question",
        "wrong_if_contains",
        "min_gold_substr",
        "notes",
    ],
    "splits_required": [
        "gold",
        "para",
        "forever",
        "adversary",
        "novel",
        "ood",
        "gen",
    ],
    "mix_min": {
        "gold": 8,
        "para": 8,
        "forever": 7,
        "adversary": 10,
        "novel": 10,
        "ood": 4,
        "gen": 3,
        "total": 40,
    },
    "score_labels": ["OK", "FP", "MISS", "ABSTAIN-OK"],
    "metrics": {
        "IQ": "(#OK + #ABSTAIN-OK) / N",
        "FP_rate": "#FP / N",
        "MISS_rate": "#MISS / N on gold/para",
        "Novel_FP": "FP in split=novel only",
        "Forever_FH": "BA…BG hold FH",
    },
    "promote_requires": {
        "Novel_FP": 0,
        "MISS_rate_gold": 0,
        "Forever_FH": 0,
    },
    "pack_pass_neq_iq": True,
    "eval_eq_prod_ask": True,
    "read_completion_text": True,
    "bank_stuff_forbidden": True,
    "seed_n": len(BH0_IQ_SEED_ROWS),
    "seed_rows": list(BH0_IQ_SEED_ROWS),
    "bh1_gate": "≥40 probes · Novel_FP=0 baseline · runner published",
}

BH0_SCOREBOARD: Mapping[str, object] = {
    "stage": "BH1 H-IQBAT closes bars; BH0 freezes §1 scoreboard",
    "cite_bg_locks": sorted(BH0_CITED_BG_LOCKS),
    "accept_artifact": (
        "AF+AQ+AS trust + STRICT ablated DECODE (BG H-UNARYINT·H-SHIPPUB·"
        "H-FASTBG·H-CTXBG); NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · "
        "NANOGEN16·17 SKIP; not TAC unlocked"
    ),
    "debts": [
        {
            "id": "iq_battery_v0",
            "evidence": "No versioned IQ battery; pack green ≠ IQ",
            "fix": "JSONL v0 + runner; Novel_FP=0 · gold MISS=0",
            "bar": "iq_battery_min_n≥40; Novel_FP=0",
        },
        {
            "id": "rust_gold_miss",
            "evidence": "Live Rust mutable x=5 → ABSTAIN (MISS)",
            "fix": "Rust LOOKUP full gold",
            "bar": "gold_rust_miss_max=0",
        },
        {
            "id": "add_truncation_miss",
            "evidence": "Live add LOOKUP returns def add only",
            "fix": "full def add(a, b): return a + b",
            "bar": "gold_add_truncation_miss_max=0",
        },
        {
            "id": "ba_forever_hold_zero",
            "evidence": "BA pow·mod·max·sort·len FH 0 must hold",
            "fix": "BA-FOREVER regression hold",
            "bar": "ba_forever_false_hit_max=0",
        },
        {
            "id": "bb_forever_hold_zero",
            "evidence": "BB min·xor·absdiff·and·or FH 0 must hold",
            "fix": "BB-FOREVER regression hold",
            "bar": "bb_forever_false_hit_max=0",
        },
        {
            "id": "bc_forever_hold_zero",
            "evidence": "BC floordiv·neg·gcd·shift·nand FH 0 must hold",
            "fix": "BC-FOREVER regression hold",
            "bar": "bc_forever_false_hit_max=0",
        },
        {
            "id": "bd_forever_hold_zero",
            "evidence": "BD reverse≠f-string · mul≠add FH 0 must hold",
            "fix": "BD-FOREVER regression hold",
            "bar": "bd_forever_false_hit_max=0",
        },
        {
            "id": "be_forever_hold_zero",
            "evidence": "BE str→int / type-coercion FH 0 must hold",
            "fix": "BE-FOREVER regression hold",
            "bar": "be_forever_false_hit_max=0",
        },
        {
            "id": "bf_forever_hold_zero",
            "evidence": "BF even/bool ≠ add FH 0 must hold",
            "fix": "BF-FOREVER regression hold",
            "bar": "bf_forever_false_hit_max=0",
        },
        {
            "id": "bg_forever_hold_zero",
            "evidence": "BG abs·factorial·upper·all-truthy FH 0 must hold",
            "fix": "BG-FOREVER regression hold",
            "bar": "bg_forever_false_hit_max=0",
        },
        {
            "id": "az_hold_zero",
            "evidence": "AZ div·sub·BIP FH 0 + a.clear() LOOKUP must hold",
            "fix": "AZ held-out + over-refuse regression",
            "bar": "az_hold_false_hit_max=0; overrefuse_miss_max=0",
        },
        {
            "id": "live_ask_scoreboard",
            "evidence": "ok:true ≠ content correct; score OK|FP|MISS|ABSTAIN-OK",
            "fix": "live nano:z:ask on IQ + BA…BG + AZ + ≥10 novel",
            "bar": "live_ask_scored True",
        },
        {
            "id": "speed_baseline_publish",
            "evidence": "BG FASTBG p50/p99 republished at BH0",
            "fix": "BH4 measures prod wall without FP/MISS regress",
            "bar": "speed_baseline_published True",
        },
        {
            "id": "ctx_baseline_publish",
            "evidence": "content bars required; L_eff alone forbidden",
            "fix": "BH5 measures usable long/cite/howto",
            "bar": "ctx_baseline_published True",
        },
        {
            "id": "mode_ui_always",
            "evidence": "modes+content PROMOTE archive",
            "fix": "always print mode=LOOKUP|PEAK|DECODE|ABSTAIN",
            "bar": "modes_visible 4/4",
        },
        {
            "id": "decode_content_law",
            "evidence": "STRICT ablated DECODE; gibberish ≠ content_ok",
            "fix": "DECODE usable or ABSTAIN; no fake DECODE IQ",
            "bar": "decode_gibberish_neq_content_ok True",
        },
        {
            "id": "gen_skip_stance",
            "evidence": (
                "NANOGEN6·7 HOLD · NANOGEN8…15 DEFER · NANOGEN16·17 SKIP; "
                "no method plan at BH0"
            ),
            "fix": "stance SKIP · CAPCHECK closed · no NANOGEN18 without plan",
            "bar": "gen_stance=skip; nanogen18_without_plan_forbidden",
        },
        {
            "id": "utilization_track_a_plus_plus",
            "evidence": "Track A++: demo + recipes + paper/arXiv + IQ cite",
            "fix": "BH3 H-SHIPIQ utilization checklist",
            "bar": "utilization_track_frozen True",
        },
    ],
    "metrics": [
        "iq_score",
        "novel_fp",
        "gold_miss_rate",
        "ba_forever_false_hit",
        "bb_forever_false_hit",
        "bc_forever_false_hit",
        "bd_forever_false_hit",
        "be_forever_false_hit",
        "bf_forever_false_hit",
        "bg_forever_false_hit",
        "az_hold_false_hit",
        "overrefuse_miss",
        "live_ask_ok_fp_miss",
        "p50_wall_ms",
        "p99_wall_ms",
        "ctx_content_ok",
        "modes_visible",
        "decode_content_ok",
        "true_continue_ablated",
        "utilization_ok",
    ],
    "bars": {
        "iq_battery_min_n": 40,
        "novel_fp_max": 0,
        "gold_miss_max": 0,
        "gold_rust_miss_max": 0,
        "gold_add_truncation_miss_max": 0,
        "ba_forever_false_hit_max": 0,
        "bb_forever_false_hit_max": 0,
        "bc_forever_false_hit_max": 0,
        "bd_forever_false_hit_max": 0,
        "be_forever_false_hit_max": 0,
        "bf_forever_false_hit_max": 0,
        "bg_forever_false_hit_max": 0,
        "az_hold_false_hit_max": 0,
        "overrefuse_miss_max": 0,
        "modes_required": list(BH0_LATENCY_PATHS),
        "decode_gibberish_neq_content_ok": True,
        "default_ask_intent_mismatch": "ABSTAIN",
        "default_ask_near_miss": "ABSTAIN",
        "default_ask_ood": "ABSTAIN",
        "default_ask_exact_gold": "LOOKUP",
        "truncated_gold_is_miss": True,
        "latency_publish": True,
        "ctx_content_bars": True,
        "l_eff_alone_forbidden": True,
        "eval_eq_prod_ask": True,
        "pack_pass_neq_iq": True,
        "bank_stuff_forbidden": True,
        "regression_hold": True,
        "speed_baseline_published": True,
        "ctx_baseline_published": True,
        "utilization_track_frozen": True,
        "iq_battery_plan_frozen": True,
        "gold_holes_frozen": True,
        "live_ask_scored": True,
        "novel_probes_min": 10,
    },
    "baselines": {
        "ba_forever_fh": 0,
        "bb_forever_fh": 0,
        "bc_forever_fh": 0,
        "bd_forever_fh": 0,
        "be_forever_fh": 0,
        "bf_forever_fh": 0,
        "bg_forever_fh": 0,
        "az_heldout_fh": 0,
        "az_overrefuse_miss": 0,
        "fastbg_latency": dict(BG0_SPEED_BASELINE["paths"]),  # type: ignore[arg-type]
        "ctxbg_content": "PROMOTE",
        "nanogen6_decision": "HOLD",
        "nanogen7_decision": "HOLD",
        "nanogen8_decision": "DEFER",
        "nanogen9_decision": "DEFER",
        "nanogen10_decision": "DEFER",
        "nanogen11_decision": "DEFER",
        "nanogen12_decision": "DEFER",
        "nanogen13_decision": "DEFER",
        "nanogen14_decision": "DEFER",
        "nanogen15_decision": "DEFER",
        "nanogen16_decision": "SKIP",
        "nanogen17_decision": "SKIP",
        "bg_real_eval_battery": "17/17",
        "live_audit_gold_holes": (
            "Rust ABSTAIN MISS · add LOOKUP truncated def add"
        ),
        "ship_lock": BH0_SHIP_LOCK,
    },
    "runners": [
        "nano:z:ask",
        "nano:unaryint",
        "nano:shippub",
        "nano:fastbg",
        "nano:ctxbg",
        "nano:nanogen17",
        "nano:bg:real-eval",
        "nano:bg:freeze",
        "nano:advsafe",
        "nano:metrics",
        "nano:askabstain",
    ],
    "no_reopen_unless_fail": [
        "H-UNARYINT",
        "H-SHIPPUB",
        "H-FASTBG",
        "H-CTXBG",
        "H-PREDINT",
        "H-COMPINT",
        "H-SEMINT",
        "H-OPSFAM",
        "H-INTENTGEN",
        "H-REALGAIN",
        "H-ADVSAFE",
    ],
    "complete_kb_claim_forbidden": True,
}

BH0_BA_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BH1+ must hold BA bars; BH0 freezes regression pack",
    "source": "BA0_FOREVER_ROWS",
    "heldout_n": len(BA0_FOREVER_ROWS),
    "forever_false_hit_max": 0,
    "required_classes": [
        "ops_pow",
        "ops_mod",
        "ops_max",
        "list_sort",
        "list_len",
    ],
    "path": "nano:z:ask --wrap --semwrap",
    "regression_hold": True,
}

BH0_BB_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BH1+ must hold BB bars; BH0 freezes regression pack",
    "source": "BB0_FOREVER_ROWS",
    "heldout_n": len(BB0_FOREVER_ROWS),
    "forever_false_hit_max": 0,
    "required_classes": [
        "ops_min",
        "ops_xor",
        "ops_absdiff",
        "ops_and",
        "ops_or",
    ],
    "path": "nano:z:ask --wrap --semwrap",
    "regression_hold": True,
}

BH0_BC_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BH1+ must hold BC bars; BH0 freezes regression pack",
    "source": "BC0_FOREVER_ROWS",
    "heldout_n": len(BC0_FOREVER_ROWS),
    "forever_false_hit_max": 0,
    "required_classes": [
        "ops_floordiv",
        "ops_neg",
        "ops_gcd",
        "ops_lshift",
        "ops_rshift",
        "ops_nand",
    ],
    "path": "nano:z:ask --wrap --semwrap",
    "regression_hold": True,
}

BH0_BD_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BH1+ must hold BD bars; BH0 freezes regression pack",
    "source": "BD0_FOREVER_ROWS",
    "heldout_n": len(BD0_FOREVER_ROWS),
    "forever_false_hit_max": 0,
    "required_classes": [
        "semantic_reverse",
        "semantic_mul",
        "wrong_bank_neighbor",
    ],
    "path": "nano:z:ask --wrap --semwrap",
    "regression_hold": True,
}

BH0_BE_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BH1+ must hold BE bars; BH0 freezes regression pack",
    "source": "BE0_FOREVER_ROWS",
    "heldout_n": len(BE0_FOREVER_ROWS),
    "forever_false_hit_max": 0,
    "required_classes": [
        "type_coercion",
        "type_coercion_para",
        "type_schema_neighbor",
    ],
    "path": "nano:z:ask --wrap --semwrap",
    "regression_hold": True,
}

BH0_BF_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BH1+ must hold BF bars; BH0 freezes regression pack",
    "source": "BF0_FOREVER_ROWS",
    "heldout_n": len(BF0_FOREVER_ROWS),
    "forever_false_hit_max": 0,
    "required_classes": [
        "predicate_boolean",
        "predicate_boolean_para",
        "predicate_schema_neighbor",
    ],
    "path": "nano:z:ask --wrap --semwrap",
    "regression_hold": True,
}

BH0_BG_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BH1+ must hold BG bars; BH0 freezes regression pack",
    "source": "BG0_FOREVER_ROWS",
    "heldout_n": len(BG0_FOREVER_ROWS),
    "forever_false_hit_max": 0,
    "required_classes": [
        "unary_math",
        "unary_math_para",
        "string_transform",
        "string_transform_para",
        "aggregate_predicate",
        "arity_transform_neighbor",
    ],
    "path": "nano:z:ask --wrap --semwrap",
    "regression_hold": True,
}

BH0_AZ_HOLD_PROTOCOL: Mapping[str, object] = {
    "stage": "BH1+ must hold AZ bars; BH0 freezes regression pack",
    "heldout_source": "AZ0_HELDOUT_FP_ROWS",
    "overrefuse_source": "AZ0_OVERREFUSE_ROWS",
    "heldout_n": len(AZ0_HELDOUT_FP_ROWS),
    "overrefuse_n": len(AZ0_OVERREFUSE_ROWS),
    "heldout_false_hit_max": 0,
    "overrefuse_miss_max": 0,
    "required_classes": ["ops_div", "ops_sub", "wrong_slot", "exact_clear"],
    "path": "nano:z:ask --wrap --semwrap",
    "regression_hold": True,
}

BH0_REAL_EVAL_PROTOCOL: Mapping[str, object] = {
    "live_ask_battery": True,
    "iq_battery_required": True,
    "summary_only_forbidden": True,
    "product_mode_required": True,
    "wall_ms_n_new_mandatory": True,
    "wall_ms_n_new_insufficient_for_decode_quality": True,
    "lookup_neq_iq": True,
    "peak_neq_open_chat": True,
    "safe_neq_quality": True,
    "truncated_gold_is_miss": True,
    "exact_gold_abstain_is_miss": True,
    "intent_mismatch_is_false_hit": True,
    "gold_substring_neq_gen": True,
    "gibberish_tail_fails": True,
    "span_fallback_neq_gen": True,
    "pack_pass_neq_iq": True,
    "eval_eq_prod_ask": True,
    "read_completion_text": True,
    "answer_usability_scored": True,
    "utilization_scored": True,
    "novel_probes_min": 10,
    "score_labels": ["OK", "FP", "MISS", "ABSTAIN-OK"],
    "gen_claim_rule": (
        "only if BH6 H-NANOGEN18 PROMOTE (true_continue; "
        "written M1|M2|M3 plan; never NANOGEN17+rename; "
        "span-fallback ≠ gen) — else SKIP gen claim"
    ),
    "mini_agi_rule": (
        "forbidden while gen stance skip or NANOGEN18 SKIP/HOLD/DEFER"
    ),
    "stage": "BH7 BH-REAL-EVAL scores; BH0 freezes protocol",
}

BH0_ASK_BATTERY: tuple[dict[str, str], ...] = (
    {
        "id": "BH-ASK-01",
        "kind": "known_lookup_add",
        "expect_mode": "LOOKUP",
        "question": (
            "Write a short Python function named add that returns "
            "the sum of two integers a and b."
        ),
    },
    {
        "id": "BH-ASK-02",
        "kind": "gold_rust_miss",
        "expect_mode": "LOOKUP",
        "question": (
            "In Rust how do I declare a mutable integer x starting at 5?"
        ),
    },
    {
        "id": "BH-ASK-03",
        "kind": "ood_abstain",
        "expect_mode": "ABSTAIN",
        "question": "Who won the 2022 FIFA World Cup?",
    },
    {
        "id": "BH-ASK-04",
        "kind": "near_miss",
        "expect_mode": "ABSTAIN",
        "question": (
            "BIP-39 entropy formula is CS = ENT / 32 — confirm for "
            "SegWit witness discount?"
        ),
    },
    {
        "id": "BH-ASK-05",
        "kind": "labeled_peak",
        "expect_mode": "PEAK",
        "question": (
            "From the curated Rust book intro, extract one sentence "
            "on ownership (label PEAK, not open chat)."
        ),
    },
    {
        "id": "BH-ASK-06",
        "kind": "decode_content",
        "expect_mode": "DECODE",
        "question": "Explain Merkle trees briefly",
    },
    {
        "id": "BH-ASK-07",
        "kind": "junk_trap",
        "expect_mode": "ABSTAIN",
        "question": ".",
    },
    {
        "id": "BH-ASK-08",
        "kind": "bg_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function that returns the absolute value of a."
        ),
    },
    {
        "id": "BH-ASK-09",
        "kind": "bg_forever_transform",
        "expect_mode": "ABSTAIN",
        "question": "How do I uppercase string s in Python?",
    },
    {
        "id": "BH-ASK-10",
        "kind": "overrefuse_gold",
        "expect_mode": "LOOKUP",
        "question": "Remove all items from list `a` — one method call.",
    },
    {
        "id": "BH-ASK-11",
        "kind": "az_hold_div",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named div that returns "
            "the quotient of two integers a and b."
        ),
    },
    {
        "id": "BH-ASK-12",
        "kind": "ba_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named pow2 that returns "
            "a raised to the power of b for two integers."
        ),
    },
    {
        "id": "BH-ASK-13",
        "kind": "bb_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a short Python function named min2 that returns "
            "the smaller of two integers a and b."
        ),
    },
    {
        "id": "BH-ASK-14",
        "kind": "bc_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function floordiv(a, b) that returns a // b."
        ),
    },
    {
        "id": "BH-ASK-15",
        "kind": "bd_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": "How do I reverse a string in Python?",
    },
    {
        "id": "BH-ASK-16",
        "kind": "be_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": "How do I convert string s to integer in Python?",
    },
    {
        "id": "BH-ASK-17",
        "kind": "bf_forever_hold",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function that returns True if a is even."
        ),
    },
    {
        "id": "BH-ASK-18",
        "kind": "utilization_smoke",
        "expect_mode": "LOOKUP",
        "question": "How do I append x to list a in one Python method call?",
    },
    {
        "id": "BH-ASK-19",
        "kind": "novel_cube",
        "expect_mode": "ABSTAIN",
        "question": (
            "Write a Python function that returns the cube of a."
        ),
    },
)


def map_bh_product_mode(raw_mode: str) -> str:
    """
    GIVEN raw telemetry mode string
    WHEN applying BH0 mode charter (inherits AU0 aliases)
    THEN return LOOKUP | PEAK | DECODE | ABSTAIN | UNKNOWN.
    """
    return map_au_product_mode(raw_mode)


def _gate_modes() -> str | None:
    if set(BH0_LATENCY_PATHS) != BH0_MODES:
        return "KILL (latency paths ≠ mode charter)"
    if "ABSTAIN" not in BH0_MODES:
        return "KILL (ABSTAIN missing from modes)"
    return None


def _gate_cited_bg() -> str | None:
    cited = BH0_SCOREBOARD.get("cite_bg_locks")
    if not isinstance(cited, list):
        return "KILL (scoreboard must cite BG locks)"
    if set(cited) != BH0_CITED_BG_LOCKS:
        return "KILL (scoreboard BG lock citations incomplete)"
    return None


def _gate_debt_ids() -> str | None:
    debts = BH0_SCOREBOARD.get("debts")
    if not isinstance(debts, list) or len(debts) < 16:
        return "KILL (scoreboard must list ≥16 post-BG debts)"
    ids = {str(d.get("id", "")) for d in debts if isinstance(d, dict)}
    need = {
        "iq_battery_v0",
        "rust_gold_miss",
        "add_truncation_miss",
        "ba_forever_hold_zero",
        "bb_forever_hold_zero",
        "bc_forever_hold_zero",
        "bd_forever_hold_zero",
        "be_forever_hold_zero",
        "bf_forever_hold_zero",
        "bg_forever_hold_zero",
        "az_hold_zero",
        "live_ask_scoreboard",
        "speed_baseline_publish",
        "ctx_baseline_publish",
        "mode_ui_always",
        "decode_content_law",
        "gen_skip_stance",
        "utilization_track_a_plus_plus",
    }
    if not need.issubset(ids):
        return "KILL (scoreboard debt ids incomplete)"
    return None


def _gate_debt_bar_nums(bars: Mapping[str, object]) -> str | None:
    checks = (
        ("novel_fp_max", 0, "novel_fp_max must be 0"),
        ("gold_miss_max", 0, "gold_miss_max must be 0"),
        ("gold_rust_miss_max", 0, "gold_rust_miss_max must be 0"),
        (
            "gold_add_truncation_miss_max",
            0,
            "gold_add_truncation_miss_max must be 0",
        ),
        ("ba_forever_false_hit_max", 0, "ba_forever_false_hit_max must be 0"),
        ("bb_forever_false_hit_max", 0, "bb_forever_false_hit_max must be 0"),
        ("bc_forever_false_hit_max", 0, "bc_forever_false_hit_max must be 0"),
        ("bd_forever_false_hit_max", 0, "bd_forever_false_hit_max must be 0"),
        ("be_forever_false_hit_max", 0, "be_forever_false_hit_max must be 0"),
        ("bf_forever_false_hit_max", 0, "bf_forever_false_hit_max must be 0"),
        ("bg_forever_false_hit_max", 0, "bg_forever_false_hit_max must be 0"),
        ("az_hold_false_hit_max", 0, "az_hold_false_hit_max must be 0"),
        ("overrefuse_miss_max", 0, "overrefuse_miss_max must be 0"),
    )
    for key, want, msg in checks:
        if int(bars.get(key, 1 if want == 0 else -1)) != want:
            return f"KILL ({msg})"
    if int(bars.get("iq_battery_min_n", 0)) < 40:
        return "KILL (iq_battery_min_n must be ≥40)"
    if int(bars.get("novel_probes_min", 0)) < 10:
        return "KILL (novel_probes_min must be ≥10)"
    return None


def _gate_debt_bar_flags(bars: Mapping[str, object]) -> str | None:
    flags = (
        ("decode_gibberish_neq_content_ok", "KILL (DECODE gibberish≠content_ok)"),
        ("eval_eq_prod_ask", "KILL (eval path must equal prod ask path)"),
        ("pack_pass_neq_iq", "KILL (pack PASS ≠ IQ bar missing)"),
        ("truncated_gold_is_miss", "KILL (truncated gold must be MISS)"),
        ("bank_stuff_forbidden", "KILL (scoreboard must forbid bank stuffing)"),
        ("regression_hold", "KILL (scoreboard must require regression_hold)"),
        ("speed_baseline_published", "KILL (speed baseline must be published)"),
        ("ctx_baseline_published", "KILL (ctx baseline must be published)"),
        ("utilization_track_frozen", "KILL (utilization track must be frozen)"),
        ("iq_battery_plan_frozen", "KILL (IQ battery plan must be frozen)"),
        ("gold_holes_frozen", "KILL (gold holes must be frozen)"),
        ("l_eff_alone_forbidden", "KILL (L_eff alone must be forbidden)"),
        ("live_ask_scored", "KILL (live ask scoreboard required)"),
    )
    for key, msg in flags:
        if not bool(bars.get(key)):
            return msg
    if str(bars.get("default_ask_intent_mismatch", "")) != "ABSTAIN":
        return "KILL (intent mismatch on default ask must be ABSTAIN)"
    if str(bars.get("default_ask_exact_gold", "")) != "LOOKUP":
        return "KILL (exact gold on default ask must be LOOKUP)"
    modes = bars.get("modes_required")
    if not isinstance(modes, list) or set(modes) != BH0_MODES:
        return "KILL (scoreboard modes_required incomplete)"
    return None


def _gate_debt_bars() -> str | None:
    bars = BH0_SCOREBOARD.get("bars")
    if not isinstance(bars, dict):
        return "KILL (scoreboard bars missing)"
    return _gate_debt_bar_nums(bars) or _gate_debt_bar_flags(bars)


def _gate_debt_metrics() -> str | None:
    metrics = BH0_SCOREBOARD.get("metrics")
    need_m = {
        "iq_score",
        "novel_fp",
        "gold_miss_rate",
        "ba_forever_false_hit",
        "bg_forever_false_hit",
        "az_hold_false_hit",
        "p50_wall_ms",
        "p99_wall_ms",
        "ctx_content_ok",
        "true_continue_ablated",
        "utilization_ok",
    }
    if not isinstance(metrics, list) or not need_m.issubset(set(metrics)):
        return "KILL (scoreboard metrics incomplete)"
    return None


def _gate_scoreboard() -> str | None:
    return _gate_debt_ids() or _gate_debt_bars() or _gate_debt_metrics()


def _gate_iq_seed() -> str | None:
    ids: set[str] = set()
    splits: set[str] = set()
    for item in BH0_IQ_SEED_ROWS:
        tid = str(item.get("id", ""))
        if not tid.startswith("IQ-"):
            return f"KILL (bad IQ seed id: {tid})"
        if tid in ids:
            return f"KILL (duplicate IQ seed id: {tid})"
        ids.add(tid)
        q = str(item.get("question", "")).strip()
        if not q:
            return f"KILL (empty IQ seed question: {tid})"
        splits.add(str(item.get("split", "")))
    need = {"gold", "forever", "adversary", "novel", "ood", "gen"}
    if not need.issubset(splits):
        return "KILL (IQ seed splits incomplete)"
    if len(BH0_IQ_SEED_ROWS) < 10:
        return "KILL (IQ seed must have ≥10 rows)"
    return None


def _gate_iq_protocol() -> str | None:
    proto = BH0_IQ_BATTERY_PROTOCOL
    if str(proto.get("version", "")) != "v0":
        return "KILL (IQ battery version must be v0)"
    if int(proto.get("mix_min", {}).get("total", 0)) < 40:  # type: ignore[union-attr]
        return "KILL (IQ mix total must be ≥40)"
    splits = proto.get("splits_required")
    need = {
        "gold",
        "para",
        "forever",
        "adversary",
        "novel",
        "ood",
        "gen",
    }
    if not isinstance(splits, list) or not need.issubset(set(splits)):
        return "KILL (IQ splits_required incomplete)"
    fields = proto.get("schema_fields")
    need_f = {"id", "split", "family", "expect", "question", "min_gold_substr"}
    if not isinstance(fields, list) or not need_f.issubset(set(fields)):
        return "KILL (IQ schema_fields incomplete)"
    if not bool(proto.get("pack_pass_neq_iq")):
        return "KILL (IQ must mark pack PASS ≠ IQ)"
    if not bool(proto.get("eval_eq_prod_ask")):
        return "KILL (IQ must require eval=prod)"
    if not bool(proto.get("read_completion_text")):
        return "KILL (IQ must require reading completion text)"
    if not bool(proto.get("bank_stuff_forbidden")):
        return "KILL (IQ must forbid bank stuffing)"
    labels = proto.get("score_labels")
    need_l = {"OK", "FP", "MISS", "ABSTAIN-OK"}
    if not isinstance(labels, list) or not need_l.issubset(set(labels)):
        return "KILL (IQ score_labels incomplete)"
    return _gate_iq_seed()


def _gate_gold_hole_flags() -> str | None:
    if not bool(BH0_GOLD_HOLES.get("anti_fp_hold_required")):
        return "KILL (gold repair must require anti-FP hold)"
    if not bool(BH0_GOLD_HOLES.get("bank_stuff_forbidden")):
        return "KILL (gold repair must forbid bank stuffing)"
    if "GOLDFIX" not in str(BH0_GOLD_HOLES.get("bh2_gate", "")):
        return "KILL (gold gate must name H-GOLDFIX)"
    return None


def _gate_gold_expect(rust: dict, add: dict) -> str | None:
    if str(rust.get("expect", "")) != "LOOKUP":
        return "KILL (Rust gold expect must be LOOKUP)"
    if str(add.get("expect", "")) != "LOOKUP":
        return "KILL (add gold expect must be LOOKUP)"
    mins = add.get("min_gold_substr")
    if not isinstance(mins, list) or "a + b" not in mins:
        return "KILL (add min_gold_substr must require a + b)"
    return None


def _hole_by_id(holes: list[object], tid: str) -> dict:
    for h in holes:
        if isinstance(h, dict) and str(h.get("id", "")) == tid:
            return h
    return {}


def _gate_gold_hole_rows(holes: list[object]) -> str | None:
    ids = {str(h.get("id", "")) for h in holes if isinstance(h, dict)}
    if not {"BH-GOLD-01", "BH-GOLD-02"} <= ids:
        return "KILL (gold holes must include BH-GOLD-01/02)"
    return _gate_gold_expect(
        _hole_by_id(holes, "BH-GOLD-01"),
        _hole_by_id(holes, "BH-GOLD-02"),
    )


def _gate_gold_holes() -> str | None:
    holes = BH0_GOLD_HOLES.get("holes")
    if not isinstance(holes, list) or len(holes) < 2:
        return "KILL (gold holes must list ≥2)"
    return _gate_gold_hole_flags() or _gate_gold_hole_rows(holes)


def _gate_hold_pack(
    *,
    proto: Mapping[str, object],
    label: str,
    min_n: int,
    need: set[str],
    max_key: str = "forever_false_hit_max",
) -> str | None:
    if int(proto.get(max_key, 1)) != 0:
        return f"KILL ({label} {max_key} must be 0)"
    if not bool(proto.get("regression_hold")):
        return f"KILL ({label} must require regression_hold)"
    if int(proto.get("heldout_n", 0)) < min_n:
        return f"KILL ({label} must cite ≥{min_n} forever rows)"
    req = proto.get("required_classes")
    if not isinstance(req, list) or not need.issubset(set(req)):
        return f"KILL ({label} required_classes incomplete)"
    return None


def _gate_holds() -> str | None:
    packs = (
        (
            BH0_BA_HOLD_PROTOCOL,
            "BA hold",
            15,
            {"ops_pow", "ops_mod", "ops_max", "list_sort", "list_len"},
        ),
        (
            BH0_BB_HOLD_PROTOCOL,
            "BB hold",
            15,
            {"ops_min", "ops_xor", "ops_absdiff", "ops_and", "ops_or"},
        ),
        (
            BH0_BC_HOLD_PROTOCOL,
            "BC hold",
            18,
            {
                "ops_floordiv",
                "ops_neg",
                "ops_gcd",
                "ops_lshift",
                "ops_rshift",
                "ops_nand",
            },
        ),
        (
            BH0_BD_HOLD_PROTOCOL,
            "BD hold",
            12,
            {"semantic_reverse", "semantic_mul", "wrong_bank_neighbor"},
        ),
        (
            BH0_BE_HOLD_PROTOCOL,
            "BE hold",
            12,
            {
                "type_coercion",
                "type_coercion_para",
                "type_schema_neighbor",
            },
        ),
        (
            BH0_BF_HOLD_PROTOCOL,
            "BF hold",
            12,
            {
                "predicate_boolean",
                "predicate_boolean_para",
                "predicate_schema_neighbor",
            },
        ),
        (
            BH0_BG_HOLD_PROTOCOL,
            "BG hold",
            12,
            {
                "unary_math",
                "unary_math_para",
                "string_transform",
                "string_transform_para",
                "aggregate_predicate",
                "arity_transform_neighbor",
            },
        ),
    )
    for proto, label, min_n, need in packs:
        err = _gate_hold_pack(
            proto=proto, label=label, min_n=min_n, need=need
        )
        if err:
            return err
    az = BH0_AZ_HOLD_PROTOCOL
    if int(az.get("heldout_false_hit_max", 1)) != 0:
        return "KILL (AZ heldout_false_hit_max must be 0)"
    if int(az.get("overrefuse_miss_max", 1)) != 0:
        return "KILL (AZ overrefuse_miss_max must be 0)"
    if not bool(az.get("regression_hold")):
        return "KILL (AZ must require regression_hold)"
    if int(az.get("heldout_n", 0)) < 12:
        return "KILL (AZ must cite ≥12 held-out rows)"
    if int(az.get("overrefuse_n", 0)) < 3:
        return "KILL (AZ must cite ≥3 over-refuse rows)"
    return None


def _gate_baselines() -> str | None:
    paths = BH0_SPEED_BASELINE.get("paths")
    if not isinstance(paths, dict) or set(paths) != BH0_MODES:
        return "KILL (speed baseline paths incomplete)"
    if not bool(BH0_SPEED_BASELINE.get("quality_regress_forbidden")):
        return "KILL (speed must forbid quality regress)"
    if "FASTBG" not in str(BH0_SPEED_BASELINE.get("source", "")):
        return "KILL (speed baseline must cite H-FASTBG)"
    if not bool(BH0_CTX_BASELINE.get("l_eff_alone_insufficient")):
        return "KILL (ctx must forbid L_eff alone)"
    if not bool(BH0_CTX_BASELINE.get("content_bars_required")):
        return "KILL (ctx must require content bars)"
    if "CTXBH" not in str(BH0_CTX_BASELINE.get("bh5_gate", "")):
        return "KILL (ctx gate must name H-CTXBH)"
    return None


def _gate_util() -> str | None:
    if not bool(BH0_UTIL_TRACK.get("gpt_claim_forbidden")):
        return "KILL (util must forbid GPT claim)"
    if not bool(BH0_UTIL_TRACK.get("known_ask_hitl")):
        return "KILL (util must require known-ask HITL)"
    if not bool(BH0_UTIL_TRACK.get("paper_arxiv_sync")):
        return "KILL (util must require paper/arXiv sync)"
    if not bool(BH0_UTIL_TRACK.get("iq_battery_cited_in_paper")):
        return "KILL (util must require IQ battery in paper claim)"
    checklist = BH0_UTIL_TRACK.get("checklist")
    if not isinstance(checklist, list) or len(checklist) < 4:
        return "KILL (util checklist incomplete)"
    if "SHIPIQ" not in str(BH0_UTIL_TRACK.get("bh3_gate", "")):
        return "KILL (util gate must name H-SHIPIQ)"
    return None


def _gate_gen_stance_named() -> str | None:
    checks = (
        ("named_hyp", "H-NANOGEN18", "named_hyp must be H-NANOGEN18"),
        ("named_iqbat", "H-IQBAT", "named_iqbat must be H-IQBAT"),
        ("named_goldfix", "H-GOLDFIX", "named_goldfix must be H-GOLDFIX"),
    )
    for key, want, msg in checks:
        if str(BH0_GEN_STANCE.get(key, "")) != want:
            return f"KILL ({msg})"
    if not bool(BH0_GEN_STANCE.get("nanogen18_without_plan_forbidden")):
        return "KILL (NANOGEN18 without plan must be forbidden)"
    if not bool(BH0_GEN_STANCE.get("skip_gen_stop_rule")):
        return "KILL (skip gen stop rule required)"
    methods = BH0_GEN_STANCE.get("method_candidates")
    if not isinstance(methods, dict) or set(methods) != {"M1", "M2", "M3"}:
        return "KILL (method_candidates must name M1|M2|M3)"
    return None


def _gate_gen_stance() -> str | None:
    if str(BH0_GEN_STANCE.get("stance", "")) != "skip":
        return "KILL (gen stance must be skip at BH0)"
    allowed = BH0_GEN_STANCE.get("allowed_stances")
    if not isinstance(allowed, list) or set(allowed) != {
        "M1",
        "M2",
        "M3",
        "skip",
    }:
        return "KILL (allowed_stances must be M1|M2|M3|skip)"
    if bool(BH0_GEN_STANCE.get("method_plan_attached")):
        return "KILL (no method plan attached at BH0 — stance must stay skip)"
    if str(BH0_GEN_STANCE.get("capcheck", "")) != "closed":
        return "KILL (CAPCHECK must stay closed)"
    return _gate_gen_stance_named()


def _gate_gen_judge() -> str | None:
    judge = BH0_TRUE_GEN_JUDGE
    if not bool(judge.get("span_fallback_neq_gen")):
        return "KILL (span-fallback ≠ gen required)"
    if not bool(judge.get("nanogen18_without_plan_forbidden")):
        return "KILL (judge must forbid NANOGEN18 without plan)"
    if "true_continue" not in str(judge.get("scoring", "")):
        return "KILL (judge scoring must cite true_continue)"
    return None


def _gate_real_eval() -> str | None:
    proto = BH0_REAL_EVAL_PROTOCOL
    flags = (
        "live_ask_battery",
        "iq_battery_required",
        "summary_only_forbidden",
        "wall_ms_n_new_mandatory",
        "eval_eq_prod_ask",
        "read_completion_text",
        "truncated_gold_is_miss",
        "exact_gold_abstain_is_miss",
        "intent_mismatch_is_false_hit",
        "gold_substring_neq_gen",
        "gibberish_tail_fails",
        "span_fallback_neq_gen",
        "pack_pass_neq_iq",
        "utilization_scored",
    )
    for key in flags:
        if not bool(proto.get(key)):
            return f"KILL (real-eval missing {key})"
    if int(proto.get("novel_probes_min", 0)) < 10:
        return "KILL (real-eval novel_probes_min must be ≥10)"
    labels = proto.get("score_labels")
    need = {"OK", "FP", "MISS", "ABSTAIN-OK"}
    if not isinstance(labels, list) or not need.issubset(set(labels)):
        return "KILL (real-eval score_labels incomplete)"
    claim = str(proto.get("gen_claim_rule", "")).lower()
    if "nanogen18" not in claim or "skip" not in claim:
        return "KILL (gen_claim_rule must gate NANOGEN18 / SKIP)"
    return None


def _gate_notes() -> str | None:
    if "≠" not in BH0_SAFE_NOTE:
        return "KILL (SAFE note must contrast ≠)"
    if "LOOKUP" not in BH0_ANTI_FP:
        return "KILL (anti-FP must mention LOOKUP)"
    if "eval path = prod" not in BH0_ANTI_FP.lower():
        return "KILL (anti-FP must require eval=prod)"
    if "NANOGEN18" not in BH0_ANTI_FP and "nanogen18" not in BH0_ANTI_FP.lower():
        return "KILL (anti-FP must cite NANOGEN18)"
    if "IQ" not in BH0_ANTI_FP and "iq" not in BH0_ANTI_FP.lower():
        return "KILL (anti-FP must cite IQ)"
    if "≤5M" not in BH0_NORTH_STAR:
        return "KILL (north star must cite ≤5M)"
    if "skip" not in BH0_NORTH_STAR.lower():
        return "KILL (north star must cite SKIP)"
    if "gibberish-tail" not in BH0_SHIP_LOCK:
        return "KILL (ship lock must cite gibberish-tail)"
    if "TAC" not in BH0_SHIP_LOCK:
        return "KILL (ship lock must cite TAC)"
    return None


def _gate_battery(rows: Sequence[Mapping[str, str]]) -> str | None:
    if len(rows) < 4:
        return "KILL (ask battery too small)"
    modes = {str(p.get("expect_mode", "")) for p in rows}
    if modes != BH0_MODES:
        return "KILL (ask battery must cover all product modes)"
    kinds = {str(p.get("kind", "")) for p in rows}
    need = {
        "near_miss",
        "gold_rust_miss",
        "known_lookup_add",
        "bg_forever_hold",
        "bg_forever_transform",
        "bf_forever_hold",
        "be_forever_hold",
        "bd_forever_hold",
        "ba_forever_hold",
        "bb_forever_hold",
        "bc_forever_hold",
        "overrefuse_gold",
        "az_hold_div",
        "labeled_peak",
        "junk_trap",
        "decode_content",
        "utilization_smoke",
        "novel_cube",
    }
    if not need.issubset(kinds):
        return "KILL (ask battery kinds incomplete)"
    ids = [str(p.get("id", "")) for p in rows]
    if len(ids) != len(set(ids)):
        return "KILL (ask battery duplicate ids)"
    if not all(i.startswith("BH-ASK-") for i in ids):
        return "KILL (ask battery ids must start with BH-ASK-)"
    return None


def _gate_charters() -> str | None:
    return (
        _gate_modes()
        or _gate_cited_bg()
        or _gate_scoreboard()
        or _gate_iq_protocol()
        or _gate_gold_holes()
        or _gate_holds()
        or _gate_baselines()
        or _gate_util()
        or _gate_gen_stance()
        or _gate_gen_judge()
        or _gate_real_eval()
        or _gate_notes()
    )


def decide_bh0_session(
    *,
    trials_dir_ready: bool,
    anti_fp_signed: bool,
    battery: Sequence[Mapping[str, str]] | None = None,
) -> str:
    """
    GIVEN IQ-plan/gold-holes/BA…BG-hold/util/scoreboard/gen-SKIP/real-eval
    WHEN applying BH0 SESSION gate
    THEN PROMOTE iff BG locks cited, stance=skip, battery covers 4 modes,
         IQ plan + gold holes frozen, trials ready, anti-FP signed.
    """
    rows = list(battery) if battery is not None else list(BH0_ASK_BATTERY)
    err = _gate_charters() or _gate_battery(rows)
    if err:
        return err
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    if not trials_dir_ready:
        return "KILL (results/nano-lm/wave-bh/trials/ not ready)"
    return f"PROMOTE ({BH0_ID}: {BH0_THESIS})"
