"""
English Football Pyramid Scraper - Fase 3 Expansion
Extiende el proyecto para incluir todas las divisiones del fútbol inglés (niveles 1-5)

Mantiene compatibilidad total con el dataset Premier League v2.0
Arquitectura modular con clase base y configuraciones específicas por división
"""

import pandas as pd
import requests
import time
import logging
from io import StringIO
from abc import ABC, abstractmethod
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class EnglishLeagueScraper(ABC):
    """Clase base abstracta para scrapers de ligas inglesas"""

    def __init__(self, division_name, division_code, expected_teams, start_year=1993, end_year=2025):
        """
        Args:
            division_name (str): Nombre de la división (e.g., "Championship")
            division_code (str): Código football-data.co.uk (e.g., "E1")
            expected_teams (int or tuple): Número esperado de equipos (o rango)
            start_year (int): Año inicial de descarga
            end_year (int): Año final de descarga
        """
        self.division_name = division_name
        self.division_code = division_code
        self.expected_teams = expected_teams
        self.start_year = start_year
        self.end_year = end_year

    def get_url(self, season):
        """Construye URL para football-data.co.uk"""
        year = int(season.split('-')[0])
        next_year_short = season.split('-')[1]
        code = f"{str(year)[-2:]}{next_year_short}"
        url = f"https://www.football-data.co.uk/mmz4281/{code}/{self.division_code}.csv"
        return url

    def clean_team_name(self, name):
        """Limpia nombres de equipos"""
        if pd.isna(name):
            return None
        return str(name).strip()

    def safe_int_conversion(self, value):
        """Convierte a entero de forma segura"""
        try:
            if pd.isna(value):
                return 0
            if isinstance(value, str):
                cleaned = ''.join(c for c in value if c.isdigit() or c == '.')
                if cleaned:
                    return int(float(cleaned))
            return int(value)
        except:
            return 0

    def download_season(self, season):
        """Descarga y procesa una temporada con manejo robusto de errores"""
        url = self.get_url(season)

        try:
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                logger.warning(f"  ✗ {self.division_name} {season}: HTTP {response.status_code}")
                return None

            # Intentar diferentes métodos de parsing
            df = None

            # Método 1: Standard parsing
            try:
                df = pd.read_csv(StringIO(response.text), encoding='utf-8')
            except:
                pass

            # Método 2: Con error handling
            if df is None:
                try:
                    df = pd.read_csv(StringIO(response.text), encoding='utf-8', on_bad_lines='skip')
                except:
                    try:
                        df = pd.read_csv(StringIO(response.text), encoding='utf-8', error_bad_lines=False)
                    except:
                        pass

            # Método 3: Con encoding diferente
            if df is None:
                try:
                    df = pd.read_csv(StringIO(response.text), encoding='latin-1')
                except:
                    pass

            if df is None:
                logger.warning(f"  ✗ {self.division_name} {season}: No se pudo parsear el CSV")
                return None

            # Limpiar el dataframe
            df = df.dropna(subset=['HomeTeam', 'AwayTeam'], how='any')

            # Verificar columnas requeridas
            required_cols = ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']
            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                logger.warning(f"  ✗ {self.division_name} {season}: Columnas faltantes: {missing_cols}")
                return None

            # Limpiar nombres de equipos
            df['HomeTeam'] = df['HomeTeam'].apply(self.clean_team_name)
            df['AwayTeam'] = df['AwayTeam'].apply(self.clean_team_name)

            # Eliminar filas con equipos nulos
            df = df.dropna(subset=['HomeTeam', 'AwayTeam'])

            # Convertir goles a números
            df['FTHG'] = df['FTHG'].apply(self.safe_int_conversion)
            df['FTAG'] = df['FTAG'].apply(self.safe_int_conversion)

            # Filtrar solo partidos válidos
            df = df[df['FTR'].isin(['H', 'D', 'A'])]

            if len(df) == 0:
                logger.warning(f"  ✗ {self.division_name} {season}: Sin partidos válidos")
                return None

            # Calcular tabla de clasificación
            standings_df = self.calculate_standings(df, season)

            if standings_df is None:
                return None

            # Validar número de equipos
            if not self.validate_team_count(len(standings_df)):
                logger.warning(f"  ✗ {self.division_name} {season}: {len(standings_df)} equipos (esperado: {self.expected_teams})")
                return None

            logger.info(f"  ✓ {self.division_name} {season}: {len(standings_df)} equipos")
            return standings_df

        except Exception as e:
            logger.warning(f"  ✗ {self.division_name} {season}: Error inesperado: {str(e)}")
            return None

    def calculate_standings(self, df, season):
        """Calcula tabla de clasificación desde datos de partidos"""
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

        if not standings:
            logger.warning(f"  ✗ {self.division_name} {season}: Sin datos de equipos")
            return None

        # Crear DataFrame y ordenar
        standings_df = pd.DataFrame(standings)
        standings_df = standings_df.sort_values(
            ['Pts', 'Dif', 'GF'],
            ascending=[False, False, False]
        ).reset_index(drop=True)

        standings_df['Pos'] = range(1, len(standings_df) + 1)
        standings_df['Temporada'] = season
        standings_df['Division'] = self.division_name

        # Formatear Dif como string con signo
        standings_df['Dif'] = standings_df['Dif'].apply(
            lambda x: f"+{x}" if x > 0 else str(x)
        )

        # Reordenar columnas
        standings_df = standings_df[[
            'Temporada', 'Division', 'Pos', 'Equipo', 'PJ', 'G', 'E', 'P',
            'Pts', 'GF', 'GC', 'Dif'
        ]]

        return standings_df

    def validate_team_count(self, count):
        """Valida que el número de equipos sea el esperado"""
        if isinstance(self.expected_teams, tuple):
            return self.expected_teams[0] <= count <= self.expected_teams[1]
        return count == self.expected_teams

    def scrape_all_seasons(self):
        """Descarga todas las temporadas de esta división"""
        all_data = []
        failed = []

        for year in range(self.start_year, self.end_year):
            next_year = year + 1
            season = f"{year}-{str(next_year)[-2:]}"

            df = self.download_season(season)

            if df is not None:
                all_data.append(df)
            else:
                failed.append(season)

            # Pausa para no sobrecargar el servidor
            time.sleep(0.5)

        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            return combined, failed

        return None, failed


