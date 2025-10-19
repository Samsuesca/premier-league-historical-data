"""
Script de Verificación Extendida - English Football Pyramid
Valida que los datos de todas las divisiones estén correctos y completos
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

log_filename = log_dir / f'verificar_english_leagues_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info(f"Logging iniciado - archivo: {log_filename}")

print("="*70)
print("VERIFICACIÓN DE DATOS - English Football Pyramid")
print("="*70)
logger.info("Iniciando verificación de datos de English Football Pyramid")

# Cargar datos
try:
    df = pd.read_csv('english_leagues_completo.csv')
    tracking = pd.read_csv('english_leagues_tracking.csv')
    print("\n✅ Archivos cargados correctamente")
except FileNotFoundError as e:
    print(f"\n❌ Error: {e}")
    print("Ejecuta primero: python scraper_english_leagues.py")
    exit(1)

# Verificar datos principales
print("\n" + "="*70)
print("DATOS PRINCIPALES")
print("="*70)
print(f"Total registros: {len(df):,}")
print(f"Divisiones: {df['Division'].nunique()}")
print(f"Temporadas: {df['Temporada'].nunique()}")
print(f"Equipos únicos: {df['Equipo'].nunique()}")

# Validar consistencia
print("\n" + "="*70)
print("VALIDACIÓN DE CONSISTENCIA")
print("="*70)

df['Suma_GEP'] = df['G'] + df['E'] + df['P']
df['Pts_Calc'] = 3 * df['G'] + df['E']

error_pj = (df['Suma_GEP'] != df['PJ']).sum()
error_pts = (df['Pts_Calc'] != df['Pts']).sum()

print(f"Errores G+E+P != PJ: {error_pj}")
print(f"Errores Pts != 3*G+E: {error_pts}")

if error_pj == 0 and error_pts == 0:
    print("\n✅ TODOS LOS DATOS SON 100% CONSISTENTES")
else:
    print("\n⚠️  ATENCIÓN: Hay inconsistencias en los datos")
    if error_pj > 0:
        problemas_pj = df[df['Suma_GEP'] != df['PJ']]
        print(f"\nRegistros con error G+E+P != PJ:")
        print(problemas_pj[['Temporada', 'Division', 'Equipo', 'PJ', 'G', 'E', 'P']].head())
    if error_pts > 0:
        problemas_pts = df[df['Pts_Calc'] != df['Pts']]
        print(f"\nRegistros con error Pts != 3*G+E:")
        print(problemas_pts[['Temporada', 'Division', 'Equipo', 'Pts', 'Pts_Calc']].head())

# Validación por división
print("\n" + "="*70)
print("VALIDACIÓN POR DIVISIÓN")
print("="*70)

divisiones_esperadas = {
    'Premier League': (20, 22),  # 1993-95: 22, después 20
    'Championship': 24,
    'League One': 24,
    'League Two': 24,
    'National League': 24
}

for division in df['Division'].unique():
    div_data = df[df['Division'] == division]
    temporadas = div_data.groupby('Temporada').size()

    print(f"\n{division}:")
    print(f"  Temporadas: {temporadas.nunique()}")
    print(f"  Total registros: {len(div_data)}")
    print(f"  Equipos únicos: {div_data['Equipo'].nunique()}")

    # Verificar número de equipos por temporada
    esperado = divisiones_esperadas[division]
    if isinstance(esperado, tuple):
        min_exp, max_exp = esperado
        anomalias = temporadas[(temporadas < min_exp) | (temporadas > max_exp)]
    else:
        anomalias = temporadas[temporadas != esperado]

    if len(anomalias) > 0:
        print(f"  ⚠️  Temporadas con número anómalo de equipos:")
        for temp, count in anomalias.items():
            print(f"     {temp}: {count} equipos (esperado: {esperado})")
    else:
        print(f"  ✅ Todas las temporadas tienen el número correcto de equipos")

# Verificar temporadas
print("\n" + "="*70)
print("COBERTURA TEMPORAL")
print("="*70)

temporadas = sorted(df['Temporada'].unique())
print(f"Primera temporada: {temporadas[0]}")
print(f"Última temporada: {temporadas[-1]}")
print(f"Total: {len(temporadas)} temporadas")

print(f"\nDistribución de registros por temporada:")
registros_por_temp = df.groupby('Temporada').size()
print(f"  Mínimo: {registros_por_temp.min()} equipos")
print(f"  Máximo: {registros_por_temp.max()} equipos")
print(f"  Promedio: {registros_por_temp.mean():.1f} equipos")

# Tracking
print("\n" + "="*70)
print("TRACKING DE EQUIPOS")
print("="*70)
print(f"Equipos en tracking: {len(tracking)}")

if 'Total_Temporadas' in tracking.columns:
    temp_max = tracking['Total_Temporadas'].max()
    equipos_32_temp = tracking[tracking['Total_Temporadas'] == temp_max]

    print(f"\nEquipos con más temporadas rastreadas ({int(temp_max)}):")
    for _, row in equipos_32_temp.head(10).iterrows():
        divisiones = row.get('Divisiones_Jugadas', 'N/A')
        mejor_div = row.get('Mejor_Division', 'N/A')
        print(f"  - {row['Equipo']}: {int(row['Total_Temporadas'])} temporadas, {divisiones} divisiones, mejor: {mejor_div}")

# Análisis de movilidad entre divisiones
print("\n" + "="*70)
print("ANÁLISIS DE MOVILIDAD")
print("="*70)

equipos_multidivision = tracking[tracking['Divisiones_Jugadas'] > 1] if 'Divisiones_Jugadas' in tracking.columns else pd.DataFrame()

if len(equipos_multidivision) > 0:
    print(f"Equipos que han jugado en múltiples divisiones: {len(equipos_multidivision)}")

    # Top 10 equipos más viajados
    equipos_mas_viajados = equipos_multidivision.nlargest(10, 'Divisiones_Jugadas')
    print(f"\nTop 10 equipos con más movilidad entre divisiones:")
    for _, row in equipos_mas_viajados.iterrows():
        print(f"  - {row['Equipo']}: {int(row['Divisiones_Jugadas'])} divisiones diferentes")

# Resumen comparativo
print("\n" + "="*70)
print("RESUMEN COMPARATIVO")
print("="*70)

resumen = df.groupby('Division').agg({
    'Temporada': 'nunique',
    'Equipo': 'nunique',
    'PJ': 'sum',
    'GF': 'sum',
    'GC': 'sum',
    'Pts': 'sum'
}).reset_index()

resumen.columns = ['Division', 'Temporadas', 'Equipos', 'Total_Partidos', 'Total_GF', 'Total_GC', 'Total_Pts']
resumen['Registros'] = df.groupby('Division').size().values

# Ordenar por nivel de división
division_order = ['Premier League', 'Championship', 'League One', 'League Two', 'National League']
resumen['Order'] = resumen['Division'].map({div: i for i, div in enumerate(division_order)})
resumen = resumen.sort_values('Order').drop('Order', axis=1)

print(resumen.to_string(index=False))

# Estadísticas interesantes
print("\n" + "="*70)
print("ESTADÍSTICAS DESTACADAS")
print("="*70)

# Equipo con más puntos en una temporada por división
for division in division_order:
    div_data = df[df['Division'] == division]
    if len(div_data) > 0:
        mejor_temp = div_data.nlargest(1, 'Pts').iloc[0]
        print(f"\n{division}:")
        print(f"  Récord de puntos: {mejor_temp['Equipo']} - {mejor_temp['Pts']} pts ({mejor_temp['Temporada']})")

# Verificar valores nulos
print("\n" + "="*70)
print("CALIDAD DE DATOS")
print("="*70)
print(f"Valores nulos en dataset principal: {df.isnull().sum().sum()}")
print(f"Valores nulos en tracking: {tracking.isnull().sum().sum() - tracking.filter(regex='_').isnull().sum().sum()} (excluyendo temporadas sin jugar)")

print("\n" + "="*70)
print("✅ VERIFICACIÓN COMPLETADA")
print("="*70)
print("\nTodo está listo para análisis de múltiples divisiones!")
print("Dataset principal: english_leagues_completo.csv")
print("Tracking: english_leagues_tracking.csv")
