# Multi-City Route Optimizer

A FastAPI delivery planner compares nearest-neighbor and genetic algorithms on open routes between Indian cities. The greedy solver visits priority groups in order. The genetic solver scores routes by distance plus a penalty for out-of-order stops. Distances are geodesic estimates between city coordinates.

## Run the application

From the repository root:

~~~sh
pip install -r requirements.txt
python main.py
~~~

See the [interactive demo](https://route-optimizer-xd92.onrender.com), [architecture](docs/ARCHITECTURE.md), [API examples](RouteOptimizer.postman_collection.json), and [deployment guide](DEPLOYMENT.md). The API supports planning a route, changing delivery priorities, and adding or removing stops.

## Reproduce the solver comparison

~~~sh
python -m scripts.quick_test
python -m scripts.benchmark --seed 42 --cases 25 --output benchmark-results.csv
~~~

The quick check prints the distances of two example itineraries. The benchmark samples 25 city sets at each of four sizes (5, 10, 15 and 17 cities including the start). Each set runs with and without delivery priorities. Both solvers receive the same start, stops and priorities, with the distance cache cleared before each call.

Each CSV row records both routes, distances, priority violations, elapsed solver times and the genetic solver seed. Positive km_saved means the genetic route was shorter. Read distance alongside violations when priorities are enabled. A seed reproduces routes in the same environment. Timings depend on the machine. This experiment measures solver performance on static city coordinates. It does not measure road travel time, fuel cost or annual savings.

## License

[MIT](LICENSE)
