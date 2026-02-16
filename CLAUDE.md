<!-- AUTO-GENERATED GIT WORKFLOW HEADER -->
<!-- Version: 1.0.0 | Template: GIT_WORKFLOW_RESEARCH.md | Last Updated: 2026-02-16 -->
<!-- DO NOT EDIT MANUALLY - Run: ~/.claude/scripts/sync-git-workflow.sh -->

---

# Git Workflow & Commit Standards

**Version:** 1.0.0
**Last Updated:** 2026-02-15
**Template Type:** Research & Academic Projects

---

## Branch Strategy

### Main Branches

- **`main`** - Stable, reproducible version (for paper submissions, presentations)
  - Only merge via Pull Requests
  - All scripts must run without errors
  - Tagged with milestones: `v1.0-submission`, `v2.0-revision`

- **`develop`** - Working branch for analysis
  - Merge exploratory branches here
  - Base for new analysis approaches
  - Can contain work-in-progress

### Supporting Branches

- **`analysis/*`** - New analytical approaches
  - Branch from: `develop`
  - Merge into: `develop`
  - Naming: `analysis/did-parallel-trends`, `analysis/robustness-checks`

- **`data/*`** - Data processing or new datasets
  - Branch from: `develop`
  - Merge into: `develop`
  - Naming: `data/clean-edif-2022`, `data/merge-municode`

- **`docs/*`** - Paper writing, documentation
  - Branch from: `develop`
  - Merge into: `develop`
  - Naming: `docs/methodology-section`, `docs/update-tables`

---

## Commit Convention

### Format

```
<emoji> <type>: <description>

[optional body]

[optional footer]
```

### Commit Types with Emojis

```bash
✨ feat:       New analysis, model, or methodology
🐛 fix:        Bug fix in code or data processing
♻️ refactor:   Code reorganization (no results change)
📚 docs:       Documentation, comments, methodology notes
✅ test:       Validation tests, balance checks
🔒 security:   Data protection, anonymization
⚡ perf:       Performance optimization (faster processing)
🚀 chore:      Dependencies, environment setup
📊 data:       Data cleaning, merging, transformation
📈 analysis:   New regression, estimation, visualization
```

### Examples

**Good commits:**
```bash
✨ feat: implement staggered DiD estimator
🐛 fix: correct municipality code merge in S2 script
📊 data: clean and standardize EDIF 2022 variables
📈 analysis: add parallel trends event study plot
📚 docs: document variable construction in README
✅ test: add balance table for treatment/control groups
♻️ refactor: modularize data cleaning pipeline
```

---

## Data Protection Rules (CRITICAL)

### Golden Rule: NEVER Modify Raw Data

```bash
# Directory structure
data/
├── raw/              # SACRED - Never modify, never commit changes
│   ├── original_dataset.dta
│   └── external_controls.csv
├── processed/        # Git-trackable cleaned data
│   ├── cleaned_data.dta
│   └── analysis_ready.dta
└── external/         # Reference data (geocodes, etc.)
```

### Raw Data Protection

- **NEVER** edit files in `data/raw/`
- **ALWAYS** create processed versions in `data/processed/`
- **DOCUMENT** all transformations in code
- **VERSION** raw data externally (Dropbox, institutional server)

### Sensitive Data

- **NEVER** commit personally identifiable information (PII)
- **ANONYMIZE** data before committing
- **ENCRYPT** if necessary (use .gitignore for sensitive files)
- **DOCUMENT** data sources and access restrictions

---

## Reproducibility Checklist

### Before Every Commit

- [ ] **Master script runs end-to-end** - `S00_Master.do` executes without errors
- [ ] **Results unchanged** - Compare tables/figures with previous version
- [ ] **Logs generated** - All scripts create log files
- [ ] **Paths are relative** - No hardcoded absolute paths
- [ ] **Dependencies documented** - Stata packages, R libraries listed
- [ ] **Random seeds set** - For simulations or bootstrapping

### Master Script Convention

Every project should have:

