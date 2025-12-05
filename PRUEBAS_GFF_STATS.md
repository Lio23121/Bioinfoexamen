# Pruebas del Programa `gff_stats.py`

## Resumen Ejecutivo

El programa `gff_stats.py` ha sido implementado completamente con ambas partes requeridas (A y B) y ha pasado todas las pruebas con éxito.

**Resultados de Pruebas:** 19/19 ✓ (100% de éxito)

---

## Part A - Implementación Base ✓

### Funcionalidad

El programa procesa archivos GFF y genera un JSON con:
- Número total de features no comentados
- Conteo por tipo de feature
- Longitud promedio por tipo (redondeado a 1 decimal)
- Distribución de strand (+ y -)

### Uso

```bash
python gff_stats.py --gff genes.gff --out report.json
```

### Salida Esperada (report.json)

```json
{
  "total_features": 75,
  "by_type": {
    "region": 1,
    "gene": 37,
    "CDS": 37
  },
  "avg_length": {
    "region": 580076.0,
    "gene": 529.0,
    "CDS": 529.0
  },
  "strand_distribution": {
    "+": 57,
    "-": 18
  }
}
```

---

## Part B - Extensión con --filter-type ✓

### Funcionalidad

Permite filtrar estadísticas para un tipo de feature específico.

### Uso

```bash
python gff_stats.py --gff genes.gff --filter-type CDS --out report.json
```

### Salida con Filtro

```json
{
  "total_features": 37,
  "by_type": {
    "CDS": 37
  },
  "avg_length": {
    "CDS": 529.0
  },
  "strand_distribution": {
    "+": 28,
    "-": 9
  }
}
```

---

## Requisitos Técnicos ✓

### ✓ Uso de argparse
- Argumentos `--gff` (requerido)
- Argumentos `--out` (requerido)
- Argumentos `--filter-type` (opcional)
- Mensajes de ayuda informativos

### ✓ Diccionarios, Comprensión de Listas, Manejo de Archivos
- Uso de `defaultdict` para agregaciones
- Procesamiento de líneas con filtrado
- Lectura y escritura de archivos JSON
- Manejo de errores (FileNotFoundError)

### ✓ Pruebas con Asserts
- 19 pruebas unitarias, de integración y de casos límite
- Todas las pruebas pasan correctamente
- Cobertura completa del programa

---

## Pruebas Ejecutadas

### Unit Tests (8 pruebas)
1. ✓ `parse_gff_line: valid GFF line` - Parseo correcto de línea GFF válida
2. ✓ `parse_gff_line: comment line` - Ignora líneas comentadas (##)
3. ✓ `parse_gff_line: empty line` - Ignora líneas vacías
4. ✓ `parse_gff_line: incomplete line` - Rechaza líneas incompletas
5. ✓ `parse_gff_line: with whitespace` - Maneja espacios en blanco
6. ✓ `calculate_length: normal feature` - Calcula longitud correctamente
7. ✓ `calculate_length: single base` - Calcula longitud de 1bp
8. ✓ `calculate_length: large feature` - Calcula longitudes grandes (580076bp)

### Integration Tests (4 pruebas)
1. ✓ `process_gff: full mycoplasma file` - Procesa archivo real correctamente
2. ✓ `process_gff: with filter_type` - Filtra por tipo de feature
3. ✓ `process_gff: strand distribution` - Distribuye strands correctamente
4. ✓ `process_gff: avg length reasonable` - Calcula promedios válidos

### Edge Cases (5 pruebas)
1. ✓ `edge case: empty GFF file` - Maneja archivo vacío
2. ✓ `edge case: only comments` - Maneja archivo solo comentarios
3. ✓ `edge case: single feature` - Procesa un único feature
4. ✓ `edge case: multiple strands` - Maneja múltiples strands
5. ✓ `edge case: nonexistent file` - Levanta FileNotFoundError

### Data Structure Tests (1 prueba)
1. ✓ `avg_length precision: 1 decimal place` - Redondea a 1 decimal

### Consistency Tests (1 prueba)
1. ✓ `filtered vs unfiltered consistency` - Resultados consistentes

---

## Implementación de Funciones

### `parse_gff_line(line)`
- Parsea una línea individual del archivo GFF
- Valida que tenga al menos 8 campos
- Retorna un diccionario con los campos o None si es comentario/vacía
- Convierte start y end a enteros

### `calculate_length(feature)`
- Calcula la longitud de un feature: `end - start + 1`
- Formula estándar en bioinformática (inclusiva en ambos extremos)

### `process_gff(gff_file, filter_type=None)`
- Lee el archivo GFF línea por línea
- Aplica filtro opcional por tipo de feature
- Calcula:
  - Número total de features
  - Conteo por tipo (usando `defaultdict(int)`)
  - Promedio de longitud por tipo (redondeado a 1 decimal)
  - Distribución de strands
- Retorna diccionario con todas las estadísticas

### `main()`
- Parsea argumentos de línea de comandos
- Valida existencia del archivo GFF
- Procesa el archivo
- Escribe salida en JSON con indentación de 2 espacios

---

## Archivos Generados

### Programa Principal
- `Src/gff_stats.py` - Implementación completa

### Pruebas
- `Src/test_gff_stats.py` - Suite de pruebas sin dependencias externas

### Resultados
- `Results/report.json` - Estadísticas del archivo completo
- `Results/report_cds.json` - Estadísticas filtradas por tipo CDS

---

## Ejemplos de Uso

### Ejemplo 1: Procesamiento Completo
```bash
python gff_stats.py --gff "Data/gff mycoplasma" --out Results/report.json
```
Output: `Statistics written to Results\report.json`

### Ejemplo 2: Procesamiento con Filtro
```bash
python gff_stats.py --gff "Data/gff mycoplasma" --filter-type CDS --out Results/report_cds.json
```
Output: `Statistics written to Results\report_cds.json`

### Ejemplo 3: Mostrar Ayuda
```bash
python gff_stats.py --help
```

---

## Validación de Resultados

### Datos del Archivo Mycoplasma

**Archivo completo:**
- Total de features: 75
- Tipos: region (1), gene (37), CDS (37)
- Genes promedio: 529.0 bp
- Strands: + (57), - (18)

**Solo CDS:**
- Total: 37
- Promedio: 529.0 bp
- Strands: + (28), - (9)

---

## Notas Técnicas

### Ventajas de la Implementación
1. **Eficiente:** Procesamiento línea por línea, sin cargar todo en memoria
2. **Robusta:** Maneja casos límite y errores apropiadamente
3. **Extensible:** Fácil agregar nuevas estadísticas
4. **Testeable:** Funciones puras sin efectos secundarios
5. **Portable:** Sin dependencias externas más allá de la stdlib

### Formato GFF
- Formato estándar para anotaciones genómicas
- 9 campos separados por tabulaciones
- El campo "feature" (tercero) especifica el tipo de elemento
- El campo "strand" (séptimo) contiene + o -

### Precisión de Cálculos
- Longitudes: Fórmula estándar `end - start + 1` (inclusive)
- Promedios: Redondeados a 1 decimal para legibilidad
- JSON: Indentado para facilitar lectura manual

---

## Conclusión

El programa `gff_stats.py` cumple completamente todos los requisitos:
- ✓ Parte A: Generación de estadísticas básicas
- ✓ Parte B: Filtrado por tipo de feature
- ✓ Requisitos técnicos: argparse, diccionarios, manejo de archivos
- ✓ Pruebas: 19/19 test cases pasando

El código es production-ready y ha sido validado exhaustivamente.
