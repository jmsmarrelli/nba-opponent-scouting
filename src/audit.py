"""Reconcile event and shot records before building scouting summaries."""
import re
import numpy as np
import pandas as pd
from .common import ROOT, TEAM, shots

def clock_seconds(value):
    m = re.fullmatch(r"PT(\d+)M([\d.]+)S", value)
    if not m:
        raise ValueError(value)
    return int(m[1]) * 60 + float(m[2])

def audit_games():
    s = shots(2025)
    sg = dict(tuple(s.groupby("GAME_ID")))
    raw = pd.read_csv(ROOT / "data/raw/nbastatsv3_2025.csv", low_memory=False)
    raw["seconds"] = raw.clock.map(clock_seconds)
    raw["teamId"] = np.where(
        raw.teamId.gt(0), raw.teamId, np.where(raw.personId.isin(TEAM), raw.personId, 0)
    )
    audits = []
    valid = []
    for game, g in raw.groupby("gameId"):
        if game not in sg:
            continue
        g = g.sort_values("actionId").copy()
        chart = sg[game]
        reasons = []
        if g.actionId.duplicated().any():
            reasons.append("duplicate order")
        for score in ["scoreHome", "scoreAway"]:
            g[score] = g[score].ffill().fillna(0)
            if g[score].diff().fillna(0).lt(0).any():
                reasons.append("score decreased")
            if g[score].diff().fillna(0).gt(4).any():
                reasons.append("score jump")
        for period, p in g.groupby("period"):
            if p.seconds.diff().fillna(0).gt(0.01).any():
                reasons.append("clock reversal")
            if (
                p.seconds.iloc[0] != (720 if period <= 4 else 300)
                or p.seconds.iloc[-1] != 0
            ):
                reasons.append("incomplete clock")
        fg = g[g.isFieldGoal.eq(1)]
        if fg.actionNumber.duplicated().any():
            reasons.append("duplicate FG event")
        else:
            j = fg.merge(
                chart,
                left_on="actionNumber",
                right_on="GAME_EVENT_ID",
                validate="one_to_one",
            )
            agree = (
                j.personId.eq(j.PLAYER_ID)
                & j.shotValue.eq(np.where(j.three, 3, 2))
                & j.shotResult.eq(np.where(j.made, "Made", "Missed"))
            )
            if len(j) != len(fg) or len(j) != len(chart) or not agree.all():
                reasons.append("shot feed disagreement")
        home = chart.HTM.iloc[0]
        away = chart.VTM.iloc[0]
        ft = g[
            g.actionType.eq("Free Throw")
            & ~g.description.str.startswith("MISS", na=False)
        ]
        for team, col in [(home, "scoreHome"), (away, "scoreAway")]:
            ident = next(k for k, v in TEAM.items() if v == team)
            points = (
                fg[fg.teamId.eq(ident)].shotValue
                * fg[fg.teamId.eq(ident)].shotResult.eq("Made")
            ).sum() + int(ft.teamId.eq(ident).sum())
            if points != g[col].iloc[-1]:
                reasons.append("scoring reconciliation")
        audits.append(
            dict(
                game_id=game,
                status="; ".join(sorted(set(reasons))) if reasons else "valid",
                home=home,
                away=away,
                date=str(chart.date.iloc[0].date()),
            )
        )
        if not reasons:
            g["date"] = str(chart.date.iloc[0].date())
            g["home"] = home
            g["away"] = away
            valid.append(g)
    pd.DataFrame(audits).to_csv(ROOT / "results/game_audit.csv", index=False)
    return pd.concat(valid), s