```stata
// S00_Master.do - Executes entire analysis pipeline

clear all
set more off

// Set working directory (user adjusts this line only)
global root "/Users/user/project"
cd "$root"

// Run all scripts in order
do "code/Stata/S0_data_cleaning.do"
do "code/Stata/S1_construct_panel.do"
do "code/Stata/S2_merge_controls.do"
do "code/Stata/S3_descriptive_stats.do"
do "code/Stata/S4_balance_tables.do"
do "code/Stata/S5_parallel_trends.do"
do "code/Stata/S6_main_regressions.do"
do "code/Stata/S7_robustness_checks.do"
do "code/Stata/S8_export_results.do"
```

---

## Standard Workflows

### 1. New Analysis Approach

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create analysis branch
git checkout -b analysis/event-study-rdd

# 3. Implement analysis
# Edit: code/Stata/S6_event_study.do

# 4. Run and verify
stata-mp -b do code/Stata/S6_event_study.do

# 5. Check output
# Review: logs/S6_event_study.log
# Review: output/figures/event_study.png

# 6. Commit code + output
git add code/Stata/S6_event_study.do
git add output/figures/event_study.png
git add output/tables/event_study_table.tex
git commit -m "📈 analysis: implement RDD-based event study"

# 7. Push and create PR
git push -u origin analysis/event-study-rdd
```

### 2. Data Cleaning/Processing

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create data branch
git checkout -b data/clean-edif-2022

# 3. Write cleaning script
# Edit: code/Stata/S0_clean_edif.do

# 4. Process data
stata-mp -b do code/Stata/S0_clean_edif.do

# 5. Verify output
# Check: data/processed/edif_2022_clean.dta
# Check: logs/S0_clean_edif.log

# 6. Commit script (NOT raw data)
git add code/Stata/S0_clean_edif.do
git add docs/data_dictionary.md  # Document variables
git commit -m "📊 data: clean EDIF 2022 survey variables"

# 7. Push and create PR
git push -u origin data/clean-edif-2022
```

### 3. Documentation/Paper Updates

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create docs branch
git checkout -b docs/update-methodology

# 3. Update documentation
# Edit: docs/methodology.md
# Edit: paper/main.tex

# 4. Commit
git add docs/methodology.md paper/main.tex
git commit -m "📚 docs: clarify DiD identification strategy"

# 5. Push
git push -u origin docs/update-methodology
```

---

## Results Documentation

### Every Analysis Script Should:

1. **Generate a log file**
```stata
log using "logs/S6_main_regressions.log", replace
// ... analysis code ...
log close
```

2. **Export tables**
```stata
esttab using "output/tables/main_results.tex", ///
    replace label booktabs ///
    title("Main Regression Results")
```

3. **Save figures**
```stata
graph export "output/figures/event_study.png", replace
```

4. **Document decisions**
```stata
/*
   Note: Dropped observations with missing municipality codes (N=127)
   Reason: Cannot merge with external controls
   Date: 2026-02-15
*/
```

---

## Commit Best Practices

### DO ✅

- **Commit scripts, not data** - Code is version-controlled, data is archived
- **Run master script** - Ensure reproducibility before committing
- **Document methodological choices** - In comments and docs/
- **Export results** - Tables and figures go to output/
- **Use relative paths** - Project should work on any machine
- **Set random seeds** - `set seed 12345` for reproducibility

### DON'T ❌

- **Modify raw data** - NEVER edit data/raw/ files
- **Commit large datasets** - Use .gitignore for .dta files >100MB
- **Hardcode paths** - Use global macros or relative paths
- **Skip logs** - Always generate log files
- **Commit without testing** - Run S00_Master.do first
- **Use display with sensitive data** - Can expose PII in logs

---

## Pre-Commit Checklist (Research)

Before every commit:

- [ ] **Master script runs** - `S00_Master.do` executes without errors
- [ ] **Results reproduced** - Tables/figures match previous version (or document changes)
- [ ] **Logs reviewed** - No unexpected errors or warnings
- [ ] **Data dictionary updated** - If new variables created
- [ ] **No PII exposed** - Checked logs and output for sensitive info
- [ ] **Paths are relative** - No hardcoded `/Users/sam/...` paths
- [ ] **Code commented** - Methodological decisions documented
- [ ] **Results exported** - Updated tables/figures in output/

---

## Pull Request Process

### PR Description Template (Research)

```markdown
## Summary
Brief description of analysis/data changes

