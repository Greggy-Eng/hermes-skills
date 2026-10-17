# PRD: 3PL_flow

**Author:** Greg + Greggy · **Date:** 2026-10-16 · **Status:** Draft (v0.3 — succinctness pass)
**Stakeholders:** Finance/AR owner, NetSuite admin, automation/ops
**Work statement:** "We need to build a new workflow for invoice adjustment to zero the invoice out and modify an existing workflow that is adjusting the receiving PO process."

## 1. Problem
For 3PL-fulfilled customers, NetSuite invoice and receiving-PO processing still requires manual correction: invoices get zeroed by hand after generation, receipts get adjusted by hand — driving manual journal entries and reconciliation work at close. Both flows must run automatically, gated per customer, with pre-adjustment values preserved (PDF archive + field snapshot).

## 2. Goals
- G1: Invoice zero-out fully automated as the final step of invoice generation — zero manual JEs per invoice.
- G2: Receiving-PO 3PL adjustments run automatically on the same gate.
- G3: Zeroed values never lost — PDF to Google Drive, originals to UDFs.
- G4: Every run reconstructible from NetSuite logs.

## 3. Non-goals *(inferred — confirm)*
- NG1: Human approval in the happy path (fully automated per Greg; FR9 exception review remains in scope).
- NG2: 3PL billing/transmission upstream of NetSuite.
- NG3: Invoice-generation logic itself — zero-out runs after generation.
- NG4: Replacing NetSuite standard AR/procurement functionality.

## 4. Users & Jobs
| Persona | Job | Today | Pain |
|---|---|---|---|
| Automation (primary) | gate → preserve → zero/adjust → log, unattended | manual JEs + hand-saved PDFs | High |
| AR/AP staff | clear refused runs | full manual adjustment | Med |
| Controller / audit | reconstruct any run from logs | memos + emailed PDFs | Med |
| Customer ops | confirm customer PDF on Drive | manual save | Low |

## 5. Proposed Solution
Two NetSuite workflows, both gated on a new customer-record 3PL checkbox (FR6) and logged per FR8.
1. **NEW — Invoice zero-out:** final step of invoice generation for gated customers — PDF → Drive, snapshot values to UDFs, zero, log. Refusals leave the invoice untouched (FR9).
2. **MODIFY — Receiving-PO:** existing workflow gains gate + logging; its per-receipt adjustment behavior is TBD-2.

## 6. Requirements
### Functional
- FR1: Zero-out runs automatically as the final step of invoice generation on invoices of 3PL-flagged customers; no action otherwise.
- FR2: Before any modification, a PDF of the invoice at full values saves to the customer's Google Drive folder.
- FR3: Every value about to be zeroed is copied to a designated UDF first; post-run the invoice reads zero, UDFs hold originals.
- FR4: Zero-out brings invoice amounts to exactly 0.00 *(mechanism + GL offset → TBD-3)*.
- FR5: Runs are idempotent per invoice — no duplicate PDF, zeroing, or records on re-execution.
- FR6: A 3PL checkbox field on the customer profile, editable by authorized staff, gates both workflows.
- FR7: Receiving-PO workflow fires its 3PL adjustments only for flagged customers *(behavior → TBD-2)*.
- FR8: Every execution of either workflow logs in NetSuite: workflow, record ID, customer, trigger, timestamp, fields changed before→after, outcome.
- FR9: Guardrail hit (threshold, closed period, Drive failure, missing UDF map) stops before modification; logged refused with reason.
- FR10: Daily digest — invoices zeroed (PDF links), receipts adjusted, refused runs.

### Non-functional
- NFR1: Postings land in the correct accounting period per close policy (Q4).
- NFR2: Zero-out is atomic — PDF, snapshot, and zeroing all persist or none do; Drive failure policy → Q6.
- NFR3: Automation runs under a dedicated least-privilege integration role, attributable in FR8 logs.

### TBD stubs
- TBD-2: FR7 adjustment behavior ← Q2a.
- TBD-3: FR4 mechanism + GL offset ← Q3.
- TBD-4: source field → UDF map ← Q5.

## 7. Success Metrics
| Metric | Baseline | Target | Timeframe | Source |
|---|---|---|---|---|
| Manual JEs/period, 3PL customers | TBD — 2 periods pre-launch | −90% | 60d post-launch | NetSuite JE search |
| Invoices manually touched at close | TBD | 0 | 60d post-launch | AR close checklist |
| Auto-zero runs with PDF+UDF integrity | n/a | 100% | ongoing | FR8 log vs Drive audit |
| Post-run correction rate | n/a | <1% | ongoing | FR8 log |

## 8. Constraints & Dependencies
- NetSuite (prod 11274532 — *confirm*) hosts workflows, checkbox, UDFs, logs.
- Google Drive API access + folder provisioning (Q7).
- UDF provisioning precedes FR3; close calendar bounds NFR1; GL offset bounds TBD-3.
- Sandbox required to prove FR5/NFR2 before prod (Q8).

## 9. Assumptions
- A1: "Invoice" = customer invoice (AR) — implied by customer gate + Drive folder; supersedes v0.1 vendor-bill reading.
- A2: Zeroing is field-level with GL offset (Q3), not a customer-facing credit memo.
- A3: "Logged in the system" = queryable inside NetSuite; storage mechanism free.
- A4: The PDF is the audit artifact — the invoice as billed, pre-zero.
- A5: The receiving-PO workflow is an existing editable NetSuite automation.
- A6: Drive uses one folder per customer, deterministic mapping.

## 10. Open Questions
- Q2a: What does the receiving-PO workflow adjust on the receipt? *(Greg)*
- Q3: Zero mechanism + GL offset accounts — posting a zeroed invoice without offset breaks AR reconciliation. *(controller)*
- Q4: Closed-period / back-dating policy. *(controller)*
- Q5: UDF field map (source → target). *(NetSuite admin)*
- Q6: Drive save failure — refuse-and-retry or zero-with-alert? Default: refuse (NFR2). *(finance)*
- Q7: Drive folder provisioning and naming. *(ops)*
- Q8: Sandbox with data copy? *(NetSuite admin)*

## 11. Milestones *(recommended — no fixed date)*
| Phase | Scope | Exit |
|---|---|---|
| M1 — Decisions & provisioning | Q2a/Q3/Q5 answered; checkbox + UDFs + Drive map; JE baseline | TBD stubs clear; sandbox ready |
| M2 — Invoice zero-out | FR1–FR10, NFR1–3, sandbox → prod | 7 straight days: all gated invoices zeroed with PDF+snapshot, <1% corrections |
| M3 — Receiving-PO modify | FR7 | Two close cycles, zero manual JEs on gated receipts |

M2 ships first — it's fully specced; pull M3 earlier if Q2a shows the PO change is the JE root cause.
