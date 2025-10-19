# English Football Pyramid - Historical Data Analysis (1993-2025)

Sistema completo de extracción y análisis de datos históricos del fútbol inglés, cubriendo las 5 divisiones principales desde 1993 hasta 2025.

## 📋 Descripción

Este proyecto proporciona bases de datos limpias y verificadas de todas las temporadas históricas del fútbol inglés profesional:
- **Premier League** (Nivel 1): 1993-2025
- **Championship** (Nivel 2): 2004-2025
- **League One** (Nivel 3): 2004-2025
- **League Two** (Nivel 4): 2004-2025
- **National League** (Nivel 5): 2005-2025

Incluye clasificaciones finales, estadísticas de equipos y seguimiento longitudinal completo.

## 🎯 Características

### Fase 2: Premier League (v2.0) ✅
- **Datos completos**: 32 temporadas (1993-94 hasta 2024-25)
- **100% verificados**: Validación automática de consistencia
- **644 registros** de 51 equipos únicos
- **0 errores** en validación

### Fase 3: English Football Pyramid Expansion ⭐ NUEVO
- **5 divisiones** completas del sistema piramidal inglés
- **3,260 registros totales** verificados (32 temporadas para niveles 1-4)
- **160 equipos únicos** rastreados a través de todas las divisiones
- **Tracking longitudinal**: Seguimiento completo desde 1993 de ascensos/descensos
- **Datos históricos completos**: Championship, League One y League Two desde 1993 (nombres históricos: First/Second/Third Division)
- **Fuente única confiable**: football-data.co.uk

## 📁 Archivos Principales

```
futbol/
├── scraper_premier_league.py                    # Scraper Premier League (Fase 2) ⭐
├── scraper_english_leagues.py                   # Scraper todas las divisiones (Fase 3) ⭐⭐ NUEVO
├── verificar_datos.py                           # Validación Premier League
├── verificar_english_leagues.py                 # Validación multi-división ⭐ NUEVO
├── premier_league_COMPLETO_football_data.csv    # Datos Premier League ⭐
├── english_leagues_completo.csv                 # Datos 5 divisiones ⭐⭐ NUEVO
├── premier_league_tracking_COMPLETO.csv         # Tracking Premier League
├── english_leagues_tracking.csv                 # Tracking longitudinal ⭐ NUEVO
├── analisis_premier_league.ipynb                # Análisis Premier League
├── README.md                                    # Este archivo
├── RESUMEN.md                                   # Guía rápida
├── CLAUDE.md                                    # Guía para Claude Code
├── Prompt.md                                    # Especificaciones Fase 3
└── archive/                                     # Versiones anteriores (v1.0 Wikipedia)
```

## 🚀 Uso Rápido

### Opción A: Solo Premier League (Fase 2)

```bash
# Extraer datos de Premier League
python scraper_premier_league.py

# Verificar datos
python verificar_datos.py

# Analizar
jupyter notebook analisis_premier_league.ipynb
```

Genera:
- `premier_league_COMPLETO_football_data.csv` (644 registros)
- `premier_league_tracking_COMPLETO.csv` (51 equipos)

### Opción B: Todas las Divisiones (Fase 3) ⭐ RECOMENDADO

```bash
# Extraer datos de todas las divisiones (Premier a National League)
python scraper_english_leagues.py

# Verificar datos extendidos
python verificar_english_leagues.py
```

Genera:
- `english_leagues_completo.csv` (3,260 registros de 5 divisiones, 32 temporadas)
- `english_leagues_tracking.csv` (160 equipos con trayectorias completas desde 1993)

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

## 📈 English Football Pyramid Expansion (Fase 3) ⭐ NUEVO

### Estructura Multi-División

**Dataset Unificado**: `english_leagues_completo.csv`

| Columna   | Descripción                       | Tipo    |
|-----------|-----------------------------------|---------|
| Temporada | Temporada (ej: "2015-16")        | string  |
| Division  | División (Premier League, etc)    | string  |
| Pos       | Posición final                    | int     |
| Equipo    | Nombre del equipo                 | string  |
| PJ        | Partidos jugados                  | int     |
| G         | Partidos ganados                  | int     |
| E         | Partidos empatados                | int     |
| P         | Partidos perdidos                 | int     |
| Pts       | Puntos totales                    | int     |
| GF        | Goles a favor                     | int     |
| GC        | Goles en contra                   | int     |
| Dif       | Diferencia de goles               | string  |

