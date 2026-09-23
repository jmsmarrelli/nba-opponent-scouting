import pandas as pd
import numpy as np
from src.prepare import factors
from src.common import ROOT

def test_offensive_rebound_denominator_uses_opponent_defensive_rebounds():
    d=pd.DataFrame(dict(fgm=[40],fg3m=[10],fga=[90],oreb=[10],dreb=[50],opp_dreb=[30],tov=[12],fta=[20],points=[110],seconds=[2880]))
    x=factors(d).iloc[0]
    assert np.isclose(x.oreb_rate,.25)
    assert np.isclose(x.estimated_possessions,100.8)
    assert np.isclose(x.estimated_pace48,100.8)

def test_scouting_games_use_audited_records():
    d=pd.read_csv(ROOT/'data/team_games.csv.gz');a=pd.read_csv(ROOT/'results/game_audit.csv')
    valid=set(a.loc[a.status.eq('valid'),'game_id'])
    assert set(d.game_id)==valid
    assert d.groupby('game_id').size().eq(2).all()
    assert not d.duplicated(['game_id','team']).any()

def test_opponent_rebounds_reconcile():
    d=pd.read_csv(ROOT/'data/team_games.csv.gz')
    j=d.merge(d[['game_id','team','dreb']],left_on=['game_id','opponent'],right_on=['game_id','team'],suffixes=('','_opponent'),validate='one_to_one')
    assert j.opp_dreb.eq(j.dreb_opponent).all()

def test_zone_shares_and_scoring_reconcile():
    z=pd.read_csv(ROOT/'results/zone_profiles.csv')
    assert np.allclose(z.groupby(['team','side']).share.sum(),1)
    d=pd.read_csv(ROOT/'data/team_games.csv.gz')
    offense=z[z.side.eq('Offense')].groupby('team').attempts.sum()
    assert offense.eq(d.groupby('team').fga.sum()).all()
