from src.graph_utils import shortest_path_route


def test_shortest_path_route_unknown_city_returns_none():
    graph = {"a": {"b": 1}, "b": {"a": 1}}

    assert shortest_path_route(graph, "a", "x") is None
