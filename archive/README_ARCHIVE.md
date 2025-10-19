# Archivos Archivados - v1.0

Este directorio contiene la primera versión del proyecto que usaba Wikipedia como fuente de datos.

## ❌ Por qué se archivó v1.0

### Problema Principal
Las tablas de Wikipedia (especialmente en inglés) tienen **estructuras inconsistentes** que causaban errores de parsing:

- **Tablas ES**: Funcionaban bien (12 temporadas exitosas)
- **Tablas EN**: Columnas "shifted" causaban datos incorrectos (21 temporadas fallidas)
- **Resultado**: Solo 36% de éxito (12/33 temporadas)

### Síntomas
```
- PJ (Partidos Jugados) mostraba valores incorrectos
- Pts siempre aparecía como 38
- G, E, P estaban mezclados con otras columnas
- 420/420 registros EN con inconsistencias
```

### Intentos de Solución
1. ✅ `scraper_robusto.py` - Parser básico con validación
2. ❌ `scraper_v2_FIXED.py` - Intento de mapeo dinámico de columnas
3. ❌ Scripts de diagnóstico - Detectaron el problema pero no lo resolvieron

### Decisión Final
Migrar a **football-data.co.uk** como fuente única:
- ✅ CSVs bien estructurados
- ✅ Datos verificados profesionalmente  
- ✅ 100% consistencia
- ✅ 32/32 temporadas exitosas

## 📁 Archivos en este directorio

### Scripts de Scraping
- `scraper_robusto.py` - Scraper original de Wikipedia ES/EN
- `scraper_v2_FIXED.py` - Intento de fix para tablas EN
- `scraper_football_data_uk.py` - Primera versión del scraper actual

### Scripts de Diagnóstico
- `diagnostico_problema.py` - Detecta inconsistencias en datos
- `analizar_y_limpiar.py` - Análisis de datos ES vs EN
- `diagnostico_temporadas.py` - Verifica temporadas faltantes

### Datos v1.0
- `premier_league_completo_limpio.csv` - Datos mezclados (ES + EN con errores)
- `premier_league_SOLO_ES_limpio.csv` - Solo datos ES (12 temporadas)
- `premier_league_tracking_equipos.csv` - Tracking incompleto
- `resumen_premier_league.csv` - Resumen parcial

## 🔍 Lecciones Aprendidas

1. **No todas las fuentes son iguales**: Wikipedia es excelente para consulta humana, pero difícil para parsing automatizado
2. **Validación es crítica**: Sin validación estricta, los errores pasan desapercibidos
3. **Fuente única > Múltiples fuentes**: Consistencia es más importante que cobertura
4. **Datos primarios > Datos derivados**: football-data.co.uk tiene resultados de partidos, no solo tablas finales

## 📊 Comparación v1.0 vs v2.0

| Aspecto | v1.0 (Wikipedia) | v2.0 (football-data.co.uk) |
|---------|------------------|----------------------------|
| Temporadas exitosas | 12/33 (36%) | 32/32 (100%) |
| Consistencia | Problemas en 420 registros | 0 errores |
| Fuentes | 2 (ES + EN) | 1 (CSV) |
| Mantenimiento | Alto (cambios en HTML) | Bajo (CSV estable) |
| Datos adicionales | No | Sí (partidos individuales) |

## 🚀 Para Usar v1.0 (No Recomendado)

Si necesitas consultar la versión antigua:

```bash
cd archive
python scraper_robusto.py  # Solo funciona para temporadas ES
```

**Advertencia**: Los datos de Wikipedia EN contienen errores conocidos.

## 💡 Si Necesitas Wikipedia

Para consulta manual de Wikipedia (no automática):
- https://es.wikipedia.org/wiki/Premier_League_1992-93
- https://en.wikipedia.org/wiki/1999–00_Premier_League

Pero para análisis automatizado, usa **v2.0 con football-data.co.uk**.

---

**Fecha de archivo**: Octubre 2024  
**Razón**: Migración a fuente más confiable  
**Estado**: Solo referencia histórica