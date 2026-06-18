# worldcup-2026

2026 FIFA World Cup prediction project. Data-driven match analysis and forecasting using ESPN API + statistical modeling.

## Quick Start

```bash
# 1. Update match data from ESPN
python predict.py

# 2. Run v7 prediction engine
python predict_v7.py
```

## Project Structure

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project rules for Claude Code (output format, timezone, workflow) |
| `predict.py` | ESPN data collector |
| `predict_v7.py` | v7 prediction engine (latest) |
| `player_database_v6.json` | Player ratings database |
| `referee_database_v6.json` | Referee style database |
| `worldcup_data.json` | Live match data |
| `MODEL_RULES.md` | Prediction model rules reference |
| `memory_backup/` | Model evolution history & match reviews |

## Prediction Reports (Chinese)

| Date | Content | Files |
|------|---------|-------|
| Jun 18 | Match review + Jun 19 predictions (4 matches) | `.md` + `_手机版.txt` |
| Jun 17 | Post-match review | `.md` |

## Workflow

1. Web search for latest match results & team news
2. Generate `.md` analysis with detailed breakdown
3. Auto-generate `_手机版.txt` mobile-optimized version
4. Update memory files after each match day

## Disclaimer

All predictions are for entertainment only. Football is beautiful because it's unpredictable.
