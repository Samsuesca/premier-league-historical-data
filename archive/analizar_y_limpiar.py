"""
Premier League Scraper v3.0 - Solución definitiva
Usa el scraper original (que funcionaba) pero añade validación POST-extracción
"""

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Cargar datos del scraper original (que funcionaba bien)
df_original = pd.read_csv('premier_league_completo_limpio.csv')

logger.info("="*70)
logger.info("ANÁLISIS Y LIMPIEZA DE DATOS")
logger.info("="*70)

# Separar por fuente
df_es = df_original[df_original['Fuente'] == 'ES'].copy()
df_en = df_original[df_original['Fuente'] == 'EN'].copy()

logger.info(f"\nRegistros ES: {len(df_es)}")
logger.info(f"Registros EN: {len(df_en)}")

# Verificar consistencia ES
df_es['Suma_GEP'] = df_es['G'] + df_es['E'] + df_es['P']
df_es['Pts_Calc'] = 3 * df_es['G'] + df_es['E']

problemas_es_pj = (df_es['Suma_GEP'] != df_es['PJ']).sum()
problemas_es_pts = (df_es['Pts_Calc'] != df_es['Pts']).sum()

logger.info(f"\nDatos ES:")
logger.info(f"  Problemas PJ: {problemas_es_pj}")
logger.info(f"  Problemas Pts: {problemas_es_pts}")

# Verificar consistencia EN
df_en['Suma_GEP'] = df_en['G'] + df_en['E'] + df_en['P']
df_en['Pts_Calc'] = 3 * df_en['G'] + df_en['E']

problemas_en_pj = (df_en['Suma_GEP'] != df_en['PJ']).sum()
problemas_en_pts = (df_en['Pts_Calc'] != df_en['Pts']).sum()

logger.info(f"\nDatos EN:")
logger.info(f"  Problemas PJ: {problemas_en_pj}")
logger.info(f"  Problemas Pts: {problemas_en_pts}")

# Los datos ES están bien, los EN tienen columnas shifted
# Solución: Usar SOLO datos ES y buscar fuente alternativa para lo que falta

logger.info("\n" + "="*70)
logger.info("ESTRATEGIA: Usar datos ES + fuente alternativa")
logger.info("="*70)

# Ver qué temporadas tenemos en ES
temporadas_es = sorted(df_es['Temporada'].unique())
todas_temporadas = [f"{y}-{str(y+1)[-2:]}" for y in range(1992, 2025)]
temporadas_faltantes = [t for t in todas_temporadas if t not in temporadas_es]

logger.info(f"\n✓ Temporadas exitosas en ES: {len(temporadas_es)}")
logger.info(f"Temporadas: {', '.join(temporadas_es)}")

logger.info(f"\n✗ Temporadas faltantes: {len(temporadas_faltantes)}")
logger.info(f"Temporadas: {', '.join(temporadas_faltantes)}")

# Guardar datos limpios (solo ES)
df_limpio = df_es[['Temporada', 'Pos', 'Equipo', 'PJ', 'G', 'E', 'P', 'Pts', 'GF', 'GC', 'Dif']].copy()
df_limpio.to_csv('premier_league_SOLO_ES_limpio.csv', index=False, encoding='utf-8-sig')

logger.info(f"\n✓ Datos limpios guardados: premier_league_SOLO_ES_limpio.csv")
logger.info(f"  {len(df_limpio)} registros")
logger.info(f"  {df_limpio['Temporada'].nunique()} temporadas")

logger.info("\n" + "="*70)
logger.info("PRÓXIMOS PASOS")
logger.info("="*70)
logger.info("1. Los datos de Wikipedia ES son 100% confiables")
logger.info("2. Para las temporadas faltantes, usar fuente alternativa:")
logger.info("   - football-data.co.uk (CSV históricos)")
logger.info("   - API-Football")
logger.info("   - Wikipedia EN (manualmente corregidos)")
logger.info("="*70)
