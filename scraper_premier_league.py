"""
Premier League Scraper - MEJORADO para football-data.co.uk
Maneja diferentes formatos de CSV según la temporada
"""

import pandas as pd
import requests
import time
import logging
from io import StringIO
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def get_football_data_url(season):
    """Construye URL para football-data.co.uk"""
    year = int(season.split('-')[0])
    next_year_short = season.split('-')[1]
    
    # Formato: 9900.csv, 0001.csv, 0102.csv, etc.
    code = f"{str(year)[-2:]}{next_year_short}"
    
    # E0 = Premier League (England Division 0)
    url = f"https://www.football-data.co.uk/mmz4281/{code}/E0.csv"
    return url


def clean_team_name(name):
    """Limpia nombres de equipos"""
    if pd.isna(name):
        return None
    return str(name).strip()


def safe_int_conversion(value):
    """Convierte a entero de forma segura"""
    try:
        if pd.isna(value):
            return 0
        if isinstance(value, str):
            # Eliminar espacios y caracteres no numéricos
            cleaned = ''.join(c for c in value if c.isdigit() or c == '.')
            if cleaned:
                return int(float(cleaned))
        return int(value)
    except:
        return 0


def download_season(season):
    """Descarga y procesa una temporada con manejo robusto de errores"""
    url = get_football_data_url(season)
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            logger.warning(f"  ✗ {season}: HTTP {response.status_code}")
            return None
        
        # Intentar diferentes métodos de parsing
        df = None
        
        # Método 1: Standard parsing
        try:
            df = pd.read_csv(StringIO(response.text), encoding='utf-8')
        except:
            pass
        
        # Método 2: Con error_bad_lines=False (para versiones antiguas de pandas)
        if df is None:
            try:
                df = pd.read_csv(StringIO(response.text), encoding='utf-8', 
                               on_bad_lines='skip')  # Nueva sintaxis
            except:
                try:
                    df = pd.read_csv(StringIO(response.text), encoding='utf-8', 
                                   error_bad_lines=False)  # Sintaxis antigua
                except:
                    pass
        
        # Método 3: Con encoding diferente
        if df is None:
            try:
                df = pd.read_csv(StringIO(response.text), encoding='latin-1')
            except:
                pass
        
        if df is None:
            logger.warning(f"  ✗ {season}: No se pudo parsear el CSV")
            return None
        
        # Limpiar el dataframe
        df = df.dropna(subset=['HomeTeam', 'AwayTeam'], how='any')
        
        # Verificar columnas requeridas
        required_cols = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            logger.warning(f"  ✗ {season}: Columnas faltantes: {missing_cols}")
            return None
        
        # Limpiar nombres de equipos
        df['HomeTeam'] = df['HomeTeam'].apply(clean_team_name)
        df['AwayTeam'] = df['AwayTeam'].apply(clean_team_name)
        
        # Eliminar filas con equipos nulos después de limpieza
        df = df.dropna(subset=['HomeTeam', 'AwayTeam'])
        
        # Convertir goles a números de forma segura
        df['FTHG'] = df['FTHG'].apply(safe_int_conversion)
        df['FTAG'] = df['FTAG'].apply(safe_int_conversion)
        
        # Filtrar solo partidos válidos (con resultado)
        df = df[df['FTR'].isin(['H', 'D', 'A'])]
        
        if len(df) == 0:
            logger.warning(f"  ✗ {season}: Sin partidos válidos")
            return None
        
        # Calcular tabla de clasificación
        teams = sorted(set(df['HomeTeam'].tolist() + df['AwayTeam'].tolist()))
        
        standings = []
        for team in teams:
            home = df[df['HomeTeam'] == team]
            away = df[df['AwayTeam'] == team]
            
            pj = len(home) + len(away)
            
            if pj == 0:
                continue
            
            # Victorias
            w_home = len(home[home['FTR'] == 'H'])
            w_away = len(away[away['FTR'] == 'A'])
            w = w_home + w_away
            
            # Empates
            d_home = len(home[home['FTR'] == 'D'])
            d_away = len(away[away['FTR'] == 'D'])
            d = d_home + d_away
            
            # Derrotas
            l = pj - w - d
            
            # Goles (usando conversión segura)
            gf = int(home['FTHG'].sum() + away['FTAG'].sum())
            gc = int(home['FTAG'].sum() + away['FTHG'].sum())
            gd = gf - gc
            
            # Puntos
            pts = 3 * w + d
            
            standings.append({
                'Equipo': team,
                'PJ': pj,
                'G': w,
                'E': d,
                'P': l,
                'GF': gf,
                'GC': gc,
                'Dif': gd,
                'Pts': pts
            })
        
        if not standings:
            logger.warning(f"  ✗ {season}: Sin datos de equipos")
            return None
        
        # Crear DataFrame y ordenar
        standings_df = pd.DataFrame(standings)
        standings_df = standings_df.sort_values(
            ['Pts', 'Dif', 'GF'], 
            ascending=[False, False, False]
        ).reset_index(drop=True)
        
        standings_df['Pos'] = range(1, len(standings_df) + 1)
        standings_df['Temporada'] = season
        
        # Formatear Dif como string con signo
        standings_df['Dif'] = standings_df['Dif'].apply(
            lambda x: f"+{x}" if x > 0 else str(x)
        )
        
        # Reordenar columnas
        standings_df = standings_df[[
            'Temporada', 'Pos', 'Equipo', 'PJ', 'G', 'E', 'P', 
            'Pts', 'GF', 'GC', 'Dif'
        ]]
        
        logger.info(f"  ✓ {season}: {len(standings_df)} equipos")
        return standings_df
        
    except Exception as e:
        logger.warning(f"  ✗ {season}: Error inesperado: {str(e)}")
        return None


