"""
Script de Verificación Rápida
Valida que los datos estén correctos y completos
"""

import pandas as pd
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

log_filename = log_dir / f'verificar_datos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

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
print("VERIFICACIÓN DE DATOS - Premier League")
print("="*70)
logger.info("Iniciando verificación de datos de Premier League")

# Cargar datos
try:
    df = pd.read_csv('premier_league_COMPLETO_football_data.csv')
    tracking = pd.read_csv('premier_league_tracking_COMPLETO.csv')
    print("\n✅ Archivos cargados correctamente")
except FileNotFoundError as e:
    print(f"\n❌ Error: {e}")
    print("Ejecuta primero: python scraper_premier_league.py")
    exit(1)

# Verificar datos principales
print("\n" + "="*70)
print("DATOS PRINCIPALES")
print("="*70)
print(f"Total registros: {len(df):,}")
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

# Verificar temporadas
print("\n" + "="*70)
print("COBERTURA TEMPORAL")
print("="*70)

temporadas = sorted(df['Temporada'].unique())
print(f"Primera temporada: {temporadas[0]}")
print(f"Última temporada: {temporadas[-1]}")
print(f"Total: {len(temporadas)} temporadas")

# Equipos por temporada
equipos_por_temp = df.groupby('Temporada').size()
print(f"\nEquipos por temporada:")
print(f"  Mínimo: {equipos_por_temp.min()}")
print(f"  Máximo: {equipos_por_temp.max()}")
print(f"  Promedio: {equipos_por_temp.mean():.1f}")

# Tracking
print("\n" + "="*70)
print("TRACKING DE EQUIPOS")
print("="*70)
print(f"Equipos en tracking: {len(tracking)}")

temp_completas = tracking['Total_Temporadas'].max()
siempre_premier = tracking[tracking['Total_Temporadas'] == temp_completas]
print(f"\nEquipos en TODAS las {int(temp_completas)} temporadas:")
for _, row in siempre_premier.iterrows():
    print(f"  - {row['Equipo']}")

# Top campeones
print("\n" + "="*70)
print("TOP CAMPEONES HISTÓRICOS")
print("="*70)

campeones = df[df['Pos'] == 1]
titulos = campeones.groupby('Equipo').size().sort_values(ascending=False)

for i, (equipo, count) in enumerate(titulos.head(5).items(), 1):
    print(f"{i}. {equipo}: {count} {'título' if count == 1 else 'títulos'}")

print("\n" + "="*70)
print("✅ VERIFICACIÓN COMPLETADA")
print("="*70)
print("\nTodo está listo para análisis!")
print("Ejecuta: jupyter notebook analisis_premier_league.ipynb")
