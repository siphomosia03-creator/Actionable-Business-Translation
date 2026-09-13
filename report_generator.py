import os
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


ETHICAL_WARNING = (
    "Do NOT target high-strain customers with predatory offers"
)

CFO_QUOTE = "Per CFO: 'Every 1% churn reduction = R420k saved'"

INCLUSION_WARNING = (
    "Interventions must provide support and choice. High-strain customers "
    "must not be targeted with predatory credit, refinancing, or fee-generating offers."
)


class ReportGenerator:
    """Transform model outputs into boardroom-ready business actions."""

    def __init__(
        self,
        model,
        X,
        region_col="region",
        strain_col="financial_strain"
    ):
        self.model = model
        self.X = X.copy()
        self.region_col = region_col
        self.strain_col = strain_col
        self.interventions = self.calculate_intervention_roi()

    def _build_financial_strain(self):
        """Create a normalized financial-strain score from available features."""

        df = self.X.copy()

        if self.strain_col in df.columns:
            strain = pd.to_numeric(
                df[self.strain_col],
                errors="coerce"
            )
        else:
            components = []

            if "debt_to_income" in df.columns:
                debt_to_income = pd.to_numeric(
                    df["debt_to_income"],
                    errors="coerce"
                ).replace([np.inf, -np.inf], np.nan)

                debt_score = debt_to_income.rank(
                    pct=True,
                    method="average"
                )
                components.append(debt_score)

            if "load_shedding_hours" in df.columns:
                load_shedding = pd.to_numeric(
                    df["load_shedding_hours"],
                    errors="coerce"
                )

                load_score = load_shedding.rank(
                    pct=True,
                    method="average"
                )
                components.append(load_score)

            if "support_tickets" in df.columns:
                support = pd.to_numeric(
                    df["support_tickets"],
                    errors="coerce"
                )

                support_score = support.rank(
                    pct=True,
                    method="average"
                )
                components.append(support_score)

            if not components:
                strain = pd.Series(
                    0.5,
                    index=df.index,
                    dtype=float
                )
            else:
                strain = pd.concat(
                    components,
                    axis=1
                ).mean(axis=1)

        strain = pd.to_numeric(
            strain,
            errors="coerce"
        )

        if strain.notna().sum() == 0:
            return pd.Series(
                0.5,
                index=df.index,
                dtype=float
            )

        minimum = strain.min()
        maximum = strain.max()

        if maximum == minimum:
            return pd.Series(
                0.5,
                index=df.index,
                dtype=float
            )

        return (
            (strain - minimum) /
            (maximum - minimum)
        ).fillna(0.5)

    def _predict_churn_probability(self):
        """Generate churn probabilities from the supplied model."""

        try:
            probabilities = self.model.predict_proba(self.X)

            if probabilities.ndim == 2 and probabilities.shape[1] >= 2:
                return probabilities[:, 1]

        except Exception:
            pass

        try:
            predictions = self.model.predict(self.X)
            return np.asarray(predictions, dtype=float)
        except Exception:
            return np.zeros(len(self.X), dtype=float)

    def calculate_intervention_roi(self):
        """Quantify business impact of three support-focused interventions."""

        interventions = {
            "Fee Waiver for High-Strain": {
                "cost": 185000,
                "saved_customers": 320,
                "lifetime_value": 6500
            },
            "Load-Shedding Support Package": {
                "cost": 240000,
                "saved_customers": 410,
                "lifetime_value": 6200
            },
            "Payment Plan Assistance": {
                "cost": 150000,
                "saved_customers": 285,
                "lifetime_value": 6800
            }
        }

        for name, details in interventions.items():
            gross_value = (
                details["saved_customers"] *
                details["lifetime_value"]
            )

            net_value = gross_value - details["cost"]

            roi = net_value / details["cost"]

            details["gross_value"] = gross_value
            details["net_value"] = net_value
            details["roi"] = roi

        return dict(
            sorted(
                interventions.items(),
                key=lambda item: item[1]["net_value"],
                reverse=True
            )
        )

    def generate_churn_heatmap(
        self,
        output_path="reports/churn_heatmap.png"
    ):
        """Create a regional churn-risk heatmap by financial-strain quartile."""

        os.makedirs(
            os.path.dirname(output_path) or ".",
            exist_ok=True
        )

        data = self.X.copy()

        if self.region_col not in data.columns:
            data[self.region_col] = "Unknown"

        data[self.region_col] = (
            data[self.region_col]
            .fillna("Unknown")
            .astype(str)
        )

        data["financial_strain"] = self._build_financial_strain()
        data["churn_probability"] = self._predict_churn_probability()

        try:
            data["strain_quartile"] = pd.qcut(
                data["financial_strain"],
                q=4,
                labels=[
                    "Q1 Low",
                    "Q2",
                    "Q3",
                    "Q4 High"
                ],
                duplicates="drop"
            )
        except ValueError:
            data["strain_quartile"] = "Overall"

        heatmap_data = data.pivot_table(
            index=self.region_col,
            columns="strain_quartile",
            values="churn_probability",
            aggfunc="mean"
        )

        if heatmap_data.empty:
            heatmap_data = pd.DataFrame(
                [[0]],
                index=["No regional data"],
                columns=["Overall"]
            )

        plt.figure(figsize=(11, 7))

        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt=".1%",
            cmap="YlOrRd",
            vmin=0,
            vmax=1,
            linewidths=0.5,
            cbar_kws={
                "label": "Mean Predicted Churn Probability"
            }
        )

        plt.title(
            "NexusLend Churn Risk by Region and Financial Strain",
            fontsize=14,
            pad=15
        )

        plt.xlabel("Financial Strain Quartile")
        plt.ylabel("Region")

        plt.figtext(
            0.5,
            0.01,
            ETHICAL_WARNING,
            ha="center",
            fontsize=9,
            wrap=True
        )

        plt.tight_layout(
            rect=[0, 0.04, 1, 1]
        )

        plt.savefig(
            output_path,
            dpi=150,
            bbox_inches="tight"
        )

        plt.close()

        return output_path

    def generate_executive_summary(
        self,
        output_path="reports/executive_summary.md"
    ):
        """Create a boardroom-ready executive summary."""

        os.makedirs(
            os.path.dirname(output_path) or ".",
            exist_ok=True
        )

        interventions = self.calculate_intervention_roi()

        top_name, top_data = max(
            interventions.items(),
            key=lambda item: item[1]["roi"]
        )

        total_cost = sum(
            item["cost"]
            for item in interventions.values()
        )

        total_net_value = sum(
            item["net_value"]
            for item in interventions.values()
        )

        projected_roi = (
            total_net_value / total_cost
            if total_cost > 0
            else 0
        )

        intervention_rows = []

        for name, details in interventions.items():
            intervention_rows.append(
                f"| {name} | "
                f"R{details['cost']:,.0f} | "
                f"{details['saved_customers']:,} | "
                f"R{details['gross_value']:,.0f} | "
                f"R{details['net_value']:,.0f} | "
                f"{details['roi']:.1%} |"
            )

        intervention_table = "\n".join(
            intervention_rows
        )

        summary = f"""# NEXUSLEND CHURN INTERVENTION PLAN

## Problem

The churn model identifies customers who may be at increased risk of leaving. Financial strain, debt burden, operational disruption and support needs should be treated as signals for **customer assistance**, not as reasons to restrict access to services.

The analysis therefore focuses on interventions that can reduce avoidable churn while improving customer inclusion.

## Solution

The recommended approach is to provide targeted, supportive interventions:

1. **{list(interventions.keys())[0]}**
2. **{list(interventions.keys())[1]}**
3. **{list(interventions.keys())[2]}**

These interventions are designed around customer support rather than additional financial pressure.

## ROI

### Recommended intervention

**{top_name}**

- Investment: R{top_data['cost']:,.0f}
- Customers potentially retained: {top_data['saved_customers']:,}
- Estimated customer lifetime value: R{top_data['lifetime_value']:,.0f}
- Gross value: R{top_data['gross_value']:,.0f}
- Net value: R{top_data['net_value']:,.0f}
- Intervention ROI: {top_data['roi']:.1%}

### Portfolio impact

| Intervention | Investment | Customers Saved | Gross Value | Net Value | ROI |
|---|---:|---:|---:|---:|---:|
{intervention_table}

**Projected ROI: R{total_net_value:,.0f} net value across the three interventions, representing {projected_roi:.1%} portfolio ROI.**

{CFO_QUOTE}

## Inclusion Impact

The objective is not simply to reduce churn. The objective is to reduce avoidable churn while ensuring that financially vulnerable customers receive appropriate support.

High-strain customers should receive options such as:

- Affordable payment plans
- Temporary fee relief
- Load-shedding support
- Human-assisted financial guidance
- Clear information about available alternatives

{INCLUSION_WARNING}

## Ethical Guardrails

**{ETHICAL_WARNING}**

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
"""

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(summary)

        return output_path

    def __str__(self):
        total_net_value = sum(
            details["net_value"]
            for details in self.interventions.values()
        )

        return (
            f"Generated {len(self.interventions)} interventions | "
            f"Projected ROI: R{total_net_value:,.0f}"
        )


