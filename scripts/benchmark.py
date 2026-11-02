"""Compare both route solvers on the same seeded delivery cases."""
import argparse
import csv
import json
import random
from collections import Counter

from utils.algorithm import optimize_route
from utils.cities import get_all_cities
from utils.distance import clear_cache


def benchmark(seed, cases):
    cities = sorted(get_all_cities())
    generator = random.Random(seed)
    for size in (5, 10, 15, 17):
        for case in range(cases):
            start, *stops = generator.sample(cities, size)
            ranks = {city: generator.randint(1, 3) for city in stops}
            solver_seed = generator.getrandbits(32)
            for priorities in ({}, ranks):
                row = dict(size=size, case=case, seed=solver_seed, start=start,
                           stops=json.dumps(stops), priorities=json.dumps(priorities))
                for name in ("greedy", "genetic"):
                    clear_cache()
                    result = optimize_route(start, stops, priorities, name == "genetic", seed=solver_seed)
                    route = result["route"]
                    if route[0] != start or sorted(route[1:]) != sorted(stops):
                        raise ValueError(f"{name} returned an invalid route")
                    row[name + "_route"] = json.dumps(route)
                    row[name + "_km"] = result["total_distance"]
                    row[name + "_ms"] = result["execution_time_ms"]
                    order = [priorities.get(city, 1) for city in route[1:]]
                    row[name + "_violations"] = sum(
                        earlier > later for i, earlier in enumerate(order) for later in order[i + 1:]
                    )
                delta = round(row["greedy_km"] - row["genetic_km"], 2)
                row["km_saved"] = delta
                row["genetic_distance_outcome"] = "shorter" if delta > 0 else "longer" if delta < 0 else "tie"
                yield row


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--cases", type=int, default=25, help="city sets per size")
    parser.add_argument("--output", default="benchmark-results.csv")
    args = parser.parse_args()
    if args.cases < 1:
        parser.error("--cases must be positive")
    counts = Counter()
    with open(args.output, "w", newline="", encoding="utf-8") as output:
        writer = None
        for row in benchmark(args.seed, args.cases):
            if writer is None:
                writer = csv.DictWriter(output, fieldnames=list(row))
                writer.writeheader()
            writer.writerow(row)
            counts[row["genetic_distance_outcome"]] += 1
    print(f"{sum(counts.values())} paired comparisons written to {args.output}: {dict(counts)}")
