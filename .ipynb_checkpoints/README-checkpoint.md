# Premier League Historical Data Scraper

Sistema robusto para extracción y análisis de datos históricos de la Premier League (1992-2025).

## 📋 Descripción

Este proyecto extrae datos completos de todas las temporadas de la Premier League desde su creación en 1992, creando una base de datos estructurada que permite hacer seguimiento histórico de equipos, analizar tendencias y generar estadísticas.

## 🎯 Objetivos

- **Datos completos**: Obtener información de TODAS las temporadas (1992-93 hasta 2024-25)
- **Datos limpios**: Validación estricta de tablas de clasificación vs. otras tablas
- **Tracking de equipos**: Seguimiento histórico de cada equipo a través de los años
- **Análisis robusto**: Funciones para consultas y visualizaciones

## 📁 Estructura del Proyecto

```
futbol/
├── scraper_robusto.py              # Scraper principal con múltiples fuentes
├── analisis_premier_league.ipynb   # Notebook de análisis completo
├── premier_league_completo_limpio.csv        # Datos principales
├── premier_league_tracking_equipos.csv       # Tracking por equipo
└── README.md                       # Este archivo
```

## 🚀 Uso Rápido

### 1. Instalar dependencias

```bash
pip install requests beautifulsoup4 pandas numpy matplotlib seaborn
```

### 2. Ejecutar el Scraper

```python
python scraper_robusto.py
```

Esto genera:
- `premier_league_completo_limpio.csv` - Datos de todas las temporadas
- `premier_league_tracking_equipos.csv` - Matriz de tracking por equipo

### 3. Análisis en Jupyter

```bash
jupyter notebook analisis_premier_league.ipynb
```

## 📊 Estructura de Datos

### Archivo Principal: `premier_league_completo_limpio.csv`

| Columna   | Descripción                      | Tipo    |
|-----------|----------------------------------|---------|
| Temporada | Temporada (ej: "1992-93")       | string  |
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

### Archivo de Tracking: `premier_league_tracking_equipos.csv`

Para cada equipo incluye:
- Columnas `{temporada}_Pos` - Posición en esa temporada
- Columnas `{temporada}_Pts` - Puntos en esa temporada
- `Total_Temporadas` - Número total de temporadas jugadas
- `Mejor_Posicion` - Mejor posición histórica
- `Peor_Posicion` - Peor posición histórica

## 🔧 Características Técnicas

### Validación Robusta

El scraper incluye múltiples capas de validación:

1. **Detección de tabla correcta**: Verifica que sea tabla de clasificación (no de equipos/entrenadores)
2. **Validación de columnas**: Debe contener Pts, PJ, GF, GC
3. **Validación de filas**: Debe tener 20-22 equipos
4. **Fuentes múltiples**: Intenta Wikipedia ES primero, luego EN

### Limpieza de Datos

- Eliminación de referencias `[1]`, `[a]`, etc.
- Normalización de nombres de equipos
- Conversión automática de tipos numéricos
- Manejo de caracteres especiales

## 📖 Funciones de Análisis

### ver_historial_equipo(nombre)

Muestra el historial completo de un equipo:

```python
ver_historial_equipo('Arsenal')
```

### ver_temporada(temporada)

Muestra la tabla de clasificación completa de una temporada:

```python
ver_temporada('2015-16')  # Temporada del Leicester
```

### comparar_equipos(*equipos)

Compara estadísticas de múltiples equipos:

```python
comparar_equipos('Manchester United', 'Liverpool', 'Arsenal')
```

## 📈 Análisis Disponibles

El notebook incluye:

1. **Verificación de calidad**: Valores nulos, temporadas faltantes, anomalías
2. **Equipos siempre en Premier**: Lista de equipos en todas las temporadas
3. **Campeones históricos**: Títulos por equipo
4. **Mejores temporadas**: Top por puntos, goles, etc.
5. **Visualizaciones**: Gráficos de títulos, puntos, tendencias

## 🎯 Casos de Uso

### 1. Seguimiento de un Equipo

```python
# Ver todas las temporadas del Manchester City
historial = df[df['Equipo'].str.contains('Manchester City')]
print(historial[['Temporada', 'Pos', 'Pts']].to_string())
```

### 2. Análisis de Descensos

```python
# Ver todos los equipos que descendieron
descendidos = df[df['Pos'] >= 18]
print(descendidos[['Temporada', 'Equipo', 'Pos', 'Pts']])
```

### 3. Récords Históricos

```python
# Mejor temporada por puntos
mejor = df.loc[df['Pts'].idxmax()]
print(f"{mejor['Equipo']} - {mejor['Temporada']}: {mejor['Pts']} puntos")
```

## ⚠️ Notas Importantes

1. **Temporadas faltantes**: Algunas temporadas pueden fallar si Wikipedia cambia su formato
2. **Nombres de equipos**: Los nombres pueden variar (ej: "Manchester United F.C." vs "Manchester United")
3. **Datos de temporada actual**: La 2024-25 puede estar incompleta si la temporada no ha terminado

## 🔄 Actualización de Datos

Para actualizar con nuevas temporadas:

```python
from scraper_robusto import PremierLeagueScraper

scraper = PremierLeagueScraper()
df_new = scraper.scrape_all_seasons(1992, 2026)  # Añadir 2025-26
```

## 🐛 Solución de Problemas

### Error: "No se encontró tabla de clasificación"

- Verifica que la URL de Wikipedia existe
- Algunas temporadas requieren la versión en inglés
- El scraper automáticamente reintenta con múltiples fuentes

### Error: Número incorrecto de equipos

- Las primeras 3 temporadas tuvieron 22 equipos (1992-95)
- Desde 1995-96 son 20 equipos
- Verifica con: `df.groupby('Temporada').size()`

### Datos inconsistentes

Si encuentras datos que no tienen sentido:
1. Verifica la temporada en Wikipedia manualmente
2. Revisa el log del scraper para ver qué fuente se usó
3. Usa la columna `Fuente` para identificar el origen

## 📝 TODO / Mejoras Futuras

- [ ] Añadir datos de goleadores por temporada
- [ ] Incluir información de entrenadores
- [ ] Agregar datos de asistencias
- [ ] Crear visualizaciones interactivas con Plotly
- [ ] API REST para consultas
- [ ] Base de datos SQLite para mejor rendimiento
- [ ] Scraping de otras ligas europeas

## 🤝 Contribuciones

Este es un proyecto personal de análisis. Si encuentras errores en los datos:

1. Verifica la temporada manualmente en Wikipedia
2. Reporta el problema indicando temporada y equipo
3. Si es posible, sugiere la corrección

## 📄 Licencia

Uso educativo y personal. Los datos pertenecen a sus respectivas fuentes (Wikipedia, Premier League).

## 🙏 Agradecimientos

- Wikipedia por mantener datos históricos detallados
- BeautifulSoup y Pandas por facilitar el scraping y análisis
- La comunidad de fútbol por documentar meticulosamente cada temporada

---

**Última actualización**: Octubre 2024
**Versión**: 1.0
**Autor**: Angel Samuel Suescarios
