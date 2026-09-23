"""Render completed offense and defense scouting sheets from cached summaries."""
from pathlib import Path
import argparse,base64,html
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from .common import ROOT

NOTES={
'OKC':[
('Locate the corner passes','Review the pass before each corner attempt against OKC, including attempts to reach the corner that end in turnovers. A location share alone does not show whether the shot was open.'),
('Review foul trips separately','Pair shot outcomes with shooting and nonshooting foul sequences. Field-goal percentage omits trips to the line that never create a field goal attempt.'),
('Tag the first defensive rotation','Use the possession record to locate help, the next pass and the recovery. The public data here do not identify those actions or prescribe a coverage.')],
'DEN':[
('Separate direct scoring from passing possessions','A shot profile records the final shooter. Review the entry, help decision and pass sequence around Denver’s primary creators before assigning a defensive cause.'),
('Track the rebound after the contest','Compare defensive recoveries and Denver offensive rebounds from similar miss locations. Team rates alone do not identify who missed an assignment.'),
('Check the current personnel','The completed-season profile mixes historical lineups. Confirm the players and rotations expected in the upcoming matchup before choosing film examples.')],
'HOU':[
('Review perimeter rebounding responsibilities','Compare Houston offensive rebounds after threes with similar misses the defense secured. Identify first contact, the eventual rebounder and outlet protection.'),
('Separate the shot from the second chance','A possession with several misses can end in a score. Review offensive-rebound sequences alongside the field-goal location profile.'),
('Compare both sides of the floor','Use the offense and defense panels to define separate review questions. These descriptive rates do not establish the value of a different scheme.')]
}

def render(team):
    d=pd.read_csv(ROOT/'results/team_profiles.csv');z=pd.read_csv(ROOT/'results/zone_profiles.csv');g=d[d.team.eq(team)]
    if len(g)!=2:raise ValueError('Team summaries not available')
    order=['Rim','Other paint','Midrange','Corner three','Above-break three','Backcourt']
    fig,axes=plt.subplots(1,2,figsize=(11,5),sharey=True)
    for ax,side in zip(axes,['Offense','Defense']):
        own=z[z.team.eq(team)&z.side.eq(side)].set_index('zone').reindex(order)
        league=z[z.side.eq(side)].groupby('zone').attempts.sum().reindex(order).fillna(0);league=league/league.sum()
        y=np.arange(len(order));ax.barh(y+.18,own.share.fillna(0)*100,height=.34,color='#176b87',label=team)
        ax.barh(y-.18,league*100,height=.34,color='#bbc5cb',label='League')
        ax.set_yticks(y,order);ax.set_xlabel('Share of attempts (%)');ax.set_title('Where they shoot' if side=='Offense' else 'Where opponents shoot')
        ax.spines[['top','right']].set_visible(False)
    axes[1].legend(loc='lower right');fig.suptitle(f'{team} | 2025–26 shot locations',fontweight='bold');fig.tight_layout()
    path=ROOT/f'figures/{team}_shot_profile.png';fig.savefig(path,dpi=180,metadata={'Software':None});fig.savefig(path.with_suffix('.svg'),metadata={'Creator':None,'Date':None});plt.close(fig)
    columns=[('efg','eFG%'),('turnover_rate','Turnovers / estimated possessions'),('oreb_rate','Player-rebound OREB%'),('free_throw_rate','FTA / FGA')]
    lines=['| Metric | Offense | Opponents |','| --- | ---: | ---: |']
    a=g[g.side.eq('Offense')].iloc[0];b=g[g.side.eq('Defense')].iloc[0]
    for key,label in columns:lines.append(f'| {label} | {a[key]:.1%} | {b[key]:.1%} |')
    notes=NOTES.get(team,[('Review the underlying events','Compare similar game situations before interpreting the rates as an opponent tendency.')])
    text=f'# {team}: opponent scouting sheet\n\nJoseph Smarrelli · September 2026\n\n2025–26 regular season. {int(a.games)} audited team games. The league reference uses 1,212 games that reconcile across event and shot records.\n\n'+ '\n'.join(lines)+f'\n\n![{team} offensive and defensive shot locations](../figures/{team}_shot_profile.png)\n\n## Film review priorities\n\n'+ '\n\n'.join(f'**{title}.** {note}' for title,note in notes)+'''\n\n## Definitions and limits\n\nEstimated possessions = FGA − player offensive rebounds + turnovers + 0.44 × FTA. Offensive-rebound percentage uses the offense’s player offensive rebounds divided by those rebounds plus the opponent’s player defensive rebounds. Team rebounds are excluded. These are documented public-data approximations; they are not asserted to match the official four-factor tables. Turnover rate uses estimated possessions rather than the alternative FGA + 0.44 × FTA + TOV denominator.\n\nThe defensive panel reports opponent offense. The figures contain no tracking, matchup adjustment or shot-clock information. Film priorities are proposed review questions; no film has been coded. Update availability and rotations before using this historical sheet for a game.\n\nSource: [pinned public NBA archive](https://github.com/shufinskiy/nba_data/tree/e829d4678be1e075f99e5d41a1c5f97089be446b). Source checksums, excluded games, team-game inputs and formulas are included in the repository.\n'''
    md=ROOT/f'reports/{team}_2025_26_scout.md';md.write_text(text)
    import markdown
    body=markdown.markdown(text,extensions=['tables'])
    encoded=base64.b64encode(path.read_bytes()).decode();body=body.replace(f'../figures/{team}_shot_profile.png',f'data:image/png;base64,{encoded}')
    css='body{font:17px/1.6 Georgia,serif;color:#172d45;max-width:900px;margin:45px auto;padding:0 22px}h1,h2{font-family:Arial,sans-serif}img{width:100%;height:auto}table{border-collapse:collapse;width:100%;font:15px Arial,sans-serif}th,td{padding:12px;border-bottom:1px solid #d8e0e5;text-align:left}a{color:#176b87}'
    md.with_suffix('.html').write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="author" content="Joseph Smarrelli"><title>{html.escape(team)} scouting sheet</title><style>{css}</style><body>{body}</body></html>')
    print(md.with_suffix('.html').name)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--team',nargs='+',default=['OKC','DEN','HOU']);args=p.parse_args()
    for team in args.team:render(team.upper())
