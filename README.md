# HAWK: Honed Anticipation of Wideout Kinematics 🦅

An analysis for the 2026 NFL Big Data Bowl Analytics Competition.

## Overview
This repo explores player movement from ball release to catch using Next Gen Stats tracking data.  
The "HAWK Index" measures reaction latency, acceleration efficiency, and pursuit geometry.

## Structure
- `data/`: Raw competition CSVs (not tracked in Git)
- `notebooks/`: Exploratory and metric notebooks
- `src/`: Core metric code (HAWK calculation)
- `outputs/`: Figures, metrics, submission files

## Notebooks

### `01_HAWK_Starter.ipynb`
Starter notebook for exploring the NFL Big Data Bowl 2026 data structure and calculating ball release frames.

### `02_safety_reaction_model.ipynb`
Analysis of defensive safety (FS/SS) reactions to ball release. Tests the hypothesis that safeties have delayed reactions and slower velocity/acceleration on complete passes vs incomplete passes.

**Key Findings:**
- Analyzed 18,072 safety-play combinations across 4,286 plays
- Hypothesis **not strongly supported** - safety reactions are remarkably similar between complete and incomplete passes
- Statistically significant differences found are small in magnitude and often in opposite direction of hypothesis
- See `SAFETY_REACTION_ANALYSIS_SYNOPSIS.md` for detailed results

## Setup
```bash
pip install -r requirements.txt
```
