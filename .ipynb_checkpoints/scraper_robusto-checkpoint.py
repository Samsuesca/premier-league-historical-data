import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
        text = text.replace('−', '-').replace('+', '')  # Normalizar Dif para numérico
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
    
    def scrape_season_wikipedia_es(self, season: str) -> pd.DataFrame:
        """Intenta extraer datos de Wikipedia en español"""
        url = self.base_url_es.format(season=season)
        return self._scrape_wikipedia_page(url, season, 'ES')
    
    def scrape_season_wikipedia_en(self, season: str) -> pd.DataFrame:
        """Intenta extraer datos de Wikipedia en inglés"""
        year = int(season.split('-')[0])
        next_year = str(year + 1)[-2:]
        url = self.base_url_en.format(year=year, next_year=next_year)
        return self._scrape_wikipedia_page(url, season, 'EN')
    
    def _scrape_wikipedia_page(self, url: str, season: str, lang: str) -> pd.DataFrame:
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
    
    def _parse_classification_table(self, table, season: str, lang: str) -> pd.DataFrame:
        """Parsea una tabla de clasificación con mapeo dinámico"""
        try:
            rows = table.find_all('tr')
            
            # Extraer encabezados reales (normalizados a minúsculas)
            header_row = rows[0]
            headers = [self._clean_text(th.get_text()).lower() for th in header_row.find_all(['th', 'td'])]
            logger.info(f"[{lang}] Headers extraídos para {season}: {headers}")
            
            # Mapear columnas dinámicamente
            col_map = {}
            for i, h in enumerate(headers):
                if 'pos' in h:
                    col_map['Pos'] = i
                elif 'equipo' in h or 'team' in h:
                    col_map['Equipo'] = i
                elif 'pj' in h or 'pld' in h or 'played' in h:
                    col_map['PJ'] = i
                elif 'g' in h or 'w' in h or 'ganados' in h or 'wins' in h:
                    col_map['G'] = i
                elif 'e' in h or 'd' in h or 'empates' in h or 'draws' in h:
                    col_map['E'] = i
                elif 'p' in h or 'l' in h or 'perdidos' in h or 'losses' in h:
                    col_map['P'] = i
                elif 'gf' in h or 'goals for' in h:
                    col_map['GF'] = i
                elif 'gc' in h or 'ga' in h or 'goals against' in h:
                    col_map['GC'] = i
                elif 'dif' in h or 'gd' in h or 'goal difference' in h:
                    col_map['Dif'] = i
                elif 'pts' in h or 'puntos' in h or 'points' in h:
                    col_map['Pts'] = i
            
            # Verificar que todas las columnas necesarias estén mapeadas
            required_cols = ['Pos', 'Equipo', 'PJ', 'G', 'E', 'P', 'GF', 'GC', 'Dif', 'Pts']
            if any(col not in col_map for col in required_cols):
                logger.error(f"[{lang}] Faltan columnas en mapeo para {season}: {col_map}")
                return None
            
            # Extraer datos
            data = []
            for row in rows[1:]:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= max(col_map.values()) + 1:  # Asegurar suficientes columnas
                    row_data = {}
                    for col_name, idx in col_map.items():
                        text = self._clean_text(cols[idx].get_text())
                        if col_name == 'Equipo':
                            text = self._extract_team_name(cols[idx])
                        row_data[col_name] = text
                    if row_data:
                        data.append(row_data)
            
            if not data or len(data) < 15:
                logger.warning(f"[{lang}] Datos insuficientes para {season}")
                return None
            
            # Crear DataFrame
            df = pd.DataFrame(data)
            
            # Agregar metadata
            df['Temporada'] = season
            df['Fuente'] = lang
            
            # Convertir columnas numéricas
            numeric_cols = ['Pos', 'PJ', 'G', 'E', 'P', 'GF', 'GC', 'Dif', 'Pts']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Validaciones básicas para detectar errores residuales
            df['Suma_GEP'] = df['G'] + df['E'] + df['P']
            if not (df['Suma_GEP'] == df['PJ']).all():
                logger.warning(f"[{lang}] Inconsistencia en PJ (G+E+P != PJ) para {season}")
            df['Pts_calc'] = 3 * df['G'] + df['E']
            if not (df['Pts_calc'] == df['Pts']).all():
                logger.warning(f"[{lang}] Inconsistencia en Pts (3*G + E != Pts) para {season}")
            df['Dif_calc'] = df['GF'] - df['GC']
            if not (df['Dif_calc'] == df['Dif']).all():
                logger.warning(f"[{lang}] Inconsistencia en Dif (GF - GC != Dif) para {season}")
            
            # Limpiar columnas temporales
            df = df.drop(['Suma_GEP', 'Pts_calc', 'Dif_calc'], axis=1)
            
            logger.info(f"[{lang}] ✓ {season}: {len(df)} equipos extraídos")
            return df
            
        except Exception as e:
            logger.error(f"[{lang}] Error parseando tabla para {season}: {e}")
            return None
    
    def scrape_season(self, season: str) -> pd.DataFrame:
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

def main():
    """Función principal"""
    scraper = PremierLeagueScraper()
    
    # Extraer todos los datos
    df_complete = scraper.scrape_all_seasons(1992, 2025)
    
    if len(df_complete) > 0:
        # Guardar datos completos
        output_file = 'premier_league_completo_limpio_v2.csv'
        df_complete.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"\n✓ Datos guardados: {output_file}")
        logger.info(f"  Total registros: {len(df_complete)}")
        logger.info(f"  Temporadas: {df_complete['Temporada'].nunique()}")
        
        logger.info("\n" + "="*70)
        logger.info("ESTADÍSTICAS FINALES")
        logger.info("="*70)
        logger.info(f"Equipos únicos: {df_complete['Equipo'].nunique()}")
        logger.info(f"Temporadas cubiertas: {df_complete['Temporada'].nunique()}")
        
        logger.info("\n" + "="*70)
        logger.info("✅ PROCESO COMPLETADO")
        logger.info("="*70)
    else:
        logger.error("No se pudieron extraer datos")

if __name__ == "__main__":
    main()