## Methodological Changes
- Added X estimator
- Changed Y sample restriction
- Updated Z controls

## Results Impact
- [ ] Results unchanged (code refactor only)
- [ ] Minor changes (<5% coefficient change)
- [ ] Major changes (different conclusions)

## Reproducibility
- [ ] Master script runs without errors
- [ ] Logs generated for all scripts
- [ ] Tables/figures exported correctly

## Data Changes
- [ ] New dataset added (describe source)
- [ ] Variables added/modified (update data dictionary)
- [ ] No changes to raw data

## Related Issues
Closes #123
```

---

## .gitignore Essentials (Research)

```bash
# Raw data (NEVER commit)
data/raw/*.dta
data/raw/*.csv
data/raw/*.xlsx

# Large processed data (archive externally)
*.dta
*.csv
*.xlsx
!data/external/municodes.csv  # Small reference files OK

# Stata temporary files
*.gph
*.smcl

# R temporary files
.Rhistory
.RData
.Rproj.user/

# LaTeX compilation
*.aux
*.log
*.out
*.synctex.gz
*.bbl
*.blg

# Output (commit final versions, not intermediates)
output/temp/

# Sensitive files
data/raw/
credentials.json
*.key
```

---

## Milestone Tagging

### Tagging Important Versions

```bash
# Before paper submission
git tag -a v1.0-submission -m "Version submitted to journal (2026-02-15)"
git push origin v1.0-submission

# After revisions
git tag -a v2.0-revision -m "Revised version addressing reviewer comments"
git push origin v2.0-revision

# Final accepted version
git tag -a v3.0-final -m "Final accepted version for publication"
git push origin v3.0-final
```

---

## Collaboration & Co-Authorship

### Multi-Author Commits

```bash
# Include co-author in commit message
git commit -m "📈 analysis: add heterogeneity analysis by region

Co-authored-by: Diana Valencia <diana@eafit.edu.co>
Co-authored-by: Eliana Rojas <eliana@eafit.edu.co>"
```

---

## Emergency Commands

### Restore Previous Results

```bash
# Find last working version
git log --oneline output/tables/main_results.tex

# Restore specific file
git checkout <commit-hash> output/tables/main_results.tex
```

### Compare Results Across Versions

```bash
# See changes in table
git diff v1.0-submission:output/tables/main.tex output/tables/main.tex
```

---

## Resources

- **Stata Reproducibility:** https://www.stata.com/manuals/u.pdf
- **R Project Organization:** https://martinctc.github.io/blog/rstudio-projects-and-working-directories/
- **Gentzkow & Shapiro Code Guide:** https://web.stanford.edu/~gentzkow/research/CodeAndData.pdf
- **OSF Preregistration:** https://osf.io

---

**Note:** This workflow header is auto-generated from `~/.claude/templates/GIT_WORKFLOW_RESEARCH.md`.
To update across all projects, run: `~/.claude/scripts/sync-git-workflow.sh`

---

<!-- END AUTO-GENERATED GIT WORKFLOW HEADER -->
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **English Football Pyramid Historical Data Analysis System** that scrapes, validates, and analyzes data from all 5 major divisions of English football (1993-2025).

**Current Version**: v3.1 - Fase 3: English Football Pyramid Expansion (Full Historical Data)

### Project Evolution
- **v1.0 (Archived)**: Wikipedia-based scraping - 36% success rate, archived due to inconsistencies
- **v2.0 (Octubre 2024)**: Premier League only via football-data.co.uk - 100% success rate, 644 records
- **v3.0 (Enero 2025)**: Extended to 5 divisions - 2,516 total records, 159 unique teams tracked
- **v3.1 (Enero 2025)**: ⭐ Full historical data 1993-2025 - 3,260 total records, 160 unique teams, 32 seasons for levels 1-4

### Coverage (Updated v3.1)
- **Premier League** (Nivel 1): 1993-2025, 32 seasons, 644 records
- **Championship** (Nivel 2): 1993-2025, 32 seasons, 768 records **(+264 vs v3.0)** - *Historical name: First Division (1993-2004)*
- **League One** (Nivel 3): 1993-2025, 31 seasons, 744 records **(+264 vs v3.0)** - *Historical name: Second Division (1993-2004)*
- **League Two** (Nivel 4): 1993-2025, 30 seasons, 720 records **(+216 vs v3.0)** - *Historical name: Third Division (1993-2004)*
- **National League** (Nivel 5): 2005-2025, 16 seasons, 384 records (unchanged - data availability limited)

**Total improvement**: +744 records (+29.5% more data)

## Common Commands

### Data Extraction - Premier League Only (Fase 2)
```bash
# Download/update Premier League data (1993-2025)
python scraper_premier_league.py

# Verify Premier League data integrity
python verificar_datos.py
```

### Data Extraction - All Divisions (Fase 3) ⭐ RECOMMENDED
```bash
# Download/update all 5 divisions (Premier to National League)
python scraper_english_leagues.py

# Verify multi-division data integrity
python verificar_english_leagues.py
```

### Analysis
```bash
# Launch Jupyter notebook for Premier League analysis
jupyter notebook analisis_premier_league.ipynb
```

### Dependencies
```bash
# Install required packages
pip install pandas requests numpy matplotlib seaborn jupyter
```

## Architecture & Data Flow

### 1. Data Source Architecture
- **Source**: football-data.co.uk CSV files (URL pattern: `https://www.football-data.co.uk/mmz4281/{YYZZ}/E0.csv`)
- **Rate Limiting**: 0.5s delay between requests in `scraper_premier_league.py:261`
- **Fallback Parsing**: Multiple CSV parsing strategies with different encodings (UTF-8, Latin-1) at `scraper_premier_league.py:64-89`

### 2. Data Processing Pipeline
The scraper follows this workflow:

1. **URL Construction** (`get_football_data_url()` at line 17): Converts season format (e.g., "2015-16") to football-data.co.uk URL codes (e.g., "1516")

2. **Match Data Download** (`download_season()` at line 52): Downloads raw CSV with columns: HomeTeam, AwayTeam, FTHG, FTAG, FTR (H/D/A)

3. **Table Calculation** (lines 124-168): Reconstructs league standings from individual match results:
   - Aggregates home/away results per team
   - Calculates: Wins (FTR='H' for home, 'A' for away), Draws (FTR='D'), Losses
   - Computes: Goals For/Against, Goal Difference, Points (3-1-0 system)

4. **Validation** (lines 290-302): Three-tier consistency check:
   - `G + E + P = PJ` (matches sum validation)
   - `Pts = 3*G + E` (points system validation)
   - Team count: 20-22 per season (Premier League size validation)

5. **Output Generation**:
   - `premier_league_COMPLETO_football_data.csv` - Main dataset with 11 columns
   - `premier_league_tracking_COMPLETO.csv` - Tracking matrix (teams × seasons) generated by `create_tracking()` at line 329

### 3. Data Schema

**Main Dataset** (`premier_league_COMPLETO_football_data.csv`):
```
Temporada | Pos | Equipo | PJ | G | E | P | Pts | GF | GC | Dif
----------|-----|--------|----|----|---|---|-----|----|----|----
1993-94   | 1   | Man United | 42 | 27 | 11 | 4 | 92 | 80 | 38 | +42
```

**Tracking Database** (`premier_league_tracking_COMPLETO.csv`):
- Pivot table structure: Each row = one team
- Columns: `{season}_Pos`, `{season}_Pts` for each of 32 seasons
- Computed metrics: `Total_Temporadas`, `Mejor_Posicion`, `Peor_Posicion`

### 4. Analysis Functions (Jupyter Notebook)

Three reusable query functions defined in `analisis_premier_league.ipynb`:

- **`ver_historial_equipo(nombre)`** (cell 22): Full team history with fuzzy name matching
- **`ver_temporada(temporada)`** (cell 23): Complete season standings table
- **`comparar_equipos(*equipos)`** (cell 24): Comparative analysis across multiple teams

### 5. Error Handling Strategy

**Robust Parsing** (`scraper_premier_league.py:52-200`):
- Multiple parsing attempts with different pandas configurations
- Safe integer conversion with `safe_int_conversion()` at line 37 (handles malformed numeric strings)
- Team name cleaning with `clean_team_name()` at line 30
- Graceful failure logging without stopping entire scrape

**Data Quality Gates**:
- Null value checks before processing (line 96, 111)
- Result validation (must be H/D/A) at line 118
- Empty dataset detection at line 120

## Key Implementation Details

### Season Code Mapping
Years map to football-data.co.uk codes via last 2 digits:
- 1993-94 → "9394"
- 2015-16 → "1516"
- 2024-25 → "2425"

Implementation: `scraper_premier_league.py:17-27`

### Why Wikipedia Was Abandoned (v1.0)
The archived scraper (`archive/scraper_robusto.py`) failed due to:
- Inconsistent HTML table structures across Wikipedia language versions
- Success rate: only 12/33 seasons (36%)
- Unreliable for production use

Migration rationale documented in `archive/README_ARCHIVE.md`

### Validation Results
- **644 records** verified
- **0 errors** in consistency checks
- **100% data quality** across all seasons
- Verification script: `verificar_datos.py`

## Data Characteristics

### Coverage Gaps
- **Missing**: 1992-93 season (not available on football-data.co.uk)
- **Partial**: 2024-25 season (ongoing, updated weekly)

### Historical Constants
- **6 teams** in all 32 seasons: Arsenal, Chelsea, Tottenham, Man United, Everton, Liverpool
- **Variable team count**: 22 teams in 1993-95, then standardized to 20 teams from 1995-96 onward

### Record Holders
- **Most points**: Man City 100 (2017-18) - found in cell 26 of notebook
- **Most goals**: Man City 106 (2017-18) - found in cell 28 of notebook
- **Most titles**: Man United (12), Man City (8)

## Working with This Codebase

### To Update Data for New Season
1. Run `python scraper_premier_league.py` - automatically fetches latest available data
2. Run `python verificar_datos.py` - confirms new data passes validation
3. Check logs for any failed seasons that may need manual investigation

### To Add New Analysis
1. Open `analisis_premier_league.ipynb`
2. Load data: `df = pd.read_csv('premier_league_COMPLETO_football_data.csv')`
3. Use existing functions (`ver_historial_equipo`, `ver_temporada`, `comparar_equipos`) as templates
4. Follow pandas operations pattern from cells 15-28

### To Debug Failed Season Downloads
Use `debug_season(season)` function at `scraper_premier_league.py:203`:
```python
debug_season('2015-16')  # Shows URL, HTTP status, CSV structure, column types
```

### To Extend to Other Leagues
football-data.co.uk supports multiple leagues with different codes:
- E0 = Premier League (England)
- SP1 = La Liga (Spain)
- I1 = Serie A (Italy)
- D1 = Bundesliga (Germany)
- F1 = Ligue 1 (France)

Modify URL pattern in `get_football_data_url()` to change league code.

## Fase 3: English Football Pyramid Expansion Architecture

### Modular Design Pattern

The Fase 3 expansion (`scraper_english_leagues.py`) implements an object-oriented architecture with:

**Base Class**: `EnglishLeagueScraper` (abstract base class at line 19)
- Contains all shared scraping logic
- Abstract methods for division-specific configuration
- Handles URL construction, data parsing, validation, and CSV generation

**Division Subclasses**:
- `PremierLeagueScraper` (line 268): E0 code, 20-22 teams, 1993-2025
- `ChampionshipScraper` (line 280): E1 code, 24 teams, 2004-2025
- `LeagueOneScraper` (line 290): E2 code, 24 teams, 2004-2025
- `LeagueTwoScraper` (line 300): E3 code, 24 teams, 2004-2025
- `NationalLeagueScraper` (line 310): EC code, 24 teams, 2005-2025

### Key Design Decisions

**1. Inheritance over Duplication**
- All scraping logic inherited from base class
- Only division-specific parameters defined in subclasses
- DRY principle: ~400 lines vs. ~2000 lines if duplicated

**2. Flexible Team Count Validation**
- Premier League accepts (20, 22) tuple for 1993-95 seasons
- Other divisions expect exactly 24 teams
- Validation at `validate_team_count()` (line 235)

**3. Unified CSV Schema**
- All divisions output same column structure
- Added `Division` column to differentiate leagues
- Format: `Temporada | Division | Pos | Equipo | PJ | G | E | P | Pts | GF | GC | Dif`

**4. Longitudinal Tracking**
- `create_tracking()` function (line 426) generates tracking matrix
- Tracks division changes across seasons for each team
- Computed metrics: Total_Temporadas, Divisiones_Jugadas, Mejor_Division
- Enables promotion/relegation analysis

### Multi-Division Workflow

Main execution flow in `scrape_all_divisions()` (line 320):

1. **Initialize scrapers** (line 328-334): One instance per division with specific year ranges
2. **Sequential scraping** (line 339): Process each division with delay between requests
3. **Validation per division** (line 351-356): Verify G+E+P=PJ and Pts=3*G+E for each
4. **Combine datasets** (line 376): Concatenate all divisions into single DataFrame
5. **Generate tracking** (line 392): Create longitudinal database with division transitions

### Data Validation Strategy

**Three-tier validation** implemented in `verificar_english_leagues.py`:

1. **Mathematical consistency** (lines 35-47):
   - G + E + P = PJ (matches played)
   - Pts = 3×G + E (points system)

2. **Division-specific team counts** (lines 51-76):
   - Premier: 20-22 teams (variable in early years)
   - Championship/League One/League Two/National: 24 teams
   - Flags anomalies like COVID-19 affected seasons

3. **Cross-division integrity** (lines 115-142):
   - Tracks teams moving between divisions
   - Identifies mobility patterns (ascensos/descensos)
   - Validates no duplicate team-season pairs

### Extending to Additional Divisions

To add National League North/South (Level 6):

1. Create new scraper class:
```python
class NationalLeagueNorthScraper(EnglishLeagueScraper):
    def __init__(self, start_year=2015, end_year=2025):
        super().__init__(
            division_name="National League North",
            division_code="EN",  # Verify code on football-data.co.uk
            expected_teams=22,
            start_year=start_year,
            end_year=end_year
        )
```

2. Add to `scrape_all_divisions()` scrapers list (line 328)
3. Update `verificar_english_leagues.py` expected teams dict (line 51)

### Performance Considerations

- **Rate limiting**: 0.5s delay between requests (line 261)
- **Parallel processing**: Currently sequential; could parallelize division scraping
- **Memory efficiency**: Processes ~110 seasons (~2,500 records) without issues
- **Execution time**: ~3-5 minutes for full 5-division scrape

### Common Issues & Solutions

**Issue**: National League seasons with 22-23 teams instead of 24
**Cause**: COVID-19 seasons (2020-21, 2021-22) had shortened/modified formats
**Solution**: Current code logs warning but accepts; update `expected_teams` to tuple if recurring

**Issue**: pandas SettingWithCopyWarning in tracking generation
**Cause**: DataFrame slicing in `create_tracking()` line 461-462
**Solution**: Use `.copy()` when creating `team_data` slice (non-critical warning)

**Issue**: Team name inconsistencies across divisions
**Cause**: Different naming conventions (e.g., "Man United" vs. "Manchester Utd")
**Solution**: `clean_team_name()` standardizes, but manual mapping may be needed for edge cases
