from pathlib import Path
import json
import xml.etree.ElementTree as ET

# ----------------------------------------------------------
# Pfade
# ----------------------------------------------------------

BASE = Path(__file__).resolve().parent.parent

MOVIES = BASE / "Web-Tools" / "MB Series-Base" / "Series"
OUTPUT = BASE / "Web-Tools" / "MB Series-Base" / "series.json"


# ----------------------------------------------------------
# XML-Hilfsfunktion
# ----------------------------------------------------------

def xml_text(root, tag):
    element = root.find(tag)

    if element is None or element.text is None:
        return ""

    return element.text.strip()


# ----------------------------------------------------------
# Einen Film lesen
# ----------------------------------------------------------

def read_serie(folder: Path):

    # ---------- NFO suchen ----------

    nfo_files = list(folder.glob("*.nfo"))

    if len(nfo_files) == 0:
        print(f"❌ {folder.name}: keine NFO gefunden")
        return None

    if len(nfo_files) > 1:
        print(f"❌ {folder.name}: mehrere NFO-Dateien gefunden")
        return None

    nfo = nfo_files[0]

    # ---------- Poster suchen ----------

    poster_files = list(folder.glob("poster.jpg"))

    if len(poster_files) > 1:
        print(f"⚠ {folder.name}: mehrere Poster gefunden")

    poster = poster_files[0] if poster_files else None

    # ---------- XML laden ----------

    try:
        root = ET.parse(nfo).getroot()
    except ET.ParseError:
        text = nfo.read_text(encoding="utf-8", errors="ignore")
        text = text.replace("&", "&amp;")
        try:
            root = ET.fromstring(text)
            print(f"⚠ {folder.name}: '&' automatisch repariert")
        except Exception as e:
            print(f"❌ {folder.name}: XML-Fehler ({e})")
            return None

    # ---------- Filmobjekt ----------

    season_count = len(root.findall("namedseason"))

    serie = {
        "id": xml_text(root, "id"),
        "title": xml_text(root, "title"),
        "plot": xml_text(root, "plot"),
        "mpaa": xml_text(root, "mpaa"),
        "year": xml_text(root, "premiered")[:4],
        "seasons": season_count,

        "folder": folder.name,
        "filename": nfo.stem,

        "poster": (
            f"Series/{folder.name}/{poster.name}"
            if poster else ""
        ),
    }

    return serie


# ----------------------------------------------------------
# Alle Filme sammeln
# ----------------------------------------------------------

series = []

folders = sorted(
    [folder for folder in MOVIES.iterdir() if folder.is_dir()],
    key=lambda folder: int(folder.name)
)

for folder in folders:

    serie = read_serie(folder)

    if not serie:
        continue

    if serie["id"] == "":
        print(f"❌ {folder.name}: keine ID gefunden")
        continue

    series.append(serie)

series.sort(key=lambda serie: int(serie["id"][1:]))

# ----------------------------------------------------------
# JSON erzeugen
# ----------------------------------------------------------

json_text = json.dumps(
    series,
    ensure_ascii=False,
    indent=4
)

# ----------------------------------------------------------
# Nur speichern wenn nötig
# ----------------------------------------------------------

if OUTPUT.exists():

    old_json = OUTPUT.read_text(encoding="utf-8")

    if old_json == json_text:
        print("✅ series.json ist bereits aktuell.")
        raise SystemExit

OUTPUT.write_text(
    json_text,
    encoding="utf-8"
)

print()
print(f"✅ {len(series)} Serien verarbeitet.")
print("💾 series.json wurde aktualisiert.")