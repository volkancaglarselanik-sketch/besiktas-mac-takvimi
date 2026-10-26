import json, re, sys
from datetime import datetime, timedelta
html = open("fikstur.html", encoding="utf-8").read()
state = json.loads(re.search(r'id="state">(.*?)</script>', html, re.S).group(1))
COMP = {"SL":"Süper Lig","UEL":"UEFA Avrupa Ligi","TK":"Türkiye Kupası","OT":"Diğer"}
stamp = "20261026T200000Z"
def fold(line):
    b = line.encode("utf-8"); out = []
    while len(b) > 74:
        cut = 74
        while (b[cut] & 0xC0) == 0x80: cut -= 1
        out.append(b[:cut]); b = b[cut:]
    out.append(b)
    return "\r\n ".join(x.decode("utf-8") for x in out)
def esc(s): return s.replace("\\","\\\\").replace(",","\\,").replace(";","\\;")
L = ["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//kartal-mac-takvimi//TR","CALSCALE:GREGORIAN","METHOD:PUBLISH",
     "X-WR-CALNAME:Beşiktaş Maçları","X-WR-TIMEZONE:Europe/Istanbul",
     "REFRESH-INTERVAL;VALUE=DURATION:PT12H","X-PUBLISHED-TTL:PT12H"]
n = 0
for m in state["matches"]:
    if not m["date"]: continue
    title = ("Beşiktaş – "+m["opp"]) if m["home"] else (m["opp"]+" – Beşiktaş")
    d = datetime.strptime(m["date"], "%Y-%m-%d")
    desc = f'{COMP[m["comp"]]} · {m["round"]}'
    L += ["BEGIN:VEVENT", f'UID:bjk-2026-27-{m["id"]}@kartal-mac-takvimi', f"DTSTAMP:{stamp}",
          fold("SUMMARY:"+esc("⚽ "+title))]
    if m["time"]:
        h, mi = map(int, m["time"].split(":"))
        start = d + timedelta(hours=h-3, minutes=mi)  # TSİ = UTC+3
        end = start + timedelta(hours=2)
        L += [f"DTSTART:{start:%Y%m%dT%H%M%S}Z", f"DTEND:{end:%Y%m%dT%H%M%S}Z", fold("DESCRIPTION:"+esc(desc))]
        alarms = [("-P1D","Yarın maç var: "+title), ("-PT1H","1 saat sonra maç: "+title)]
    else:
        L += [f"DTSTART;VALUE=DATE:{d:%Y%m%d}", f"DTEND;VALUE=DATE:{d+timedelta(days=1):%Y%m%d}",
              "TRANSP:TRANSPARENT", fold("DESCRIPTION:"+esc(desc+" · Saat henüz açıklanmadı"))]
        alarms = [("-PT4H","Yarın maç var: "+title), ("PT10H","Bugün maç var: "+title)]
    for trig, text in alarms:
        L += ["BEGIN:VALARM","ACTION:DISPLAY",f"TRIGGER:{trig}",fold("DESCRIPTION:"+esc(text)),"END:VALARM"]
    L += ["END:VEVENT"]; n += 1
L.append("END:VCALENDAR")
open(sys.argv[1], "w", encoding="utf-8", newline="").write("\r\n".join(L)+"\r\n")
print(n, "events")
