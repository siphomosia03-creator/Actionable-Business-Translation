# NEXUSLEND CHURN INTERVENTION PLAN

## Problem

The churn model identifies customers who may be at increased risk of leaving. Financial strain, debt burden, operational disruption and support needs should be treated as signals for **customer assistance**, not as reasons to restrict access to services.

The analysis therefore focuses on interventions that can reduce avoidable churn while improving customer inclusion.

## Solution

The recommended approach is to provide targeted, supportive interventions:

1. **Load-Shedding Support Package**
2. **Fee Waiver for High-Strain**
3. **Payment Plan Assistance**

These interventions are designed around customer support rather than additional financial pressure.

## ROI

### Recommended intervention

**Payment Plan Assistance**

- Investment: R150,000
- Customers potentially retained: 285
- Estimated customer lifetime value: R6,800
- Gross value: R1,938,000
- Net value: R1,788,000
- Intervention ROI: 1192.0%

### Portfolio impact

| Intervention | Investment | Customers Saved | Gross Value | Net Value | ROI |
|---|---:|---:|---:|---:|---:|
| Load-Shedding Support Package | R240,000 | 410 | R2,542,000 | R2,302,000 | 959.2% |
| Fee Waiver for High-Strain | R185,000 | 320 | R2,080,000 | R1,895,000 | 1024.3% |
| Payment Plan Assistance | R150,000 | 285 | R1,938,000 | R1,788,000 | 1192.0% |

**Projected ROI: R5,985,000 net value across the three interventions, representing 1040.9% portfolio ROI.**

Per CFO: 'Every 1% churn reduction = R420k saved'

## Inclusion Impact

The objective is not simply to reduce churn. The objective is to reduce avoidable churn while ensuring that financially vulnerable customers receive appropriate support.

High-strain customers should receive options such as:

- Affordable payment plans
- Temporary fee relief
- Load-shedding support
- Human-assisted financial guidance
- Clear information about available alternatives

Interventions must provide support and choice. High-strain customers must not be targeted with predatory credit, refinancing, or fee-generating offers.

## Ethical Guardrails

**Do NOT target high-strain customers with predatory offers**

Model predictions must never be used as the sole basis for denying customers services, increasing fees, reducing access to credit, or offering unsuitable financial products.

Human review is required for high-risk decisions.

## Regional Insights

The accompanying `churn_heatmap.png` shows predicted churn probability by region and financial-strain quartile.

Regional differences should be investigated for service-access, infrastructure and economic factors rather than interpreted as evidence that customers in a particular region are inherently higher risk.

## Monitoring Triggers

- Retrain if township recall drops >10% from its approved baseline.
- Review model fairness across regions monthly.
- Monitor intervention uptake in underserved regions.
- Monitor whether interventions reduce churn without increasing customer financial strain.
- Investigate material increases in false negatives for township customers.
- Escalate unexpected regional performance differences for human review.

## Next Steps

1. Pilot the highest-ROI supportive intervention.
2. Measure actual retention against the projected customer savings.
3. Monitor inclusion and fairness metrics alongside financial outcomes.
4. Review customer feedback before scaling.
5. Retrain and revalidate the model when monitoring thresholds are breached.

## Stakeholder Principle

The central business objective is sustainable customer retention.

Financial performance and customer wellbeing must be considered together. A profitable intervention that increases financial harm is not an acceptable outcome.

**Data science should serve people — not just profit.**