class PremierLeagueScraper(EnglishLeagueScraper):
    """Scraper para Premier League (Nivel 1)"""
    def __init__(self, start_year=1993, end_year=2025):
        super().__init__(
            division_name="Premier League",
            division_code="E0",
            expected_teams=(20, 22),  # 1993-95: 22 equipos, 1995+: 20 equipos
            start_year=start_year,
            end_year=end_year
        )


class ChampionshipScraper(EnglishLeagueScraper):
    """
    Scraper para Championship/First Division (Nivel 2)

    Nota histórica:
    - 1993-2004: Se llamaba "First Division"
    - 2004-presente: Renombrada a "Championship"
    Usamos nombre moderno "Championship" para consistencia en el dataset
    """
    def __init__(self, start_year=1993, end_year=2025):
        super().__init__(
            division_name="Championship",
            division_code="E1",
            expected_teams=24,
            start_year=start_year,
            end_year=end_year
        )


class LeagueOneScraper(EnglishLeagueScraper):
    """
    Scraper para League One/Second Division (Nivel 3)

    Nota histórica:
    - 1993-2004: Se llamaba "Second Division"
    - 2004-presente: Renombrada a "League One"
    Usamos nombre moderno "League One" para consistencia en el dataset
    """
    def __init__(self, start_year=1993, end_year=2025):
        super().__init__(
            division_name="League One",
            division_code="E2",
            expected_teams=24,
            start_year=start_year,
            end_year=end_year
        )


