# Premier League Historical Data Analysis (1993-2025)

Sistema completo de extracción y análisis de datos históricos de la Premier League desde 1993 hasta 2025.

## 📋 Descripción

Este proyecto proporciona una base de datos limpia y verificada de todas las temporadas de la Premier League, incluyendo clasificaciones finales, estadísticas de equipos y seguimiento histórico.

## 🎯 Características

- **Datos completos**: 32 temporadas (1993-94 hasta 2024-25)
- **100% verificados**: Validación automática de consistencia
- **Fuente confiable**: football-data.co.uk
- **Tracking histórico**: Seguimiento de cada equipo a través de los años
- **644 registros** de 51 equipos únicos

## 📁 Archivos Principales

```
futbol/
├── scraper_premier_league.py              # Scraper principal ⭐
├── analisis_premier_league.ipynb          # Notebook de análisis
├── premier_league_COMPLETO_football_data.csv    # Datos completos ⭐
├── premier_league_tracking_COMPLETO.csv         # Tracking por equipo ⭐
├── README.md                              # Este archivo
├── RESUMEN.md                             # Guía rápida
└── archive/                               # Versiones anteriores
```

## 🚀 Uso Rápido

### 1. Extraer Datos Actualizados

```bash
python scraper_premier_league.py
```

Esto descarga y procesa todas las temporadas, generando:
- `premier_league_COMPLETO_football_data.csv`
- `premier_league_tracking_COMPLETO.csv`

### 2. Análisis en Jupyter

```bash
jupyter notebook analisis_premier_league.ipynb
```

## 📊 Estructura de Datos

### Archivo Principal: `premier_league_COMPLETO_football_data.csv`

| Columna   | Descripción                      | Tipo    |
|-----------|----------------------------------|---------|
| Temporada | Temporada (ej: "1993-94")       | string  |
| Pos       | Posición final                   | int     |
| Equipo    | Nombre del equipo                | string  |
| PJ        | Partidos jugados                 | int     |
| G         | Partidos ganados                 | int     |
| E         | Partidos empatados               | int     |
| P         | Partidos perdidos                | int     |
| Pts       | Puntos totales                   | int     |
| GF        | Goles a favor                    | int     |
| GC        | Goles en contra                  | int     |
| Dif       | Diferencia de goles              | string  |

### Archivo de Tracking: `premier_league_tracking_COMPLETO.csv`

- Matriz de equipos × temporadas
- `{temporada}_Pos` - Posición en cada temporada
- `{temporada}_Pts` - Puntos en cada temporada
- `Total_Temporadas` - Temporadas jugadas
- `Mejor_Posicion` - Mejor posición histórica
- `Peor_Posicion` - Peor posición histórica

## 📈 Análisis Disponibles

El notebook incluye funciones para:

### `ver_historial_equipo(nombre)`
```python
ver_historial_equipo('Arsenal')
```

### `ver_temporada(temporada)`
```python
ver_temporada('2015-16')  # Temporada del Leicester
```

### `comparar_equipos(*equipos)`
```python
comparar_equipos('Man United', 'Liverpool', 'Arsenal')
```

## 🎯 Casos de Uso

### Ver tabla de una temporada específica
```python
import pandas as pd
df = pd.read_csv('premier_league_COMPLETO_football_data.csv')
temporada_2016 = df[df['Temporada'] == '2015-16'].sort_values('Pos')
print(temporada_2016[['Pos', 'Equipo', 'Pts']])
```

### Encontrar campeones históricos
```python
campeones = df[df['Pos'] == 1].sort_values('Temporada')
print(campeones[['Temporada', 'Equipo', 'Pts']])
```

### Equipos siempre en Premier League
```python
tracking = pd.read_csv('premier_league_tracking_COMPLETO.csv')
siempre_premier = tracking[tracking['Total_Temporadas'] == 32]
print(siempre_premier[['Equipo', 'Mejor_Posicion', 'Peor_Posicion']])
```

## 🔧 Requisitos

```bash
pip install pandas requests
```

## 📝 Validación de Datos

El scraper incluye validación automática:

✅ **G + E + P = PJ** (partidos jugados)  
✅ **Pts = 3×G + E** (sistema de puntos)  
✅ **20-22 equipos** por temporada  

**Resultado:** 0 errores en 644 registros

## 🏆 Top 10 Equipos Históricos

| Equipo      | Temporadas | Mejor Pos | Peor Pos |
|-------------|------------|-----------|----------|
| Arsenal     | 32         | 1         | 12       |
| Chelsea     | 32         | 1         | 14       |
| Tottenham   | 32         | 2         | 17       |
| Man United  | 32         | 1         | 15       |
| Everton     | 32         | 4         | 17       |
| Liverpool   | 32         | 1         | 8        |
| Newcastle   | 30         | 2         | 18       |
| West Ham    | 29         | 5         | 20       |
| Aston Villa | 29         | 4         | 20       |
| Man City    | 27         | 1         | 18       |

## 📌 Notas Importantes

1. **Temporada 1992-93 no incluida**: football-data.co.uk empieza en 1993-94
2. **Temporada 2024-25**: Datos parciales (temporada en curso)
3. **Nombres de equipos**: Formato estándar (ej: "Man United" en lugar de "Manchester United F.C.")

## 🔄 Historia del Proyecto

### v2.0 - Versión Actual (Octubre 2024)
- ✅ Migración a football-data.co.uk como fuente única
- ✅ 100% de datos consistentes y verificados
- ✅ 32 temporadas completas
- ✅ Sistema de tracking automático

### v1.0 - Versión Inicial (Archivada)
- Scraping de Wikipedia (español e inglés)
- Problemas de inconsistencia en tablas EN
- 12 temporadas exitosas, 21 con errores
- **Motivo del cambio**: Tablas de Wikipedia con estructuras diferentes causaban errores de parsing

**Archivos v1.0 movidos a `/archive`:**
- `scraper_robusto.py` - Scraper original de Wikipedia
- `scraper_v2_FIXED.py` - Intento de fix para tablas EN
- Scripts de diagnóstico y limpieza

## 🤝 Contribuciones

Sugerencias y mejoras son bienvenidas. El proyecto está diseñado para:
- Mantenerse actualizado con nuevas temporadas
- Expandirse a otras ligas
- Añadir más análisis estadísticos

## 📄 Fuente de Datos

**football-data.co.uk**
- URL: http://www.football-data.co.uk/englandm.php
- Licencia: Uso libre para fines no comerciales
- Actualización: Semanal durante la temporada

## 🙏 Agradecimientos

- **football-data.co.uk** por mantener datos históricos detallados
- Comunidad de análisis de fútbol por documentar metodologías

---

**Última actualización**: Octubre 2024  
**Versión**: 2.0  
**Autor**: Angel Samuel Suescarios  
**Temporadas**: 1993-94 a 2024-25 (32 temporadas)