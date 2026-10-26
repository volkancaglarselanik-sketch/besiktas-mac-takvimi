import json, urllib.request, datetime
def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)
def show(e, full=False):
    c = e["competitions"][0]
    teams = " vs ".join(f'{t["homeAway"]}:{t["team"]["displayName"]}' for t in c["competitors"])
    st = (c.get("status") or e.get("status") or {}).get("type", {})
    print(" ", e["id"], e["date"], "tv=", c.get("timeValid"), e.get("timeValid"), st.get("name"), st.get("detail"), teams, "|", (e.get("league") or c.get("league") or {}).get("name") if isinstance(e.get("league") or c.get("league"), dict) else e.get("season",{}).get("slug"))
    if full: print(json.dumps(e, ensure_ascii=False)[:3000])
B = "https://site.api.espn.com/apis/site/v2/sports/soccer"
for lg in ["all", "tur.1", "uefa.europa", "tur.cup"]:
    u = f"{B}/{lg}/teams/1895/schedule?fixture=true"
    try: d = get(u)
    except Exception as ex: print(lg, "schedule ERROR", ex); continue
    evs = d.get("events", [])
    print(f"== schedule {lg}: {len(evs)} events")
    for i, e in enumerate(evs[:60]): show(e, full=(i == 0 and lg == "tur.1"))
today = datetime.date.today()
for lg in ["tur.1", "uefa.europa"]:
    rng = f"{today:%Y%m%d}-{today + datetime.timedelta(days=60):%Y%m%d}"
    try: d = get(f"{B}/{lg}/scoreboard?dates={rng}&limit=500")
    except Exception as ex: print(lg, "scoreboard ERROR", ex); continue
    evs = [e for e in d.get("events", []) if "1895" in [t["team"]["id"] for t in e["competitions"][0]["competitors"]]]
    print(f"== scoreboard {lg} {rng}: {len(d.get('events',[]))} total, {len(evs)} bjk")
    for e in evs: show(e)
