# nano_lm — TinyStories student + teacher track

Isolated Python/PyTorch research track (not part of the C++ EvoGen domain).

## Champion tip-stack (parked)

Protocol: train **H-CURL**, decode **H-EARLY** (speed) or **H-POOL** (quality@wall).  
Card: [`docs/results/nano-lm/champion-card.md`](../docs/results/nano-lm/champion-card.md).  
Agenda: [`docs/NANO-STUDENT-AGENDA.md`](../docs/NANO-STUDENT-AGENDA.md).

## Setup

```bash
python3 -m venv nano_lm/.venv
source nano_lm/.venv/bin/activate
pip install -r nano_lm/requirements.txt
```

## Phase-10 lab (AR / BoN / MAE)

```bash
npm run nano:lab          # GPU-heavy + live charts
npm run nano:lab:smoke
npm run nano:lab:bench
npm run nano:test
```

## Champion matrix + tips

```bash
npm run nano:matrix && npm run nano:matrix:report
npm run nano:cur && npm run nano:cur:report
npm run nano:curl && npm run nano:curl:report
npm run nano:dec
npm run nano:deck && npm run nano:deck:report
npm run nano:deckl && npm run nano:deckl:report
npm run nano:pool && npm run nano:pool:report
npm run nano:early && npm run nano:early:report
npm run nano:ear2 && npm run nano:ear2:report
npm run nano:bud && npm run nano:bud:report
npm run nano:spec
```

## Formal (fit≠eval, 3 seeds)

```bash
npm run nano:formal:cur && npm run nano:formal:cur:report
npm run nano:formal:curl && npm run nano:formal:curl:report
npm run nano:formal:hdec && npm run nano:formal:hdec:report
npm run nano:formal:hdeck && npm run nano:formal:hdeck:report
npm run nano:formal:hdeckl && npm run nano:formal:hdeckl:report
npm run nano:formal:hpool && npm run nano:formal:hpool:report
npm run nano:formal:hearly && npm run nano:formal:hearly:report
npm run nano:formal:hear2 && npm run nano:formal:hear2:report
npm run nano:formal:hbud && npm run nano:formal:hbud:report
```

KILL / non-champion markdown: [`docs/results/nano-lm/archive/`](../docs/results/nano-lm/archive/).