class LeagueTwoScraper(EnglishLeagueScraper):
    """
    Scraper para League Two/Third Division (Nivel 4)

    Nota histórica:
    - 1993-2004: Se llamaba "Third Division"
    - 2004-presente: Renombrada a "League Two"
    Usamos nombre moderno "League Two" para consistencia en el dataset
    """
    def __init__(self, start_year=1993, end_year=2025):
        super().__init__(
            division_name="League Two",
            division_code="E3",
            expected_teams=24,
            start_year=start_year,
            end_year=end_year
        )


class NationalLeagueScraper(EnglishLeagueScraper):
    """Scraper para National League (Nivel 5)"""
    def __init__(self, start_year=2005, end_year=2025):  # Datos disponibles desde 2005
        super().__init__(
            division_name="National League",
            division_code="EC",
            expected_teams=24,
            start_year=start_year,
            end_year=end_year
        )


def scrape_all_divisions():
    """Ejecuta el scraping de todas las divisiones con datos históricos completos (1993-2025)"""

    logger.info("="*70)
    logger.info("ENGLISH FOOTBALL PYRAMID - FULL HISTORICAL DATA (1993-2025)")
    logger.info("="*70)
    logger.info("")
    logger.info("Nota: Championship/League One/League Two usan códigos E1/E2/E3")
    logger.info("que existían desde 1993 con nombres históricos diferentes:")
    logger.info("  - E1: First Division (1993-2004) → Championship (2004-presente)")
    logger.info("  - E2: Second Division (1993-2004) → League One (2004-presente)")
    logger.info("  - E3: Third Division (1993-2004) → League Two (2004-presente)")
    logger.info("")

    # Definir scrapers para cada división - AHORA CON 32 TEMPORADAS COMPLETAS
    scrapers = [
        PremierLeagueScraper(1993, 2025),      # 32 temporadas
        ChampionshipScraper(1993, 2025),       # 32 temporadas (antes First Division)
        LeagueOneScraper(1993, 2025),          # 32 temporadas (antes Second Division)
        LeagueTwoScraper(1993, 2025),          # 32 temporadas (antes Third Division)
        NationalLeagueScraper(2005, 2025)      # 20 temporadas (datos desde 2005)
    ]

    all_results = []
    summary = []

    for scraper in scrapers:
        logger.info(f"\n{'='*70}")
        logger.info(f"PROCESANDO: {scraper.division_name.upper()}")
        logger.info(f"{'='*70}")

        data, failed = scraper.scrape_all_seasons()

        if data is not None:
            all_results.append(data)

            # Validar datos
            data['Suma'] = data['G'] + data['E'] + data['P']
            data['Pts_Calc'] = 3 * data['G'] + data['E']

            problemas_pj = (data['Suma'] != data['PJ']).sum()
            problemas_pts = (data['Pts_Calc'] != data['Pts']).sum()

            summary.append({
                'Division': scraper.division_name,
                'Temporadas': data['Temporada'].nunique(),
                'Equipos': data['Equipo'].nunique(),
                'Registros': len(data),
                'Errores_PJ': problemas_pj,
                'Errores_Pts': problemas_pts,
                'Temporadas_Fallidas': len(failed)
            })

            logger.info(f"\n✓ {scraper.division_name} completado:")
            logger.info(f"  Temporadas exitosas: {data['Temporada'].nunique()}")
            logger.info(f"  Temporadas fallidas: {len(failed)}")
            logger.info(f"  Total registros: {len(data):,}")
            logger.info(f"  Equipos únicos: {data['Equipo'].nunique()}")
            logger.info(f"  Errores G+E+P != PJ: {problemas_pj}")
            logger.info(f"  Errores Pts != 3*G+E: {problemas_pts}")

            if failed:
                logger.info(f"  Temporadas fallidas: {', '.join(failed[:5])}")
        else:
            summary.append({
                'Division': scraper.division_name,
                'Temporadas': 0,
                'Equipos': 0,
                'Registros': 0,
                'Errores_PJ': 0,
                'Errores_Pts': 0,
                'Temporadas_Fallidas': scraper.end_year - scraper.start_year
            })

    # Combinar todos los datos
    if all_results:
        combined = pd.concat(all_results, ignore_index=True)

        # Guardar CSV unificado
        output_file = 'english_leagues_completo.csv'
        combined_clean = combined[[
            'Temporada', 'Division', 'Pos', 'Equipo', 'PJ', 'G', 'E', 'P',
            'Pts', 'GF', 'GC', 'Dif'
        ]]
        combined_clean.to_csv(output_file, index=False, encoding='utf-8-sig')

        # Resumen general
        logger.info("\n" + "="*70)
        logger.info("RESUMEN GENERAL")
        logger.info("="*70)

        summary_df = pd.DataFrame(summary)
        print(summary_df.to_string(index=False))

        logger.info(f"\n✅ DATOS GUARDADOS: {output_file}")
        logger.info(f"Total registros: {len(combined_clean):,}")
        logger.info(f"Divisiones: {combined_clean['Division'].nunique()}")
        logger.info(f"Temporadas únicas: {combined_clean['Temporada'].nunique()}")
        logger.info(f"Equipos únicos: {combined_clean['Equipo'].nunique()}")

        # Crear tracking
        create_tracking(combined_clean)

        return combined_clean

    return None


