# Remodelacion a KNN + algoritmo genetico

Fecha: 2026-05-27  
Rama: `improve`

## Objetivo

Remodelar el proyecto para que la solucion sea realmente KNN + algoritmo genetico, eliminando la seleccion greedy como nucleo de decision del reparto.

La regla de negocio mantenida es:

- Todos los paquetes deben repartirse.
- Un camion puede llevar varios paquetes.
- Un camion puede seguir recogiendo paquetes tras entregar.
- Si necesita recoger en otra oficina/ciudad, se desplaza por el grafo.
- No se exige regresar a deposito.

## Que se cambio

### 1. `src/genetic_vrp.py`

Se reemplazo el algoritmo genetico anterior.

Antes:

- El cromosoma era una permutacion de ciudades de destino.
- El GA solo ordenaba los destinos de una tanda ya elegida.
- La seleccion de paquetes y la asignacion a camiones ocurria fuera del GA.
- La capacidad del camion no formaba parte del problema genetico.

Ahora:

- El cromosoma representa rutas por camion.
- Cada ruta contiene IDs de paquetes.
- El GA decide que paquetes atiende cada camion y en que orden.
- El fitness simula recogida y entrega de paquetes sobre el grafo.
- Se respeta la capacidad de cada camion.
- Se penalizan rutas invalidas, paquetes no entregados y entregas tardias de mayor prioridad.
- Se usa semilla fija para reproducibilidad.
- Se cachean distancias y rutas para evitar recalculos innecesarios.

### 2. `src/reparto.py`

Se elimino la logica greedy de reparto.

Antes:

- Se buscaban paquetes disponibles en la ciudad actual.
- Si no habia paquetes, se elegia la ciudad mas cercana con paquetes.
- Se ordenaban paquetes por prioridad.
- Se metian en el camion mientras cupieran.
- Despues se usaba el GA solo para ordenar destinos.

Ahora:

- `repartir_todos_los_paquetes` valida que KNN haya creado `oficina_asignada`.
- Crea un `ProblemGeneticVRP`.
- Llama al algoritmo genetico.
- Comprueba que el plan entregue todos los paquetes.
- Devuelve el plan generado por el GA.

### 3. `src/graph_utils.py`

Se corrigio el comportamiento ante ciudades inexistentes.

Antes:

- `shortest_path_route` podia lanzar `KeyError` si el origen o destino no existian en el grafo.

Ahora:

- `shortest_path` y `shortest_path_route` devuelven `None` cuando el origen o destino no existen.
- El GA puede tratar rutas invalidas como penalizaciones controladas.

## Por que se cambio

El audit detectaba que el proyecto usaba KNN y algoritmo genetico, pero que la parte genetica no resolvia el reparto completo. La decision mas importante, que paquetes llevaba cada camion, seguia estando fuera del GA.

Con esta remodelacion:

- KNN sigue asignando cada paquete a una oficina/delegacion.
- El AG pasa a decidir la planificacion completa del reparto.
- La capacidad de los vehiculos forma parte de la evaluacion genetica.
- El reparto ya no depende de una seleccion greedy previa.

## Que mejora

### Mejor alineacion academica

El proyecto es ahora mas defendible como KNN + AG:

- KNN se usa para asignacion geografica de oficinas.
- El algoritmo genetico se usa para construir y optimizar rutas de reparto.

### Menos dependencia de reglas greedy

La solucion anterior dependia de ordenar paquetes por prioridad y meterlos en el camion mientras cupieran. Eso podia generar tandas validas, pero no era una decision genetica.

Ahora el GA explora diferentes asignaciones paquete-camion y diferentes ordenes de entrega.

### Mejor resultado observado

Con los datos actuales:

- Antes: 30/30 paquetes entregados, distancia total observada 20540 km.
- Ahora: 30/30 paquetes entregados, distancia total observada 16745 km.

La mejora observada es de 3795 km menos en esta ejecucion.

### Mejor control de errores

El problema genetico valida:

- que haya paquetes;
- que haya vehiculos;
- que cada paquete quepa en al menos un camion;
- que ciudades iniciales, oficinas y destinos existan en el grafo.

