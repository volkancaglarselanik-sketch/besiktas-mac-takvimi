import json, urllib.request, datetime
def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)
today = datetime.date.today()
rng = f"{today:%Y%m%d}-{today + datetime.timedelta(days=300):%Y%m%d}"
for lg in ["tur.1", "uefa.europa", "tur.cup", "tur.super_cup"]:
    u = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{lg}/scoreboard?dates={rng}&limit=1000"
    try:
        d = get(u)
    except Exception as e:
        print(lg, "ERROR", e); continue
    evs = d.get("events", [])
    bjk = [e for e in evs if "besiktas" in json.dumps(e.get("competitions", [{}])[0].get("competitors", []), ensure_ascii=True).lower()]
    print(f"== {lg}: {len(evs)} events, {len(bjk)} Besiktas, league={d.get('leagues',[{}])[0].get('name')}")
    for e in bjk[:40]:
        c = e["competitions"][0]
        teams = " vs ".join(f'{t["homeAway"]}:{t["team"]["displayName"]}' for t in c["competitors"])
        print(e["id"], e["date"], "timeValid=", c.get("timeValid"), e.get("timeValid"), e["status"]["type"]["name"], e["status"]["type"].get("detail"), teams, "|", c.get("venue",{}).get("fullName"))
    if bjk:
        print(json.dumps(bjk[0], ensure_ascii=False)[:2500])
try:
    d = get("https://site.api.espn.com/apis/site/v2/sports/soccer/tur.1/teams")
    for t in d["sports"][0]["leagues"][0]["teams"]:
        if "besik" in t["team"]["displayName"].lower().replace("ş","s"): print("TEAM", t["team"]["id"], t["team"]["displayName"])
except Exception as e: print("teams ERROR", e)