### Tracking Longitudinal

**Archivo**: `english_leagues_tracking.csv`

Sigue la trayectoria completa de cada equipo a través de todas las divisiones:
- Posición y puntos en cada temporada
- División jugada por temporada
- Total de temporadas jugadas
- Número de divisiones diferentes jugadas
- Mejor división alcanzada

### Resumen por División

| División        | Temporadas | Equipos | Registros | Periodo      | Nota Histórica |
|-----------------|------------|---------|-----------|--------------|----------------|
| Premier League  | 32         | 51      | 644       | 1993-2025    | - |
| Championship    | 32         | 69      | 768       | 1993-2025    | First Division (1993-2004) |
| League One      | 31         | 91      | 744       | 1993-2025    | Second Division (1993-2004) |
| League Two      | 30         | 80      | 720       | 1993-2025    | Third Division (1993-2004) |
| National League | 16         | 90      | 384       | 2005-2025    | Datos limitados |
| **TOTAL**       | **32**     | **160** | **3,260** | **1993-2025**| **+744 registros vs v3.0** |

### Casos de Uso - Análisis Multi-División

#### Trayectoria completa de un equipo
```python
import pandas as pd

df = pd.read_csv('english_leagues_completo.csv')
tracking = pd.read_csv('english_leagues_tracking.csv')

# Ver historial completo de Leicester
leicester = df[df['Equipo'] == 'Leicester'].sort_values('Temporada')
print(leicester[['Temporada', 'Division', 'Pos', 'Pts']])
```

#### Equipos con mayor movilidad
```python
# Equipos que han jugado en más divisiones
movilidad = tracking[['Equipo', 'Total_Temporadas', 'Divisiones_Jugadas', 'Mejor_Division']]
mas_viajados = movilidad.nlargest(10, 'Divisiones_Jugadas')
print(mas_viajados)
```

#### Análisis de ascensos/descensos
```python
# Encontrar equipos que ascendieron de Championship a Premier League
for season in df['Temporada'].unique():
    premier = df[(df['Temporada'] == season) & (df['Division'] == 'Premier League')]
    print(f"{season}: {premier['Equipo'].tolist()}")
```

### Récords por División

| División        | Récord de Puntos | Equipo        | Temporada |
|-----------------|------------------|---------------|-----------|
| Premier League  | 100 pts          | Man City      | 2017-18   |
| Championship    | 106 pts          | Reading       | 2005-06   |
| League One      | 111 pts          | Birmingham    | 2024-25   |
| League Two      | 99 pts           | Northampton   | 2015-16   |
| National League | 111 pts          | Wrexham       | 2022-23   |

## 🏆 Top 10 Equipos Históricos (Premier League)

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

## 🎢 Equipos con Mayor Movilidad (Todas las Divisiones)

| Equipo       | Temporadas | Divisiones Jugadas | Mejor División |
|--------------|------------|--------------------|----------------|
| Luton        | 25         | 5                  | Premier League |
| Coventry     | 28         | 4                  | Championship   |
| Bolton       | 29         | 4                  | Championship   |
| Portsmouth   | 23         | 4                  | Championship   |
| Bournemouth  | 20         | 4                  | Championship   |

## 📌 Notas Importantes

1. **Temporada 1992-93 no incluida**: football-data.co.uk empieza en 1993-94
2. **Temporada 2024-25**: Datos parciales (temporada en curso)
3. **Nombres de equipos**: Formato estándar (ej: "Man United" en lugar de "Manchester United F.C.")

## 🔄 Historia del Proyecto

### v3.0 - Fase 3: English Football Pyramid Expansion (Enero 2025) ⭐
- ✅ Extensión a 5 divisiones completas del fútbol inglés
- ✅ 2,516 registros totales verificados (0 errores)
- ✅ 159 equipos únicos rastreados
- ✅ Tracking longitudinal con seguimiento de ascensos/descensos
- ✅ Arquitectura modular con clase base abstracta
- ✅ Compatibilidad total con dataset Premier League v2.0

### v2.0 - Premier League Data (Octubre 2024)
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