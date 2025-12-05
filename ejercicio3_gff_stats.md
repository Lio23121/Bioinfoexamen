# Ejercicio 3 — Estadísticas de un archivo GFF

## **Parte A — Implementación base**

Escribe un programa `gff_stats.py` que:

### **Uso**
```
python gff_stats.py --gff genes.gff --out report.json
```

### **Objetivo**

Procesar el GFF y generar un JSON con:
- Número total de líneas no comentadas.
- Conteo por tipo de feature.
- Longitud promedio por tipo.
- Distribución de strand (+ y -).

### **Ejemplo de salida esperada (report.json)**

```json
{
  "total_features": 512,
  "by_type": {
    "gene": 210,
    "CDS": 290,
    "mRNA": 12
  },
  "avg_length": {
    "gene": 890.3,
    "CDS": 320.7
  },
  "strand_distribution": {
    "+": 61,
    "-": 39
  }
}
```

## **Parte B — Extensión**

Agregar:

```
--filter-type TYPE
```

Ejemplo:

```
python gff_stats.py --gff genes.gff --filter-type CDS
```

Solo calcula estadísticas para las líneas cuyo `type == CDS`.

---

## **Requisitos técnicos**
- Uso de argparse.
- Diccionarios, comprensión de listas, manejo básico de archivos.
- Pruebas con asserts + documento de pruebas, bien con pytest.
