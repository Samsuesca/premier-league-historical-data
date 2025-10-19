"""
Premier League Scraper v2.0 - FIX para tablas EN
Corrige el problema de columnas shifted en Wikipedia inglés
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PremierLeagueScraper:
    """Scraper mejorado con fix para tablas EN"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.base_url_es = "https://es.wikipedia.org/wiki/Premier_League_{season}"
        self.base_url_en = "https://en.wikipedia.org/wiki/{year}–{next_year}_Premier_League"
    
    def _clean_text(self, text: str) -> str:
        """Limpia texto de caracteres especiales"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\[.*?\]', '', text)
        text = text.replace('↑', '').replace('↓', '').replace('(C)', '').replace('(D)', '')
        return text.strip()
    
    def _is_classification_table(self, table) -> bool:
        """Verifica si es tabla de clasificación"""
        try:
            header_row = table.find('tr')
            if not header_row:
                return False
            
            headers_text = header_row.get_text().upper()
            
            has_points = any(word in headers_text for word in ['PTS', 'PUNTOS', 'POINTS'])
            has_matches = any(word in headers_text for word in ['PJ', 'PARTIDOS', 'PLAYED', 'PLD'])
            has_goals = any(word in headers_text for word in ['GF', 'GOLES', 'GOALS'])
            is_team_info = any(word in headers_text for word in ['ENTRENADOR', 'MANAGER', 'COACH', 'ESTADIO', 'STADIUM', 'CAPITÁN', 'CAPTAIN'])
            
            rows = table.find_all('tr')
            has_enough_rows = len(rows) >= 20
            
            return has_points and has_matches and has_goals and not is_team_info and has_enough_rows
            
        except Exception as e:
            logger.debug(f"Error verificando tabla: {e}")
            return False
    
    def _extract_team_name(self, cell) -> str:
        """Extrae nombre del equipo"""
        link = cell.find('a')
        if link and link.get('title'):
            team_name = link.get('title')
            team_name = team_name.replace(' Football Club', '').replace(' F.C.', '')
            team_name = team_name.replace(' Association Football Club', '')
            return team_name
        return self._clean_text(cell.get_text())
    
    def _detect_column_structure(self, headers: list, rows: list) -> dict:
        """
        Detecta la estructura de columnas y devuelve un mapeo
        para corregir el problema de shift en tablas EN
        """
        headers_upper = [h.upper() for h in headers]
        
        # Detectar posiciones de columnas clave
        mapping = {}
        
        # Buscar índices de columnas importantes
        for i, h in enumerate(headers_upper):
            if 'POS' in h or 'POSITION' in h or h == '#':
                mapping['pos_idx'] = i
            elif 'TEAM' in h or 'CLUB' in h or 'EQUIPO' in h:
                mapping['team_idx'] = i
            elif h in ['PLD', 'PJ', 'PLAYED', 'P'] and 'PTS' not in h:
                mapping['pj_idx'] = i
            elif h in ['W', 'G', 'WON']:
                mapping['w_idx'] = i
            elif h in ['D', 'E', 'DRAWN']:
                mapping['d_idx'] = i
            elif h in ['L', 'P', 'LOST'] and i > mapping.get('d_idx', -1):
                mapping['l_idx'] = i
            elif 'PTS' in h or 'POINTS' in h or 'PUNTOS' in h:
                mapping['pts_idx'] = i
            elif 'GF' in h or ('GOALS' in h and 'FOR' in h):
                mapping['gf_idx'] = i
            elif 'GA' in h or 'GC' in h or ('GOALS' in h and 'AGAINST' in h):
                mapping['gc_idx'] = i
            elif 'GD' in h or 'DIF' in h or ('GOAL' in h and 'DIFF' in h):
                mapping['gd_idx'] = i
        
        logger.info(f"Mapeo de columnas detectado: {mapping}")
        return mapping
    
    def _parse_classification_table_fixed(self, table, season: str, lang: str) -> Optional[pd.DataFrame]:
        """Parsea tabla de clasificación con corrección de columnas"""
        try:
            rows = table.find_all('tr')
            header_row = rows[0]
            headers = [self._clean_text(th.get_text()) for th in header_row.find_all(['th', 'td'])]
            
            # Detectar estructura de columnas
            col_mapping = self._detect_column_structure(headers, rows[1:])
            
            data = []
            for row in rows[1:]:
                cols = row.find_all(['td', 'th'])
                if len(cols) < 8:  # Necesitamos al menos 8 columnas
                    continue
                
                try:
                    # Extraer datos usando el mapeo detectado
                    row_data = {}
                    
                    # Posición
                    pos_idx = col_mapping.get('pos_idx', 0)
                    pos_text = self._clean_text(cols[pos_idx].get_text())
                    row_data['Pos'] = re.search(r'(\d+)', pos_text).group(1) if re.search(r'(\d+)', pos_text) else ''
                    
                    # Equipo
                    team_idx = col_mapping.get('team_idx', 1)
                    row_data['Equipo'] = self._extract_team_name(cols[team_idx])
                    
                    # PJ (Partidos Jugados)
                    pj_idx = col_mapping.get('pj_idx', 2)
                    row_data['PJ'] = self._clean_text(cols[pj_idx].get_text())
                    
                    # G (Ganados)
                    w_idx = col_mapping.get('w_idx', 3)
                    row_data['G'] = self._clean_text(cols[w_idx].get_text())
                    
                    # E (Empatados)
                    d_idx = col_mapping.get('d_idx', 4)
                    row_data['E'] = self._clean_text(cols[d_idx].get_text())
                    
                    # P (Perdidos)
                    l_idx = col_mapping.get('l_idx', 5)
                    row_data['P'] = self._clean_text(cols[l_idx].get_text())
                    
                    # GF (Goles a Favor)
                    gf_idx = col_mapping.get('gf_idx', 6)
                    row_data['GF'] = self._clean_text(cols[gf_idx].get_text())
                    
                    # GC (Goles en Contra)
                    gc_idx = col_mapping.get('gc_idx', 7)
                    row_data['GC'] = self._clean_text(cols[gc_idx].get_text())
                    
                    # Diferencia de goles
                    if 'gd_idx' in col_mapping:
                        gd_idx = col_mapping['gd_idx']
                        row_data['Dif'] = self._clean_text(cols[gd_idx].get_text())
                    else:
                        row_data['Dif'] = ''
                    
                    # Puntos
                    pts_idx = col_mapping.get('pts_idx', len(cols) - 1)
                    row_data['Pts'] = self._clean_text(cols[pts_idx].get_text())
                    
                    data.append(row_data)
                    
                except Exception as e:
                    logger.debug(f"Error procesando fila: {e}")
                    continue
            
            if not data or len(data) < 15:
                return None
            
            df = pd.DataFrame(data)
            
            # Convertir a numérico
            numeric_cols = ['Pos', 'PJ', 'G', 'E', 'P', 'Pts', 'GF', 'GC']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Validar datos
            if not self._validate_data(df):
                logger.warning(f"[{lang}] Datos no válidos para {season}")
                return None
            
            df['Temporada'] = season
            df['Fuente'] = lang
            
            # Seleccionar columnas finales
            cols_to_keep = ['Temporada', 'Pos', 'Equipo', 'PJ', 'G', 'E', 'P', 'Pts', 'GF', 'GC', 'Dif']
            df = df[[col for col in cols_to_keep if col in df.columns]]
            
            logger.info(f"[{lang}] ✓ {season}: {len(df)} equipos extraídos")
            return df
            
        except Exception as e:
            logger.error(f"Error parseando tabla: {e}")
            return None
    
    def _validate_data(self, df: pd.DataFrame) -> bool:
        """Valida que los datos sean correctos"""
        if df is None or len(df) < 15:
            return False
        
        # Validar que PJ sea consistente (38 o 42)
        if 'PJ' in df.columns:
            unique_pj = df['PJ'].unique()
            if len(unique_pj) > 2 or not any(pj in [38, 42] for pj in unique_pj):
                logger.warning(f"PJ inconsistente: {unique_pj}")
                return False
        
        # Validar G + E + P = PJ
        if all(col in df.columns for col in ['G', 'E', 'P', 'PJ']):
            suma = df['G'] + df['E'] + df['P']
            if not (suma == df['PJ']).all():
                logger.warning("G + E + P != PJ")
                return False
        
        # Validar Pts = 3*G + E
        if all(col in df.columns for col in ['Pts', 'G', 'E']):
            pts_esperado = 3 * df['G'] + df['E']
            if not (pts_esperado == df['Pts']).all():
                logger.warning("Pts != 3*G + E")
                return False
        
        return True
    
    def _scrape_wikipedia_page(self, url: str, season: str, lang: str) -> Optional[pd.DataFrame]:
        """Extrae datos de una página de Wikipedia"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            tables = soup.find_all('table', {'class': 'wikitable'})
            
            for table in tables:
                if self._is_classification_table(table):
                    return self._parse_classification_table_fixed(table, season, lang)
            
            logger.warning(f"[{lang}] No se encontró tabla de clasificación válida en {url}")
            return None
            
        except Exception as e:
            logger.error(f"[{lang}] Error extrayendo {url}: {e}")
            return None
    
    def scrape_season_wikipedia_es(self, season: str) -> Optional[pd.DataFrame]:
        """Intenta extraer de Wikipedia ES"""
        url = self.base_url_es.format(season=season)
        return self._scrape_wikipedia_page(url, season, 'ES')
    
    def scrape_season_wikipedia_en(self, season: str) -> Optional[pd.DataFrame]:
        """Intenta extraer de Wikipedia EN"""
        year = int(season.split('-')[0])
        next_year = str(year + 1)[-2:]
        url = self.base_url_en.format(year=year, next_year=next_year)
        return self._scrape_wikipedia_page(url, season, 'EN')
    
    def scrape_season(self, season: str) -> Optional[pd.DataFrame]:
        """Extrae una temporada usando múltiples fuentes"""
        logger.info(f"Extrayendo temporada {season}...")
        
        # Intentar ES primero
        df = self.scrape_season_wikipedia_es(season)
        if df is not None:
            return df
        
        # Si falla, intentar EN
        logger.info(f"  Reintentando con Wikipedia EN...")
        df = self.scrape_season_wikipedia_en(season)
        if df is not None:
            return df
        
        logger.error(f"✗ No se pudo extraer temporada {season}")
        return None
    
    def scrape_all_seasons(self, start_year: int = 1992, end_year: int = 2025) -> pd.DataFrame:
        """Extrae todas las temporadas"""
        all_data = []
        failed_seasons = []
        
        logger.info("="*70)
        logger.info("INICIANDO EXTRACCIÓN CON FIX PARA TABLAS EN")
        logger.info("="*70)
        
        for year in range(start_year, end_year):
            next_year = year + 1
            season = f"{year}-{str(next_year)[-2:]}"
            
            df = self.scrape_season(season)
            
            if df is not None:
                all_data.append(df)
            else:
                failed_seasons.append(season)
            
            time.sleep(0.8)
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            
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
    """Crea base de datos de tracking de equipos"""
    logger.info("\nCreando base de datos de tracking de equipos...")
    
    all_teams = df['Equipo'].unique()
    all_seasons = sorted(df['Temporada'].unique())
    
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
    tracking_df['Total_Temporadas'] = tracking_df.filter(regex='_Pos').notna().sum(axis=1)
    tracking_df['Mejor_Posicion'] = tracking_df.filter(regex='_Pos').min(axis=1)
    tracking_df['Peor_Posicion'] = tracking_df.filter(regex='_Pos').max(axis=1)
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
        output_file = 'premier_league_completo_FIXED.csv'
        df_complete.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"\n✓ Datos guardados: {output_file}")
        logger.info(f"  Total registros: {len(df_complete)}")
        logger.info(f"  Temporadas: {df_complete['Temporada'].nunique()}")
        
        # Validar datos
        logger.info("\n" + "="*70)
        logger.info("VALIDACIÓN DE DATOS")
        logger.info("="*70)
        
        # Verificar consistencia
        df_complete['Suma_GEP'] = df_complete['G'] + df_complete['E'] + df_complete['P']
        df_complete['Pts_Esperado'] = 3 * df_complete['G'] + df_complete['E']
        
        problemas_pj = (df_complete['Suma_GEP'] != df_complete['PJ']).sum()
        problemas_pts = (df_complete['Pts_Esperado'] != df_complete['Pts']).sum()
        
        logger.info(f"Registros con G+E+P != PJ: {problemas_pj}")
        logger.info(f"Registros con Pts != 3*G+E: {problemas_pts}")
        
        if problemas_pj == 0 and problemas_pts == 0:
            logger.info("✅ TODOS LOS DATOS SON CONSISTENTES!")
        else:
            logger.warning("⚠️  Aún hay inconsistencias")
        
        # Crear tracking
        tracking_df = create_team_tracking_database(df_complete)
        tracking_file = 'premier_league_tracking_equipos_FIXED.csv'
        tracking_df.to_csv(tracking_file, index=False, encoding='utf-8-sig')
        logger.info(f"\n✓ Base de tracking guardada: {tracking_file}")
        
        # Estadísticas
        logger.info("\n" + "="*70)
        logger.info("ESTADÍSTICAS FINALES")
        logger.info("="*70)
        logger.info(f"Equipos únicos: {df_complete['Equipo'].nunique()}")
        logger.info(f"Temporadas cubiertas: {df_complete['Temporada'].nunique()}")
        logger.info(f"Registros por fuente:")
        for fuente, count in df_complete['Fuente'].value_counts().items():
            logger.info(f"  {fuente}: {count}")
        
        print("\nTop 10 equipos por temporadas jugadas:")
        print(tracking_df[['Equipo', 'Total_Temporadas', 'Mejor_Posicion', 'Peor_Posicion']].head(10).to_string(index=False))
        
        logger.info("\n" + "="*70)
        logger.info("✅ PROCESO COMPLETADO")
        logger.info("="*70)
    else:
        logger.error("No se pudieron extraer datos")


if __name__ == "__main__":
    main()
