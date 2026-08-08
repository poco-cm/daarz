# Civilization Lifecycle Phases

This is the official Genesis-to-Renewal sequence from the founding specification. No phase transition is active until its test is passed and recorded in `civilization/milestones/`.

| Phase | Entry condition | Exit condition | First required institutions | Greatest risk | Transition test |
|---|---|---|---|---|---|
| Genesis | Empty repository plus approved specification | Full scaffold and every manifest written | None; definition only | Writing code before meaning | `SCAFFOLD_REPORT.md` matches the specification |
| Birth | Scaffold fixed and approved | First real agent operates in `runtime/` | `constitution/`, `factory/`, `runtime/`, `safety/` | Activating without a safety kill switch | Run one agent and stop it manually |
| Formation | One living agent | First three institutions use real logic and `protocols/` | `population/`, `protocols/`, `governance/` | Repeating fixed-function behavior | Zero static `return True` in active institutions |
| Education | Three or more institutions operate | First measurable learning curriculum exists | `universities/`, `learning/`, `evaluation/` | Learning without evaluation | Document before/after performance |
| Expansion | Learning is proven | First bounded internal economy operates | `economy/`, `contracts/`, `orchestration/` | Ungoverned growth | Every new resource has a signed contract |
| Maturity | Economy operates | First complete governance decision succeeds | Full `governance/`, `archive/` | Formal governance without real authority | A real decision is rejected or changed |
| Adaptation | Governance is effective | Crisis simulation is survived without breaking constitution | `defense/`, `simulations/`, `security/` | Breaking the constitution for necessity | Full crisis scenario and defense report |
| Evolution | Crisis is survived | First architectural change completes the pipeline | `research/`, `knowledge/` | Evolution without archival identity | `archive/provenance/` records every change |
| Renewal | Evolution is documented | Continuity is proven through a new generation | `continuity/`, `scientists/` | Loss of continuity without a human operator | Full restoration from archive without momentary human intervention |
