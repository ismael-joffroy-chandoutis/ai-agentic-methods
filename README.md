**English** · [Français](README.fr.md)

# Agentic methods

Reusable methods for building AI agent systems that produce readable deliverables.
No client data here: these are methods, not case studies.

## Methods

- **[GEO / AEO audit](geo-aeo-audit-method.md)**: measuring and improving a brand's
  visibility in AI answers (ChatGPT, Gemini, Perplexity, Google AI Overviews).
- **[Agentic reporting](agentic-reporting-method.md)**: structuring a monthly report
  that produces itself from documents that get dropped in.
- **[Multi-agent QC harness](multi-agent-qc-harness.md)**: adversarially verifying
  what agents produce, with a catch-and-correct controller after every write step.

## Nine lessons from one night of agentic work

An agent-run document service, taken from prototype to a rehearsed deployment in a
single working night: a regulatory document check validated blind against three
passes of human review, a mail-only correction loop tested live, a server
deployment rehearsed in a container before buying the machine, the same task run on
four different reasoning engines, and a retrospective cost measurement of the whole
engagement. Anonymised throughout — what generalises is the method, never the case.

Lesson pages are written in French.

1. **[Blind backtest](lessons/01-blind-backtest.md)** — validating an automated
   document check against human corrections it never saw: 71 % strict recall,
   99.2 % precision, and why the misses are never regulatory.
2. **[Source anchoring](lessons/02-source-anchoring.md)** — a generated report cited
   a source that was never submitted, and the output gate did not see it. The
   closed-list check that shuts that door.
3. **[Transparent correction loop](lessons/03-transparent-correction-loop.md)** —
   announcing a correction is not proving it: block-level diff between passes,
   refusing to ship when the targeted area did not move, and answering honestly
   when the request was already satisfied.
4. **[Email as the only interface](lessons/04-email-as-only-interface.md)** — no
   portal, no app: state machine, SQLite as the ledger, pass ceiling, and the
   recipient guard that replies to the real sender rather than to a config file.
5. **[Rehearsing deployment in a container](lessons/05-rehearse-deployment-in-container.md)**
   — real systemd as PID 1, eight blocking gaps found before spending a euro on
   hosting, plus a lock that promised more than it held.
6. **[Engine agnosticism](lessons/06-engine-agnosticism.md)** — the same task on
   four engines from four families, one of them a local open-weights model: what it
   proves, what it does not, and why production calls the HTTP API rather than the
   agentic CLI (a factor of ~300 on cost).
7. **[French open data for regulatory checks](lessons/07-open-data-regulatory.md)** —
   the postal-address geocoding trap that silently answers correctly about the wrong
   building, self-updating legal references, and the three fields of a national
   database you must not trust.
8. **[An incomplete reference, and calibrated uncertainty](lessons/08-signal-uncertainty.md)**
   — half a composite rule is more dangerous than no rule, and a check that flags
   its own uncertainty makes the gap fixable in a day.
9. **[Retrospective cost of an agent engagement](lessons/09-retrospective-cost.md)** —
   measuring machine and human time separately: 84 machine-hours against 8 hours of
   human presence, half the bill being context re-reads, and file size telling you
   nothing about cost.

## Generic code

Five reusable, deterministic checks in [`code/`](code/) — output gate, source
anchoring, block diff, numeric grounding, findings merge. None of them calls a
model: same input, same verdict, every time.

## License

Prose: CC BY-SA 4.0 ([LICENSE](LICENSE)). Code: MIT ([LICENSE-CODE](LICENSE-CODE)).
By Ismaël Joffroy Chandoutis.