def create_tracking(df):
    """Crea base de datos de tracking longitudinal por división"""
    logger.info("")
    logger.info("="*70)
    logger.info("CREANDO TRACKING LONGITUDINAL")
    logger.info("="*70)

    all_teams = sorted(df['Equipo'].unique())
    all_seasons = sorted(df['Temporada'].unique())
    all_divisions = ['Premier League', 'Championship', 'League One', 'League Two', 'National League']

    tracking = []
    for team in all_teams:
        row = {'Equipo': team}

        # Para cada temporada, registrar división y posición
        for season in all_seasons:
            data = df[(df['Equipo'] == team) & (df['Temporada'] == season)]
            if len(data) > 0:
                division = data.iloc[0]['Division']
                row[f'{season}_Division'] = division
                row[f'{season}_Pos'] = data.iloc[0]['Pos']
                row[f'{season}_Pts'] = data.iloc[0]['Pts']
            else:
                row[f'{season}_Division'] = None
                row[f'{season}_Pos'] = None
                row[f'{season}_Pts'] = None

        # Métricas agregadas
        team_data = df[df['Equipo'] == team]
        row['Total_Temporadas'] = len(team_data)
        row['Divisiones_Jugadas'] = team_data['Division'].nunique()
        row['Mejor_Division'] = team_data['Division'].min() if len(team_data) > 0 else None

        # Mejor posición global
        if len(team_data) > 0:
            # Calcular "puntuación" por división: Premier=1, Championship=2, etc.
            division_map = {d: i+1 for i, d in enumerate(all_divisions)}
            team_data['Division_Score'] = team_data['Division'].map(division_map)
            team_data['Global_Score'] = team_data['Division_Score'] * 100 + team_data['Pos']
            row['Mejor_Posicion_Global'] = team_data['Global_Score'].min()
        else:
            row['Mejor_Posicion_Global'] = None

        tracking.append(row)

    tracking_df = pd.DataFrame(tracking)
    tracking_df = tracking_df.sort_values('Total_Temporadas', ascending=False)

    output = 'english_leagues_tracking.csv'
    tracking_df.to_csv(output, index=False, encoding='utf-8-sig')

    logger.info(f"✓ Tracking guardado: {output}")
    logger.info(f"  {len(tracking_df)} equipos únicos rastreados")

    logger.info("")
    logger.info("Top 15 equipos por temporadas jugadas:")
    display_cols = ['Equipo', 'Total_Temporadas', 'Divisiones_Jugadas', 'Mejor_Division']
    print(tracking_df[display_cols].head(15).to_string(index=False))

    logger.info("")
    logger.info("="*70)
    logger.info("✅ EXPANSIÓN FASE 3 COMPLETADA")
    logger.info("="*70)


if __name__ == "__main__":
    scrape_all_divisions()
