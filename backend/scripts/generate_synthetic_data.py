"""Create deterministic, realistic demo accounts without exposing personal data."""
import argparse
import json
import random
from pathlib import Path

NAMES = ["Atlas", "Bluebird", "Cedar", "Delta", "Evergreen", "Fable", "Granite", "Harbor", "Indigo", "Juniper"]
TEMPLATES = [
    ("The export is still not working and our team is frustrated. We may cancel if this is not fixed.", 1, 7, -42, True),
    ("I am still waiting for a resolution. This billing issue is unacceptable.", 2, 5, -28, True),
    ("The team has some questions about the dashboard, but onboarding is progressing.", 3, 3, -12, False),
    ("Everything is working well. The adoption session was very useful.", 4, 1, 8, False),
    ("Can you help us update account permissions?", 4, 1, 2, False),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="sample_data/generated_customers.json")
    args = parser.parse_args()
    rng, records = random.Random(args.seed), []
    for index in range(args.count):
        transcript, csat, tickets, usage, failed = rng.choice(TEMPLATES)
        records.append({"customer_id": f"SYN-{index + 1:05d}", "name": f"{rng.choice(NAMES)} {rng.choice(['Labs', 'Retail', 'Health', 'Finance', 'Studio'])}", "plan": rng.choice(["Starter", "Growth", "Scale", "Enterprise"]), "monthly_value": rng.choice([450, 900, 1800, 4200, 9800]), "satisfaction_score": csat, "support_tickets_30d": tickets, "usage_change_pct": usage, "payment_failed": failed, "transcript": transcript, "source": "synthetic"})
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} records to {output}")


if __name__ == "__main__":
    main()
