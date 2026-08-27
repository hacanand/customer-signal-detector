import json
import random
from datasets import load_dataset

# We'll use this specific open source dataset for support queries
DATASET_NAME = "bitext/Bitext-customer-support-llm-chatbot-training-dataset"
OUTPUT_PATH = "sample_data/open_source_customers.json"
NUM_RECORDS = 50

# Fictional companies
COMPANIES = [
    "Atlas Health", "Bluebird Studio", "Indigo Finance", "Evergreen Labs",
    "Juniper Health", "Delta Studio", "Granite Retail", "Fable Labs",
    "Harbor Finance", "Cedar Retail"
]

PLANS = ["Starter", "Growth", "Scale", "Enterprise"]

def main():
    print(f"Loading dataset {DATASET_NAME}...")
    ds = load_dataset(DATASET_NAME, split='train')
    
    # Shuffle and pick a subset to have a variety of intents
    ds = ds.shuffle(seed=42).select(range(NUM_RECORDS))
    
    customers = []
    
    for i, record in enumerate(ds):
        intent = record.get("intent", "general_query")
        transcript = record.get("instruction", "No transcript available")
        
        # We synthesize realistic metrics based on the text length and randomness
        monthly_value = random.choice([450, 900, 1800, 4200, 9800])
        
        # Introduce a few explicitly risky patterns
        is_risky = "cancel" in intent or "refund" in intent or random.random() < 0.2
        
        csat = random.randint(1, 2) if is_risky else random.randint(3, 5)
        tickets = random.randint(4, 8) if is_risky else random.randint(1, 3)
        usage = random.randint(-45, -15) if is_risky else random.randint(-5, 15)
        payment_failed = is_risky and random.random() < 0.5
        
        customer = {
            "customer_id": f"OS-{str(i+1).zfill(5)}",
            "name": random.choice(COMPANIES),
            "plan": random.choice(PLANS),
            "monthly_value": monthly_value,
            "satisfaction_score": csat,
            "support_tickets_30d": tickets,
            "usage_change_pct": usage,
            "payment_failed": payment_failed,
            "transcript": transcript,
            "source": "open-source-hf"
        }
        customers.append(customer)
        
    with open(OUTPUT_PATH, "w") as f:
        json.dump(customers, f, indent=2)
        
    print(f"Generated {len(customers)} records to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
