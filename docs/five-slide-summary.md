# Five-slide summary deck content

## 1 PROBLEM UNDERSTANDING AND OBJECTIVE
Customer signals are fragmented across support, billing, satisfaction, and product usage. Teams intervene after escalation. Objective: continuously correlate those signals into a ranked, explainable queue of accounts needing attention.

## 2 SOLUTION ARCHITECTURE AND DESIGN FLOW
`Customer JSON / CSV-ready records → FastAPI validation → Explainable weighted signal engine → Optional Groq rationale/action → Risk-ranked API response → Next.js operations dashboard`

The deterministic layer remains available when no API key is configured; Groq enriches, but does not decide, the risk score.

## 3 IMPLEMENTATION HIGHLIGHTS
- FastAPI + Pydantic input validation; one-click sample analysis and custom JSON testing.
- Signals: low CSAT, support spike, usage decline, payment failure, negative/cancellation language.
- Score is capped at 100 and bucketed into Healthy, Watch, High, and Critical.
- Dashboard shows queue, filters, revenue at risk, score ring, evidence, rationale, and recommended action.

## 4 CHALLENGES AND LEARNINGS
The key trade-off is speed versus model sophistication. A transparent baseline makes the prototype dependable and easy to audit, while LLM enrichment improves human readability. Production calibration should use historical churn/save labels, and integrations should add identity resolution, deduplication, and monitoring for drift.

## 5 DEMO SUMMARY AND NEXT STEPS
Demo flow: open dashboard → review critical queue → inspect Northstar Health evidence → paste a custom record → run analysis. Next: connect CRM and billing APIs, add batch scheduling, sentiment/embedding evaluation, intervention tracking, and role-based access.