Si no se puede construir un plan valido, el codigo falla con un mensaje explicito.

## Limitaciones que quedan

- El modelo sigue siendo una aproximacion academica, no un solver industrial de VRP.
- El GA no modela ventanas temporales.
- No se exige retorno a deposito porque no era obligatorio.
- La carga multiple se simula por paquetes consecutivos con la misma oficina de recogida dentro de la ruta de un camion.
- No se ha anadido una suite formal de tests, aunque seria recomendable para proteger futuras modificaciones.

## Pendientes del audit y resolucion aplicada

### 1. Separar mejor distancia real y coste de fitness

Estado: Resuelto.

Se cambio el retorno del AG a una estructura `GeneticResult`:

```python
GeneticResult(
    best_chromosome=best,
    plan=plan,
    total_distance=total_distance,
    fitness_cost=fitness_cost,
)
```

Impacto:

- La distancia real queda separada de las penalizaciones internas.
- El resultado del AG es mas facil de explicar y consumir.

### 2. Documentar mejor `oficina_asignada` vs `destino`

Estado: Resuelto.

README documenta el modelo de datos:

- `oficina_asignada`: oficina/delegacion de recogida.
- `destino`: ciudad final de entrega.

El AG mantiene nombres internos claros: `pickup` y `destination`.

Impacto:

- Hace el proyecto mas defendible academicamente.
- Reduce la apariencia de incoherencia entre KNN y reparto.

### 3. Mejorar optimizacion de distancias

Estado: Resuelto.

El AG precalcula rutas y distancias relevantes al crear `ProblemGeneticVRP` y conserva caches:

- `distance_cache`
- `route_cache`

Impacto:

- Mejor rendimiento si crecen paquetes, ciudades o generaciones.
- Fitness mas barato de evaluar.

### 4. Justificar y validar KNN

Estado: Resuelto.

`asignar_oficinas` ahora:

- valida columnas requeridas;
- valida coordenadas nulas;
- exige `k=1`;
- documenta que KNN se usa como nearest-office assignment.

Impacto:

- Mejora robustez ante CSV mal formado.
- Refuerza la parte KNN del proyecto.

### 5. Crear archivo de dependencias

Estado: Resuelto.

Se creo `requirements.txt`:

```text
pandas
scikit-learn
pytest
```

Impacto:

- Facilita reproducir el proyecto.
- Evita depender solo de instrucciones textuales en README.

### 6. Tests opcionales pero recomendables

Estado: Resuelto.

Se creo `tests/` con pruebas para:

- grafo con ciudad desconocida;
- KNN;
- coordenadas nulas;
- entrega 30/30 con el dataset actual;
- reproducibilidad del AG;
- paquete demasiado grande.

Impacto:

- Protege el redisenio KNN + AG.
- Facilita seguir mejorando sin romper el reparto.

### 7. Limpiar `__pycache__` versionado

Estado: Resuelto.

Se creo `.gitignore`:

```text
__pycache__/
*.pyc
.venv/
venv/
```

Los `.pyc` fueron eliminados del indice Git.

Impacto:

- Diffs mas limpios.
- Evita cambios por recompilaciones locales.

### 8. Unificar nombres

Estado: Resuelto en el flujo principal.

Se normalizaron nombres en `main.py`, `src/reparto.py`, `src/utils.py` y `src/knn_assignment.py`. Se mantienen `Package`, `Vehicle`, `pickup` y `destination` en el AG porque expresan claramente el modelo interno.

Impacto:

- Mejora legibilidad.
- Reduce typos como `vehicules`.

### 9. Hacer rutas de datos independientes del directorio actual

Estado: Resuelto.

`cargar_datos` acepta `data_dir` y usa una ruta por defecto basada en la raiz del proyecto:

```python
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
```

Impacto:

- El proyecto funciona aunque se ejecute desde otro working directory.
- Facilita tests y reutilizacion.

## Verificacion realizada

Comando ejecutado:

```bash
python main.py
```

Resultado observado:

- Paquetes entregados: 30 / 30.
- Vehiculos con ruta: 5.
- Distancia total recorrida: 16745 km.
- El proyecto sigue usando KNN antes de invocar el reparto genetico.
