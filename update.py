"""Beşiktaş maç takvimini ESPN'den çekip besiktas.ics dosyasını günceller.

Veri alınamazsa dosyaya dokunmadan hata ile çıkar; böylece telefondaki
takvim boşalmaz, GitHub da çalıştırmayı başarısız olarak işaretler.
"""
import json
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

TEAM_ID = "1895"  # ESPN: Besiktas
URL = f"https://site.api.espn.com/apis/site/v2/sports/soccer/all/teams/{TEAM_ID}/schedule?fixture=true"
OUT = "besiktas.ics"
TSI = timezone(timedelta(hours=3))

NAMES = {
    "Besiktas": "Beşiktaş", "Kasimpasa": "Kasımpaşa", "Genclerbirligi": "Gençlerbirliği",
    "Caykur Rizespor": "Çaykur Rizespor", "Goztepe": "Göztepe", "Eyupspor": "Eyüpspor",
    "Fenerbahce": "Fenerbahçe", "Erzurum BB": "Erzurumspor", "Amed SFK": "Amed SK",
    "Istanbul Basaksehir": "Başakşehir", "Hapoel Be'er": "Hapoel Beer-Sheva",
    "Union St.-Gilloise": "Union Saint-Gilloise", "Omonia Nicosia": "Omonia",
    "Fatih Karagumruk": "Fatih Karagümrük", "Antalyaspor": "Antalyaspor",
}
LEAGUES = {
    "Turkish Super Lig": "Süper Lig", "UEFA Europa League": "UEFA Avrupa Ligi",
    "UEFA Champions League": "UEFA Şampiyonlar Ligi", "UEFA Conference League": "UEFA Konferans Ligi",
    "Turkish Cup": "Türkiye Kupası", "Turkish Super Cup": "Süper Kupa",
}


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def league_name(ev):
    lg = ev.get("league") or ev["competitions"][0].get("league") or {}
    name = lg.get("name") if isinstance(lg, dict) else None
    name = name or (ev.get("seasonType") or {}).get("name") or ""
    for en, tr in LEAGUES.items():
        if en in name:
            return tr
    return name


def parse(data):
    matches = []
    for ev in data.get("events", []):
        comp = ev["competitions"][0]
        teams = {t["homeAway"]: t["team"] for t in comp["competitors"]}
        if "home" not in teams or "away" not in teams:
            continue
        name = lambda t: NAMES.get(t["displayName"], t["displayName"])
        start = datetime.strptime(ev["date"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)
        matches.append({
            "id": ev["id"],
            "title": f'{name(teams["home"])} – {name(teams["away"])}',
            "start": start,
            "time_known": bool(comp.get("timeValid", ev.get("timeValid", False))),
            "league": league_name(ev),
            "venue": (comp.get("venue") or {}).get("fullName", ""),
        })
    return sorted(matches, key=lambda m: m["start"])


def fold(line):
    b = line.encode("utf-8")
    out = []
    while len(b) > 74:
        cut = 74
        while (b[cut] & 0xC0) == 0x80:
            cut -= 1
        out.append(b[:cut])
        b = b[cut:]
    out.append(b)
    return "\r\n ".join(x.decode("utf-8") for x in out)


def esc(s):
    return s.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


def build(matches, stamp):
    L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//besiktas-mac-takvimi//TR", "CALSCALE:GREGORIAN",
         "METHOD:PUBLISH", "X-WR-CALNAME:Beşiktaş Maçları", "X-WR-TIMEZONE:Europe/Istanbul",
         "REFRESH-INTERVAL;VALUE=DURATION:PT6H", "X-PUBLISHED-TTL:PT6H"]
    for m in matches:
        title = m["title"]
        L += ["BEGIN:VEVENT", f'UID:espn-{m["id"]}@besiktas-mac-takvimi', f"DTSTAMP:{stamp}",
              fold("SUMMARY:" + esc("⚽ " + title))]
        if m["venue"]:
            L.append(fold("LOCATION:" + esc(m["venue"])))
        if m["time_known"]:
            end = m["start"] + timedelta(hours=2)
            L += [f'DTSTART:{m["start"]:%Y%m%dT%H%M%SZ}', f"DTEND:{end:%Y%m%dT%H%M%SZ}",
                  fold("DESCRIPTION:" + esc(m["league"]))]
            alarms = [("-P1D", "Yarın maç var: " + title), ("-PT1H", "1 saat sonra maç: " + title)]
        else:
            day = m["start"].astimezone(TSI).date()
            L += [f"DTSTART;VALUE=DATE:{day:%Y%m%d}", f"DTEND;VALUE=DATE:{day + timedelta(days=1):%Y%m%d}",
                  "TRANSP:TRANSPARENT",
                  fold("DESCRIPTION:" + esc(m["league"] + " · Saat henüz açıklanmadı · tarih değişebilir"))]
            alarms = [("-PT4H", "Yarın maç var: " + title), ("PT10H", "Bugün maç var: " + title)]
        for trig, text in alarms:
            L += ["BEGIN:VALARM", "ACTION:DISPLAY", f"TRIGGER:{trig}", fold("DESCRIPTION:" + esc(text)), "END:VALARM"]
        L.append("END:VEVENT")
    L.append("END:VCALENDAR")
    return "\r\n".join(L) + "\r\n"


def without_stamps(text):
    return "\n".join(l for l in text.splitlines() if not l.startswith("DTSTAMP:"))


def main():
    try:
        matches = parse(fetch())
    except Exception as e:
        sys.exit(f"Veri alınamadı, takvim değiştirilmedi: {e}")
    if not matches:
        sys.exit("ESPN hiç maç döndürmedi, takvim değiştirilmedi.")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    new = build(matches, stamp)
    try:
        with open(OUT, encoding="utf-8", newline="") as f:
            old = f.read()
    except FileNotFoundError:
        old = ""
    if without_stamps(old) == without_stamps(new):
        print(f"Değişiklik yok ({len(matches)} maç).")
        return
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write(new)
    print(f"Takvim güncellendi: {len(matches)} maç.")
    for m in matches:
        when = m["start"].astimezone(TSI).strftime("%d.%m.%Y %H:%M" if m["time_known"] else "%d.%m.%Y (saat yok)")
        print(f'  {when}  {m["title"]}  [{m["league"]}]')


if __name__ == "__main__":
    main()
