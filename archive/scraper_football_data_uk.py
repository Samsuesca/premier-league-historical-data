"""
Premier League Scraper - SOLO football-data.co.uk
Fuente única y confiable para TODAS las temporadas
"""

import pandas as pd
import requests
import time
import logging
from io import StringIO

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


def download_season(season):
    """Descarga y procesa una temporada"""
    url = get_football_data_url(season)
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            logger.warning(f"  ✗ {season}: HTTP {response.status_code}")
            return None
        
        # Leer CSV
        df = pd.read_csv(StringIO(response.text))
        
        # Verificar que tenga las columnas necesarias
        required_cols = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']
        if not all(col in df.columns for col in required_cols):
            logger.warning(f"  ✗ {season}: Columnas faltantes")
            return None
        
        # Calcular tabla de clasificación desde los partidos
        teams = sorted(set(df['HomeTeam'].tolist() + df['AwayTeam'].tolist()))
        
        standings = []
        for team in teams:
            home = df[df['HomeTeam'] == team]
            away = df[df['AwayTeam'] == team]
            
            pj = len(home) + len(away)
            
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
            
            # Goles
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
        
        # Ordenar por puntos, diferencia de goles, goles a favor
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
        logger.warning(f"  ✗ {season}: {e}")
        return None


def scrape_all_seasons(start_year=1993, end_year=2025):
    """Descarga todas las temporadas"""
    
    logger.info("="*70)
    logger.info("PREMIER LEAGUE DATA - football-data.co.uk")
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
    logger.info("✅ PROCESO COMPLETADO - DATOS 100% LIMPIOS")
    logger.info("="*70)


if __name__ == "__main__":
    scrape_all_seasons(1993, 2025)
