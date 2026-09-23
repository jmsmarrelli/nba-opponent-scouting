"""Build offense and defense summaries from reconciled public events."""
import numpy as np
import pandas as pd
from .common import ROOT,TEAM
from .audit import audit_games

def factors(box):
    d=box.copy()
    d['efg']=(d.fgm+.5*d.fg3m)/d.fga
    d['estimated_possessions']=d.fga-d.oreb+d.tov+.44*d.fta
    d['turnover_rate']=d.tov/d.estimated_possessions
    d['oreb_rate']=d.oreb/(d.oreb+d.opp_dreb)
    d['free_throw_rate']=d.fta/d.fga
    d['points_per_estimated_possession']=d.points/d.estimated_possessions
    d['estimated_pace48']=2880*d.estimated_possessions/d.seconds
    return d

def run():
    for name in ['results','figures','reports']: (ROOT/name).mkdir(exist_ok=True)
    e,s=audit_games();s=s[s.GAME_ID.isin(e.gameId.unique())].copy()
    miss=e.actionType.eq('Missed Shot') | (e.actionType.eq('Free Throw')&e.description.str.startswith('MISS',na=False))
    shooter=e.teamId.where(miss).groupby([e.gameId,e.period]).ffill()
    rb=e[e.actionType.eq('Rebound')&e.personId.gt(0)&~e.personId.isin(TEAM)].copy()
    rb['oreb']=rb.teamId.eq(shooter.loc[rb.index]);rb['dreb']=~rb.oreb
    rebounds=rb.groupby(['gameId','teamId'])[['oreb','dreb']].sum()
    records=[]
    for game,g in e.groupby('gameId'):
        home,away=g.home.iloc[0],g.away.iloc[0]
        final=g.iloc[-1];duration=2880+max(int(g.period.max())-4,0)*300
        for team,opp,score in [(home,away,'scoreHome'),(away,home,'scoreAway')]:
            tid=next(k for k,v in TEAM.items() if v==team);oid=next(k for k,v in TEAM.items() if v==opp)
            sh=s[s.GAME_ID.eq(game)&s.team.eq(team)]
            own=g[g.teamId.eq(tid)]
            def count(ident,column):
                return int(rebounds.loc[(game,ident),column]) if (game,ident) in rebounds.index else 0
            records.append(dict(game_id=game,team=team,opponent=opp,seconds=duration,points=int(final[score]),fga=len(sh),fgm=int(sh.made.sum()),fg3m=int(sh.loc[sh.three,'made'].sum()),fta=int(own.actionType.eq('Free Throw').sum()),tov=int(own.actionType.eq('Turnover').sum()),oreb=count(tid,'oreb'),dreb=count(tid,'dreb'),opp_dreb=count(oid,'dreb')))
    box=pd.DataFrame(records);box.to_csv(ROOT/'data/team_games.csv.gz',index=False)
    summaries=[]
    for side in ['Offense','Defense']:
        key='team' if side=='Offense' else 'opponent'
        aggregate=box.groupby(key).sum(numeric_only=True).drop(columns='game_id')
        aggregate['games']=box.groupby(key).size()
        aggregate.index.name='team';out=factors(aggregate.reset_index());out['side']=side;summaries.append(out)
    pd.concat(summaries).to_csv(ROOT/'results/team_profiles.csv',index=False)
    s['zone']=s.SHOT_ZONE_BASIC.replace({'Left Corner 3':'Corner three','Right Corner 3':'Corner three','Restricted Area':'Rim','In The Paint (Non-RA)':'Other paint','Mid-Range':'Midrange','Above the Break 3':'Above-break three','Backcourt':'Backcourt'})
    zones=[]
    for side,key in [('Offense','team'),('Defense','opponent')]:
        z=s.groupby([key,'zone']).agg(attempts=('made','size'),makes=('made','sum'),points=('points','sum')).reset_index().rename(columns={key:'team'})
        z['share']=z.attempts/z.groupby('team').attempts.transform('sum');z['fg_pct']=z.makes/z.attempts;z['side']=side;zones.append(z)
    pd.concat(zones).to_csv(ROOT/'results/zone_profiles.csv',index=False)
    print(len(box),'team-game rows; source audit complete')

if __name__=='__main__':run()
