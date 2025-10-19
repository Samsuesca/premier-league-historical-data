"""
Premier League Historical Data Scraper
Versión robusta con múltiples fuentes y validación de datos
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from typing import Optional, Dict, List, Tuple
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PremierLeagueScraper:
    """Scraper robusto para datos históricos de Premier League"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.base_url_es = "https://es.wikipedia.org/wiki/Premier_League_{season}"
        self.base_url_en = "https://en.wikipedia.org/wiki/{year}–{next_year}_Premier_League"
        
    def _clean_text(self, text: str) -> str:
        """Limpia texto de caracteres especiales y referencias"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\[.*?\]', '', text)
        text = text.replace('↑', '').replace('↓', '').replace('(C)', '').replace('(D)', '')
        return text.strip()
    
    def _is_classification_table(self, table) -> bool:
        """Verifica si una tabla es una tabla de clasificación válida"""
        try:
            header_row = table.find('tr')
            if not header_row:
                return False
            
            headers_text = header_row.get_text().upper()
            
            # Debe contener columnas de clasificación típicas
            has_points = any(word in headers_text for word in ['PTS', 'PUNTOS', 'POINTS'])
            has_matches = any(word in headers_text for word in ['PJ', 'PARTIDOS', 'PLAYED', 'PLD'])
            has_goals = any(word in headers_text for word in ['GF', 'GOLES', 'GOALS'])
            
            # NO debe ser tabla de equipos/entrenadores
            is_team_info = any(word in headers_text for word in ['ENTRENADOR', 'MANAGER', 'COACH', 'ESTADIO', 'STADIUM', 'CAPITÁN', 'CAPTAIN'])
            
            rows = table.find_all('tr')
            has_enough_rows = len(rows) >= 20  # Al menos 20 equipos
            
            return has_points and has_matches and has_goals and not is_team_info and has_enough_rows
            
        except Exception as e:
            logger.debug(f"Error verificando tabla: {e}")
            return False
    
    def _extract_team_name(self, cell) -> str:
        """Extrae el nombre del equipo de una celda"""
        # Intentar obtener del atributo title del enlace
        link = cell.find('a')
        if link and link.get('title'):
            team_name = link.get('title')
            # Limpiar sufijos comunes
            team_name = team_name.replace(' Football Club', '').replace(' F.C.', '')
            team_name = team_name.replace(' Association Football Club', '')
            return team_name
        
        # Si no hay enlace, usar el texto
        return self._clean_text(cell.get_text())
    
    def scrape_season_wikipedia_es(self, season: str) -> Optional[pd.DataFrame]:
        """Intenta extraer datos de Wikipedia en español"""
        url = self.base_url_es.format(season=season)
        return self._scrape_wikipedia_page(url, season, 'ES')
    
    def scrape_season_wikipedia_en(self, season: str) -> Optional[pd.DataFrame]:
        """Intenta extraer datos de Wikipedia en inglés"""
        year = int(season.split('-')[0])
        next_year = str(year + 1)[-2:]
        url = self.base_url_en.format(year=year, next_year=next_year)
        return self._scrape_wikipedia_page(url, season, 'EN')
    
    def _scrape_wikipedia_page(self, url: str, season: str, lang: str) -> Optional[pd.DataFrame]:
        """Extrae datos de una página de Wikipedia"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar tabla de clasificación
            tables = soup.find_all('table', {'class': 'wikitable'})
            
            for table in tables:
                if self._is_classification_table(table):
                    return self._parse_classification_table(table, season, lang)
            
            logger.warning(f"[{lang}] No se encontró tabla de clasificación válida en {url}")
            return None
            
        except Exception as e:
            logger.error(f"[{lang}] Error extrayendo {url}: {e}")
            return None
    
    def _parse_classification_table(self, table, season: str, lang: str) -> Optional[pd.DataFrame]:
        """Parsea una tabla de clasificación"""
        try:
            rows = table.find_all('tr')
            
            # Extraer encabezados
            header_row = rows[0]
            headers = []
            for th in header_row.find_all(['th', 'td']):
                text = self._clean_text(th.get_text())
                headers.append(text)
            
            # Extraer datos
            data = []
            for row in rows[1:]:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 10:
                    row_data = []
                    for i, col in enumerate(cols):
                        if i == 1:  # Columna del equipo
                            text = self._extract_team_name(col)
                        else:
                            text = self._clean_text(col.get_text())
                        row_data.append(text)
                    
                    if row_data:
                        data.append(row_data)
            
            if not data or len(data) < 15:
                return None
            
            # Crear DataFrame
            df = pd.DataFrame(data)
            
            # Asignar columnas estándar
            standard_cols = ['Pos', 'Equipo', 'Pts', 'PJ', 'G', 'E', 'P', 'GF', 'GC', 'Dif']
            df.columns = standard_cols[:min(len(df.columns), 10)] + list(df.columns[10:])
            
            # Limpiar columna de posición
            if 'Pos' in df.columns:
                df['Pos'] = df['Pos'].str.extract(r'(\d+)', expand=False)
            
            # Agregar metadata
            df['Temporada'] = season
            df['Fuente'] = lang
            
            # Seleccionar solo columnas relevantes
            cols_to_keep = ['Temporada', 'Pos', 'Equipo', 'PJ', 'G', 'E', 'P', 'Pts', 'GF', 'GC', 'Dif']
            df = df[[col for col in cols_to_keep if col in df.columns]]
            
            logger.info(f"[{lang}] ✓ {season}: {len(df)} equipos extraídos")
            return df
            
        except Exception as e:
            logger.error(f"Error parseando tabla: {e}")
            return None
    
    def scrape_season(self, season: str) -> Optional[pd.DataFrame]:
        """Intenta extraer datos de una temporada usando múltiples fuentes"""
        logger.info(f"Extrayendo temporada {season}...")
        
        # Intentar primero español
        df = self.scrape_season_wikipedia_es(season)
        if df is not None:
            return df
        
        # Si falla, intentar inglés
        logger.info(f"  Reintentando con Wikipedia EN...")
        df = self.scrape_season_wikipedia_en(season)
        if df is not None:
            return df
        
        logger.error(f"✗ No se pudo extraer temporada {season}")
        return None
    
    def scrape_all_seasons(self, start_year: int = 1992, end_year: int = 2025) -> pd.DataFrame:
        """Extrae todas las temporadas de Premier League"""
        all_data = []
        failed_seasons = []
        
        logger.info("="*70)
        logger.info("INICIANDO EXTRACCIÓN DE DATOS DE PREMIER LEAGUE")
        logger.info("="*70)
        
        for year in range(start_year, end_year):
            next_year = year + 1
            season = f"{year}-{str(next_year)[-2:]}"
            
            df = self.scrape_season(season)
            
            if df is not None:
                all_data.append(df)
            else:
                failed_seasons.append(season)
            
            # Pausa para no sobrecargar servidores
            time.sleep(0.8)
        
        # Combinar todos los datos
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Convertir columnas numéricas
            numeric_cols = ['Pos', 'PJ', 'G', 'E', 'P', 'Pts', 'GF', 'GC']
            for col in numeric_cols:
                if col in combined_df.columns:
                    combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
            
            logger.info("\n" + "="*70)
            logger.info("RESUMEN DE EXTRACCIÓN")
            logger.info("="*70)
            logger.info(f"✓ Temporadas exitosas: {len(all_data)}")
            logger.info(f"✗ Temporadas fallidas: {len(failed_seasons)}")
            if failed_seasons:
                logger.info(f"  Temporadas fallidas: {', '.join(failed_seasons)}")
            
            return combined_df
        else:
            logger.error("No se pudieron extraer datos")
            return pd.DataFrame()


