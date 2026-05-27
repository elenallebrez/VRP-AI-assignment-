import pandas as pd
import pytest

from src.knn_assignment import asignar_oficinas


def test_asignar_oficinas_creates_assigned_office():
    paquetes = pd.DataFrame({"latitud": [40.4], "longitud": [-3.7]})
    oficinas = pd.DataFrame(
        {
            "ciudad": ["madrid", "sevilla"],
            "latitud": [40.4168, 37.3886],
            "longitud": [-3.7038, -5.9823],
        }
    )

    result = asignar_oficinas(paquetes, oficinas)

    assert result.loc[0, "oficina_asignada"] == "MADRID"


def test_asignar_oficinas_rejects_missing_coordinates():
    paquetes = pd.DataFrame({"latitud": [None], "longitud": [-3.7]})
    oficinas = pd.DataFrame({"ciudad": ["madrid"], "latitud": [40.4168], "longitud": [-3.7038]})

    with pytest.raises(ValueError, match="coordenadas nulas"):
        asignar_oficinas(paquetes, oficinas)
