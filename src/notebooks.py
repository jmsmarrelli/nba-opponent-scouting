"""Build and execute notebooks that review the included result tables."""
from pathlib import Path
import os, sys, json
import nbformat as nb
from nbclient import NotebookClient
ROOT = Path(__file__).resolve().parents[1]


def execute(jobs):
    os.environ.setdefault("OMP_NUM_THREADS", "4")
    cache = ROOT / ".cache"
    cache.mkdir(exist_ok=True)
    for key, folder in [("JUPYTER_RUNTIME_DIR", "runtime"), ("IPYTHONDIR", "ipython"), ("MPLCONFIGDIR", "matplotlib")]:
        path = cache / folder
        path.mkdir(exist_ok=True)
        os.environ[key] = str(path)
    spec = cache / "jupyter/kernels/review"
    spec.mkdir(parents=True, exist_ok=True)
    (spec / "kernel.json").write_text(json.dumps({"argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"], "display_name": "Python 3", "language": "python"}))
    os.environ["JUPYTER_PATH"] = str(cache / "jupyter")
    (ROOT / "notebooks").mkdir(exist_ok=True)
    for stem, title, code, table, figures, limits in jobs:
        book = nb.v4.new_notebook(metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}, "language_info": {"name": "python", "version": "3.12"}})
        setup = "from pathlib import Path\nimport numpy as np\nimport pandas as pd\nimport json\nfrom IPython.display import display, Image\nroot = Path.cwd()\nif root.name == 'notebooks':\n    root = root.parent\np = root / 'projects' / " + repr(stem)
        book.cells = [
            nb.v4.new_markdown_cell("# " + title + "\n\nJoseph Smarrelli · September 2026\n\nThis notebook recalculates selected findings from the included derived tables. It does not refit the underlying models. See the repository README for the complete source-data build and the accompanying article for interpretation."),
            nb.v4.new_code_cell(setup),
            nb.v4.new_markdown_cell("## Recalculate the result\nThe assertions check that the article’s reported quantities agree with the delivered tables."),
            nb.v4.new_code_cell(code),
            nb.v4.new_markdown_cell("## Inspect the estimates"),
            nb.v4.new_code_cell(table),
            nb.v4.new_markdown_cell("## Figures"),
            nb.v4.new_code_cell("\n".join("display(Image(filename=str(root / " + repr(f) + ")))" for f in figures)),
            nb.v4.new_markdown_cell("## Interpretation limits\n" + limits),
        ]
        NotebookClient(book, timeout=300, kernel_name="review", resources={"metadata": {"path": str(ROOT)}}).execute()
        for cell in book.cells:
            cell.metadata.pop("execution", None)
        path = ROOT / "notebooks" / (stem + ".ipynb")
        nb.write(book, path)
        print(path.name, "executed", flush=True)

JOBS = [('01_opponent_scouting',
  'Opponent scouting: verify the denominators',
  "d = pd.read_csv(root / 'data/team_games.csv.gz')\n"
  "profiles = pd.read_csv(root / 'results/team_profiles.csv')\n"
  'assert d.game_id.nunique() == 1212\n'
  "pooled = d.groupby('team')[['oreb', 'opp_dreb', 'fga', 'fgm', 'fg3m', 'fta', 'tov']].sum()\n"
  "pooled['oreb_rate'] = pooled.oreb / (pooled.oreb + pooled.opp_dreb)\n"
  "pooled['efg'] = (pooled.fgm + 0.5 * pooled.fg3m) / pooled.fga\n"
  "published = profiles.loc[profiles.side.eq('Offense')].set_index('team')\n"
  "assert np.allclose(pooled.oreb_rate, published.loc[pooled.index, 'oreb_rate'])\n"
  "assert np.allclose(pooled.efg, published.loc[pooled.index, 'efg'])\n"
  "display(pooled.loc[['OKC', 'DEN', 'HOU']])",
  "display(profiles.loc[profiles.team.isin(['OKC', 'DEN', 'HOU'])])",
  ['figures/OKC_shot_profile.png', 'figures/DEN_shot_profile.png'],
  'Player rebounds exclude team rebounds. Possession rates are estimates; the sheets label their '
  'denominators. Location data do not show defensive positioning, and the written film questions '
  'are not completed film coding.')]

if __name__ == "__main__":
    execute(JOBS)