def debug_season(season):
    """Función para debuggear una temporada específica"""
    url = get_football_data_url(season)
    
    logger.info(f"\nDEBUG {season}")
    logger.info(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        logger.info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # Mostrar primeras líneas
            lines = response.text.split('\n')[:5]
            for i, line in enumerate(lines):
                logger.info(f"Línea {i}: {line[:100]}...")
            
            # Intentar leer con diferentes métodos
            try:
                df = pd.read_csv(StringIO(response.text))
                logger.info(f"Columnas: {list(df.columns[:10])}")
                logger.info(f"Filas: {len(df)}")
                
                # Verificar tipos de datos problemáticos
                if 'FTHG' in df.columns:
                    logger.info(f"FTHG tipos: {df['FTHG'].dtype}")
                    logger.info(f"FTHG únicos: {df['FTHG'].unique()[:10]}")
                
            except Exception as e:
                logger.info(f"Error al parsear: {e}")
                
    except Exception as e:
        logger.info(f"Error de descarga: {e}")


def scrape_all_seasons(start_year=1993, end_year=2025, debug_failed=False):
    """Descarga todas las temporadas con opción de debug"""
    
    logger.info("="*70)
    logger.info("PREMIER LEAGUE DATA - football-data.co.uk (VERSIÓN MEJORADA)")
    logger.info("="*70)
    logger.info("")
    
    all_data = []
    failed = []
    
    for year in range(start_year, end_year):
        next_year = year + 1
        season = f"{year}-{str(next_year)[-2:]}"
        
        df = download_season(season)
        
        if df is not None:
            all_data.append(df)
        else:
            failed.append(season)
        
        # Pausa para no sobrecargar el servidor
        time.sleep(0.5)
    
    # Debug de temporadas fallidas si se solicita
    if debug_failed and failed:
        logger.info("\n" + "="*70)
        logger.info("DEBUGGING TEMPORADAS FALLIDAS")
        logger.info("="*70)
        for season in failed[:2]:  # Debug solo las primeras 2
            debug_season(season)
    
    logger.info("")
    logger.info("="*70)
    logger.info("RESUMEN")
    logger.info("="*70)
    logger.info(f"✓ Temporadas exitosas: {len(all_data)}")
    logger.info(f"✗ Temporadas fallidas: {len(failed)}")
    
    if failed:
        logger.info(f"\nTemporadas fallidas: {', '.join(failed)}")
    
    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        
        # Validar datos
        logger.info("")
        logger.info("="*70)
        logger.info("VALIDACIÓN")
        logger.info("="*70)
        
        # Verificar G + E + P = PJ
        combined['Suma'] = combined['G'] + combined['E'] + combined['P']
        problemas_pj = (combined['Suma'] != combined['PJ']).sum()
        
        # Verificar Pts = 3*G + E
        combined['Pts_Calc'] = 3 * combined['G'] + combined['E']
        problemas_pts = (combined['Pts_Calc'] != combined['Pts']).sum()
        
        logger.info(f"Registros con G+E+P != PJ: {problemas_pj}")
        logger.info(f"Registros con Pts != 3*G+E: {problemas_pts}")
        
        if problemas_pj == 0 and problemas_pts == 0:
            logger.info("\n✅ TODOS LOS DATOS SON 100% CONSISTENTES!")
        
        # Guardar
        output = 'premier_league_COMPLETO_football_data.csv'
        combined_clean = combined[[
            'Temporada', 'Pos', 'Equipo', 'PJ', 'G', 'E', 'P', 
            'Pts', 'GF', 'GC', 'Dif'
        ]]
        combined_clean.to_csv(output, index=False, encoding='utf-8-sig')
        
        logger.info("")
        logger.info("="*70)
        logger.info("DATOS GUARDADOS")
        logger.info("="*70)
        logger.info(f"Archivo: {output}")
        logger.info(f"Total registros: {len(combined_clean):,}")
        logger.info(f"Temporadas: {combined_clean['Temporada'].nunique()}")
        logger.info(f"Equipos únicos: {combined_clean['Equipo'].nunique()}")
        
        # Crear tracking
        create_tracking(combined_clean)
        
        return combined_clean
    
    return None


def create_tracking(df):
    """Crea base de datos de tracking"""
    logger.info("")
    logger.info("Creando tracking de equipos...")
    
    all_teams = sorted(df['Equipo'].unique())
    all_seasons = sorted(df['Temporada'].unique())
    
    tracking = []
    for team in all_teams:
        row = {'Equipo': team}
        
        for season in all_seasons:
            data = df[(df['Equipo'] == team) & (df['Temporada'] == season)]
            if len(data) > 0:
                row[f'{season}_Pos'] = data.iloc[0]['Pos']
                row[f'{season}_Pts'] = data.iloc[0]['Pts']
            else:
                row[f'{season}_Pos'] = None
                row[f'{season}_Pts'] = None
        
        tracking.append(row)
    
    tracking_df = pd.DataFrame(tracking)
    tracking_df['Total_Temporadas'] = tracking_df.filter(regex='_Pos').notna().sum(axis=1)
    tracking_df['Mejor_Posicion'] = tracking_df.filter(regex='_Pos').min(axis=1)
    tracking_df['Peor_Posicion'] = tracking_df.filter(regex='_Pos').max(axis=1)
    tracking_df = tracking_df.sort_values('Total_Temporadas', ascending=False)
    
    output = 'premier_league_tracking_COMPLETO.csv'
    tracking_df.to_csv(output, index=False, encoding='utf-8-sig')
    
    logger.info(f"✓ Tracking guardado: {output}")
    logger.info(f"  {len(tracking_df)} equipos únicos")
    
    logger.info("")
    logger.info("Top 10 equipos por temporadas:")
    print(tracking_df[['Equipo', 'Total_Temporadas', 'Mejor_Posicion', 'Peor_Posicion']].head(10).to_string(index=False))
    
    logger.info("")
    logger.info("="*70)
    logger.info("✅ PROCESO COMPLETADO")
    logger.info("="*70)


if __name__ == "__main__":
    # Ejecutar con debug para las temporadas fallidas
    scrape_all_seasons(1993, 2025, debug_failed=True)
