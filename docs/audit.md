# Auditoria tecnica del repositorio

Fecha: 2026-05-27  
Rama revisada: `improve`  
Estado: hallazgos del audit resueltos tras la remodelacion KNN + AG

## Contexto de evaluacion

1. Todos los paquetes se deben repartir.
2. El proyecto academico debe implementar KNN y algoritmo genetico para el VRP.
3. No era obligatorio crear tests, pero se han anadido pruebas minimas.
4. El reparto permite varios paquetes por camion, recogida tras entrega y rutas abiertas sin regreso obligatorio a deposito.
5. La decision greedy fue eliminada como nucleo del reparto.

## Resumen ejecutivo actualizado

El proyecto queda remodelado como solucion KNN + algoritmo genetico:

- KNN asigna cada paquete a la oficina/delegacion mas cercana (`oficina_asignada`).
- `oficina_asignada` se interpreta como oficina de recogida.
- `destino` se interpreta como ciudad final de entrega.
- El algoritmo genetico decide asignacion paquete-camion y orden de entrega.
- El cromosoma representa rutas por camion con IDs de paquetes.
- Se valida que todos los paquetes sean entregables.
- Se eliminaron los `.pyc` versionados.
- Se anadieron dependencias, configuracion de pytest y tests minimos.

Verificacion actual:

- `python -m compileall main.py src`: correcto.
- `python main.py`: correcto, entrega 30/30 paquetes.
- `pytest -q`: correcto, 6 tests pasan.

## Estado de hallazgos

### 1. El cromosoma agrupaba paquetes con el mismo destino

Estado: Resuelto.

El AG ya no usa una lista de destinos unicos como cromosoma. Ahora cada gen es un ID de paquete y el cromosoma completo representa rutas por camion.

### 2. Regreso a deposito

Estado: Resuelto como decision de modelado.

No se exige regreso a deposito. El proyecto documenta rutas abiertas/continuas, coherentes con que el camion pueda seguir recogiendo paquetes desde su ultima ciudad.

### 3. Capacidad y carga multiple fuera del AG

Estado: Resuelto.

La capacidad se valida y se evalua dentro del problema genetico. La asignacion de paquetes a camiones ya no ocurre mediante una seleccion greedy previa.

### 4. Fitness penalizado confundido con distancia real

Estado: Resuelto.

Se separo el resultado genetico en:

- `total_distance`: distancia real del plan.
- `fitness_cost`: distancia + penalizaciones internas del AG.

`genetic_algorithm` devuelve un `GeneticResult`, evitando confundir metricas reales con coste de optimizacion.

### 5. Penalizacion por duplicados

Estado: Resuelto.

El cromosoma se construye desde paquetes individuales y la deteccion de duplicados queda solo como defensa durante la evaluacion.

### 6. Falta de semilla configurable

Estado: Resuelto.

`genetic_algorithm` acepta `seed` y usa `random.Random(seed)`.

### 7. Tamano de poblacion podia exceder `population_size`

Estado: Resuelto.

El bucle del AG controla el tamano de `next_population` y solo anade el segundo hijo si hay espacio.

### 8. Riesgo de bucle infinito en el reparto

Estado: Resuelto.

El `while not entregado.all()` fue eliminado. Si el AG no entrega todos los paquetes, se lanza un error claro.

### 9. El AG no resolvia el VRP completo

Estado: Resuelto para el alcance academico.

El AG ahora decide asignacion de paquetes a vehiculos y orden de entrega. Sigue siendo una aproximacion academica, pero ya no es solo un TSP por tanda elegida previamente.

### 10. Diferencia entre destino real y oficina asignada

Estado: Resuelto.

README y documentacion explican que:

- `oficina_asignada` es oficina/delegacion de recogida.
- `destino` es ciudad final de entrega.

El AG usa internamente `pickup` y `destination`.

### 11. `shortest_path_route` fallaba con destinos desconocidos

Estado: Resuelto.

`shortest_path` y `shortest_path_route` devuelven `None` cuando origen o destino no existen.

### 12. Seleccion greedy de carga multiple

Estado: Resuelto.

La seleccion greedy fue eliminada de `src/reparto.py`; la asignacion y el orden pasan por el AG.

### 13. Mutacion inesperada del DataFrame de paquetes

Estado: Resuelto.

`src/reparto.py` trabaja con copias y no agrega columnas de estado al DataFrame original.

### 14. Recalculo excesivo de rutas y distancias

Estado: Resuelto.

El AG precalcula rutas/distancias relevantes y mantiene caches `distance_cache` y `route_cache`.

### 15. KNN con `k=1`

Estado: Resuelto.

`asignar_oficinas` valida columnas, coordenadas nulas y exige `k=1`, porque el objetivo del proyecto es asignar la oficina mas cercana.

### 16. No habia archivo de dependencias

Estado: Resuelto.

Se creo `requirements.txt` con:

- `pandas`
- `scikit-learn`
- `pytest`

### 17. No habia tests automatizados

Estado: Resuelto.

Se anadio `pytest.ini` y pruebas minimas:

- ciudad desconocida en grafo;
- asignacion KNN;
- validacion de coordenadas nulas;
- entrega 30/30 con el dataset actual;
- reproducibilidad del AG con semilla;
- error claro para paquete demasiado grande.

### 18. `__pycache__` versionado

Estado: Resuelto.

Se creo `.gitignore` y se eliminaron los `.pyc` del indice Git.

### 19. Imports sin uso

Estado: Resuelto.

Los imports antiguos sin uso fueron eliminados.

### 20. Nombres mezclados

Estado: Resuelto en el flujo principal.

Se normalizaron nombres en `main.py`, `src/reparto.py`, `src/utils.py` y `src/knn_assignment.py`. Quedan nombres internos en ingles (`Package`, `Vehicle`, `pickup`, `destination`) por claridad tecnica del AG.

### 21. Rutas de datos acopladas al directorio de ejecucion

Estado: Resuelto.

`cargar_datos` acepta `data_dir` y por defecto resuelve la carpeta `data` desde la raiz del proyecto con `Path(__file__).resolve().parents[1]`.

## Conclusion

Todos los hallazgos parciales o pendientes del audit fueron resueltos en esta iteracion. El proyecto queda mas alineado con el objetivo academico KNN + algoritmo genetico, con mejor reproducibilidad, validaciones, tests y documentacion.