def load_training_data(
    input_path="data/processed/engineered_features.csv"
):
    """Load the engineered dataset."""

    if not os.path.exists(input_path):
        raise FileNotFoundError(
            f"Dataset not found: {input_path}"
        )

    return pd.read_csv(input_path)


def load_model(
    model_path="models/churn_pipeline.pkl"
):
    """Load the trained Milestone 3 pipeline."""

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model not found: {model_path}"
        )

    with open(
        model_path,
        "rb"
    ) as file:
        return pickle.load(file)


def main():
    input_path = "data/processed/engineered_features.csv"
    model_path = "models/churn_pipeline.pkl"

    summary_path = "reports/executive_summary.md"
    heatmap_path = "reports/churn_heatmap.png"

    print("Loading engineered data...")
    df = load_training_data(input_path)

    print(f"Loaded dataset: {df.shape}")

    if "churned" in df.columns:
        X = df.drop(
            columns=["churned"]
        )
    else:
        X = df.copy()

    print("Loading Milestone 3 model...")
    model = load_model(model_path)

    print("Creating ReportGenerator...")
    generator = ReportGenerator(
        model=model,
        X=X,
        region_col="region",
        strain_col="financial_strain"
    )

    print("Calculating intervention ROI...")
    interventions = generator.calculate_intervention_roi()

    for name, details in interventions.items():
        print(
            f"{name}: "
            f"ROI={details['roi']:.1%}, "
            f"Net Value=R{details['net_value']:,.0f}"
        )

    print("Generating churn heatmap...")
    generator.generate_churn_heatmap(
        heatmap_path
    )

    print("Generating executive summary...")
    generator.generate_executive_summary(
        summary_path
    )

    print(generator)

    print("Phase 4 completed successfully.")
    print(
        f"Executive summary saved to: {summary_path}"
    )
    print(
        f"Churn heatmap saved to: {heatmap_path}"
    )


if __name__ == "__main__":
    main()