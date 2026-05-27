# VRP AI Assignment

University project for Artificial Intelligence that solves a Vehicle Routing Problem variant using KNN and a genetic algorithm.

## Model

- `paquetes.csv` contains packages with size, priority, final destination and coordinates.
- KNN assigns each package to the nearest office/delegation through `oficina_asignada`.
- `oficina_asignada` is treated as the pickup office.
- `destino` is treated as the final delivery city.
- Routes are open: vehicles do not have to return to a depot.
- A vehicle can carry multiple packages as long as capacity is respected.

## Approach

1. Load CSV data.
2. Use KNN with `k=1` to assign the nearest pickup office.
3. Build the city graph from the distance CSV.
4. Use a genetic algorithm to assign packages to vehicles and optimize delivery order.

The genetic algorithm chromosome is a list of vehicle routes. Each route contains package IDs, so package assignment and ordering are optimized by the GA instead of by a greedy preselection.

## Project Structure

```text
.
|-- data/
|-- docs/
|-- src/
|-- tests/
|-- main.py
|-- requirements.txt
`-- README.md
```

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Tests

```bash
pytest
```
