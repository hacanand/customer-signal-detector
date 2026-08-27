"""Download a reproducible Banking77 fixture and persist it as API-ready JSON."""
import argparse
import asyncio
import json
from pathlib import Path

from app.repositories.huggingface_repository import HuggingFaceCustomerRepository


async def run(args: argparse.Namespace) -> None:
    repository = HuggingFaceCustomerRepository(args.dataset, args.split, args.count, args.trust_remote_code)
    customers = await repository.list_customers()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps([customer.model_dump() for customer in customers], indent=2), encoding="utf-8")
    print(f"Wrote {len(customers)} {args.dataset} records to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="PolyAI/banking77")
    parser.add_argument("--split", default="test")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--output", default="sample_data/hf_banking77_customers.json")
    parser.add_argument("--trust-remote-code", action="store_true", help="Required by the legacy Banking77 dataset loading script; review it before use.")
    asyncio.run(run(parser.parse_args()))