def create_team_tracking_database(df: pd.DataFrame) -> pd.DataFrame:
    """Crea una base de datos para tracking de equipos por año"""
    
    logger.info("\nCreando base de datos de tracking de equipos...")
    
    # Obtener todos los equipos únicos
    all_teams = df['Equipo'].unique()
    all_seasons = sorted(df['Temporada'].unique())
    
    # Crear matriz de equipos x temporadas
    tracking_data = []
    
    for team in all_teams:
        team_data = {'Equipo': team}
        
        for season in all_seasons:
            season_data = df[(df['Equipo'] == team) & (df['Temporada'] == season)]
            
            if len(season_data) > 0:
                row = season_data.iloc[0]
                team_data[f'{season}_Pos'] = row['Pos']
                team_data[f'{season}_Pts'] = row['Pts']
            else:
                team_data[f'{season}_Pos'] = None
                team_data[f'{season}_Pts'] = None
        
        tracking_data.append(team_data)
    
    tracking_df = pd.DataFrame(tracking_data)
    
    # Calcular estadísticas
    tracking_df['Total_Temporadas'] = tracking_df.filter(regex='_Pos').notna().sum(axis=1)
    tracking_df['Mejor_Posicion'] = tracking_df.filter(regex='_Pos').min(axis=1)
    tracking_df['Peor_Posicion'] = tracking_df.filter(regex='_Pos').max(axis=1)
    
    # Ordenar por total de temporadas
    tracking_df = tracking_df.sort_values('Total_Temporadas', ascending=False)
    
    logger.info(f"✓ Base de tracking creada: {len(tracking_df)} equipos únicos")
    
    return tracking_df


def main():
    """Función principal"""
    scraper = PremierLeagueScraper()
    
    # Extraer todos los datos
    df_complete = scraper.scrape_all_seasons(1992, 2025)
    
    if len(df_complete) > 0:
        # Guardar datos completos
        output_file = 'premier_league_completo_limpio.csv'
        df_complete.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"\n✓ Datos guardados: {output_file}")
        logger.info(f"  Total registros: {len(df_complete)}")
        logger.info(f"  Temporadas: {df_complete['Temporada'].nunique()}")
        
        # Crear base de datos de tracking
        tracking_df = create_team_tracking_database(df_complete)
        tracking_file = 'premier_league_tracking_equipos.csv'
        tracking_df.to_csv(tracking_file, index=False, encoding='utf-8-sig')
        logger.info(f"\n✓ Base de tracking guardada: {tracking_file}")
        
        # Mostrar estadísticas
        logger.info("\n" + "="*70)
        logger.info("ESTADÍSTICAS FINALES")
        logger.info("="*70)
        logger.info(f"Equipos únicos: {df_complete['Equipo'].nunique()}")
        logger.info(f"Temporadas cubiertas: {df_complete['Temporada'].nunique()}")
        
        print("\nTop 10 equipos por temporadas jugadas:")
        print(tracking_df[['Equipo', 'Total_Temporadas', 'Mejor_Posicion', 'Peor_Posicion']].head(10).to_string(index=False))
        
        logger.info("\n" + "="*70)
        logger.info("✅ PROCESO COMPLETADO")
        logger.info("="*70)
    else:
        logger.error("No se pudieron extraer datos")


if __name__ == "__main__":
    main()
