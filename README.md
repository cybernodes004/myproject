#!/usr/bin/env bash
# Legt den kompletten J.A.R.V.I.S.-Ordner an:  bash jarvis_bundle.sh
set -e
mkdir -p jarvis && cd jarvis
cat > '.gitignore' <<'JARVIS_EOF'
.venv/
venv/
__pycache__/
*.pyc
data/
certs/
backend/.env
voices/*.onnx
voices/*.onnx.json
voices/xtts/*.wav
frontend/vendor/
.DS_Store
JARVIS_EOF
cat > 'README.md' <<'JARVIS_EOF'
# J.A.R.V.I.S. – dein privater KI-Assistent

Läuft komplett auf **deinem eigenen Rechner**. Kein OpenAI, keine Cloud-KI, keine Abo-Kosten.
Nur **du** hast Zugang: ein Besitzer-Konto, Passwort, Zugriff nur aus deinem eigenen Netz.

---

## Bausteine (Technologie → Aufgabe)

| Technologie | Aufgabe | Wo im Code |
|---|---|---|
| **Python** (FastAPI) | Hauptprogramm, zentrale Steuerung | `backend/main.py` |
| **SQLite** | dauerhafte Speicherung (Chats, Gedächtnis, Aktionen, Termine) | `backend/core/db.py` |
| **ChromaDB** | semantisches Gedächtnis (Suche nach Bedeutung) | `backend/engines/memory.py` |
| **Embeddings** (`nomic-embed-text`, lokal) | Bedeutung von Texten erkennen | `backend/core/llm.py` |
| **LLM-API** (Ollama, lokal: `qwen2.5:7b`) | Intelligenz & Antworten, Werkzeug-Nutzung | `backend/core/llm.py` |
| **Whisper** (faster-whisper) | Sprache → Text (DE/TR/EN automatisch) | `backend/engines/voice.py` |
| **Text-to-Speech** (Piper / XTTS) | Antworten sprechen, mehrere weibliche Stimmen | `backend/engines/voice.py` |
| **Streamlit** | Jarvis-Steuerfenster (Verwaltung) | `backend/control_panel.py` |
| **HTML/JS-HUD** + d3 | Jarvis-Oberfläche: Kern, Knoten, Weltkugel, Fenster, Handy-App | `frontend/` |
| **Playwright** | Webseiten automatisch öffnen & lesen | `backend/agents/web_agent.py` |
| **Computer Vision** (`qwen2.5vl`) | Bildschirminhalte & Fotos erkennen | `backend/agents/computer_agent.py` |
| **Git / GitHub** | Quellcode & Versionen verwalten | `.git` (wird von `install.sh` angelegt) |

## Architektur (getrennte Komponenten)

```
                ┌────────────── Dashboard (HUD, Handy-App, Pop-out-Fenster) ──────────────┐
                │  Kern · Chat · Prozess-Knoten · Weltkugel · Fenster · Aktionen · Konsole │
                └───────────────────────────────┬──────────────────────────────────────────┘
   Steuerfenster (Streamlit) ───────────────────┤  HTTPS + Login-Token
                                                ▼
 ┌──────────────────────────── main.py · zentrale Steuerung ─────────────────────────────┐
 │  SECURITY AGENT  Login · nur eigenes Netz · Sperren · Protokoll                       │
 │  TASK AGENT      Verstehen → Gedächtnis → Planen → Werkzeuge → Antwort → Lernen        │
 │     ├─ MEMORY ENGINE   8 Gedächtnisarten · SQLite + ChromaDB + Embeddings             │
 │     ├─ VOICE ENGINE    Whisper · Piper · XTTS                                         │
 │     ├─ WEB AGENT       SearXNG-Suche · Playwright · Recherche                          │
 │     ├─ COMPUTER AGENT  Apps · Bildschirm sehen · Tippen/Klicken · Befehle · Dateien    │
 │     ├─ MEDIA AGENT     Bilder · Videos                                                 │
 │     ├─ SERVICES        Kalender · Erinnerungen · Automatisierung · Mail · Spotify · TG │
 │     └─ SYSTEM AGENT    Selbstdiagnose                                                  │
 │  SCHEDULER       Morgenbriefing · Erinnerungen · Automatisierungen · Nacht-Zusammenfassung │
 └────────────────────────────────────────────────────────────────────────────────────────┘
                     Ollama (Gehirn)   ·   SearXNG (Suche)   ·   data/ (alles Persönliche)
```

## Das Gedächtnis

| Gedächtnisart | Was es tut | Beispiel |
|---|---|---|
| **Persönliches Gedächtnis / Profil** | Name, Anrede, Über-mich, Fakten über dich | „Nenn mich Chef.“ → wird exakt gespeichert |
| **Regelgedächtnis** | dauerhafte Anweisungen, haben **immer Vorrang** | „Sprich ab jetzt nur Deutsch mit mir.“ |
| **Kurzzeitgedächtnis** | die letzten 20 Nachrichten des Chats | Rückfragen verstehen |
| **Langzeitgedächtnis** | Fakten, Vorlieben, Ziele, Projekte, dauerhaft | „Ich mag keinen Zucker im Kaffee.“ |
| **Gesprächsgedächtnis** | jede Nachricht wird indexiert + jede Nacht Tageszusammenfassung | „Was haben wir gestern an Nova geändert?“ |
| **Wissensgedächtnis** | hochgeladene Dateien, gespeicherte Webseiten, Recherchen | PDF hochladen → Fragen dazu stellen |
| **Verknüpfungsgedächtnis** | ähnliche Erinnerungen werden automatisch verbunden | „Nova“ ↔ „5000 € Ziel“ ↔ „Dark Mode“ |
| **Aktionsgedächtnis** | jedes ausgeführte Werkzeug mit Ergebnis & Dauer | im Tab ⚡ Aktionen und im Steuerfenster |

**Wie Jarvis lernt:** Nach jeder Antwort prüft Jarvis im Hintergrund, ob du etwas Dauerhaftes über dich gesagt hast.
Damit nichts Falsches gespeichert wird, gilt:
- Gelernt wird **nur aus deinen eigenen Aussagen** (nie aus Jarvis' Antworten).
- Jede neue Erinnerung muss sich **in deinen Worten wiederfinden**, sonst wird sie verworfen.
- Anrede und Sprache werden **ohne KI-Raten** per festem Muster erkannt (DE/TR/EN).
- Ähnliches wird **aktualisiert statt doppelt** gespeichert.
- Alles ist sichtbar und korrigierbar: Tab 🧠 Gedächtnis oder Steuerfenster.

## Was Jarvis kann
- 🎙 **Sprechen & Verstehen:** Whisper, Mikrofon-Taste, **Cmd/Strg + J**, oder 👏 **zweimal klatschen**
- 🔊 **Mehrere weibliche Stimmen**, pro Sprache wählbar (Einstellungen ⚙)
- ⚡ **Live-Antworten** Wort für Wort, mit **Prozess-Anzeige** (Knoten, Prozent, Millisekunden, Token/s)
- 📋 **Aufgaben in Schritte zerlegen** (`plan_task`) und selbstständig abarbeiten, mit **Selbstkorrektur** bei Fehlern
- 🌍 **Weltkugel:** „Zeig mir Tokio.“ → die Kugel dreht sich hin
- 🗔 **Info-Fenster**, Ergebnis-Anzeigen, Code-Ausgaben, Screenshots
- 🖥 **Computersteuerung:** Apps öffnen, Bildschirm ansehen, tippen, klicken, Befehle, Dateien lesen und schreiben. **Riskantes nur nach deiner Bestätigung mit Vorschau.**
- 🌐 **Web-Agent:** private Suche, Webseiten lesen (Playwright), **selbstständige Recherche** mit Quellen
- 🖼 **Bilder verstehen** (Foto anhängen) und **erstellen** (SDXL-Turbo)
- 🎬 **Videos bauen:** Szenen + Bilder + Jarvis-Stimme + Kamerafahrt → MP4
- 📅 Kalender, ⏰ Erinnerungen, ⚙ **Automatisierungen** („Jeden Morgen um 8: KI-News zusammenfassen“)
- ☀ **Proaktives Morgenbriefing:** Termine, Mails, News und ein Vorschlag passend zu deinen Zielen
- ✉ Gmail lesen & zusammenfassen, Entwürfe anlegen (sendet nie selbst) · 🎵 Spotify · 📱 Telegram
- 🎯 **Ziele & Projekte:** Jarvis kennt sie und hilft aktiv, auch beim Geldverdienen (Ideen, Pläne, Umsetzung)
- 🩺 **Selbstdiagnose:** „Jarvis, mach eine Selbstdiagnose.“ oder Tab 🩺 System
- 🖥🖥 **Mehrere Bildschirme:** jedes Panel per ⧉ in ein eigenes Fenster ziehen, alles bleibt live verbunden

## Voraussetzungen
- Mac mit Apple-Chip und **mindestens 16 GB RAM** (32 GB empfohlen). Linux/Windows mit NVIDIA geht auch.
- ca. 25 GB freier Speicher
- [Ollama](https://ollama.com/download), [Homebrew](https://brew.sh), optional [Docker Desktop](https://www.docker.com/products/docker-desktop/) oder OrbStack (für die Websuche)

## Installation (einmalig)
```bash
cd jarvis
./install.sh
```
Das Skript installiert Python 3.12, alle Pakete, den unsichtbaren Browser, die Modelle, Stimmen, Karte, das HTTPS-Zertifikat und Git.
Am Ende fragt es nach **deinem Benutzernamen und Passwort** (min. 12 Zeichen).

**Mac-Berechtigungen** für die Computersteuerung: Systemeinstellungen → Datenschutz & Sicherheit →
„Bildschirmaufnahme“ **und** „Bedienungshilfen“ → Terminal erlauben.

## Starten
```bash
./start.sh
```
| Was | Adresse |
|---|---|
| Dashboard | https://localhost:8443 (Zertifikatswarnung einmal bestätigen, es ist dein eigenes) |
| Steuerfenster | http://127.0.0.1:8501 (nur auf diesem Rechner) |
| Handy im WLAN | die Adresse, die `start.sh` anzeigt |

## Handy-App
1. Handy im **gleichen WLAN** → Adresse öffnen → Warnung bestätigen → einloggen
2. **iPhone:** Safari → Teilen → „Zum Home-Bildschirm“ · **Android:** Chrome → ⋮ → „App installieren“
3. **Unterwegs:** [Tailscale](https://tailscale.com) auf Mac und Handy (kostenlos, verschlüsselter privater Tunnel).
   Port 8443 **niemals** im Router freigeben, Jarvis blockt fremde Netze ohnehin.

## Sicherheit
- **Nur ein Konto:** `create_user.py` legt genau ein Besitzer-Konto an, eine Registrierung im Web gibt es nicht
- bcrypt-Passwort-Hash, Login-Token läuft nach 72 h ab, **Passwortänderung meldet alle Geräte ab**
- 5 falsche Passwörter → 15 Minuten Sperre · jeder Login und jeder Angriff landet im **Sicherheitsprotokoll**
- **Netzwerk-Schutz:** Anfragen aus dem Internet werden abgewiesen (nur eigener Rechner, Heim-WLAN, Tailscale)
- Computer-Agent: gesperrte Pfade (`.ssh`, Schlüsselbund, `.env` …), nur unter `FILE_ROOT`, **Bestätigung mit Vorschau**
- Telegram antwortet nur deiner Chat-ID, fremde Versuche werden protokolliert
- Alle Daten liegen in `data/`. Backup = Ordner kopieren. `data/`, `certs/`, `backend/.env` sind von Git ausgeschlossen.

### Ehrlich: was „nichts geht raus“ bedeutet
Die **KI selbst** schickt nie etwas an Dritte. Aber die Websuche fragt Suchmaschinen über deine eigene SearXNG
(ohne Konto, ohne Profil). Gmail, Spotify und Telegram reden zwangsläufig mit diesen Diensten.
Alle drei sind **optional**: Lässt du die Felder in `backend/.env` leer, bleibt Jarvis vollständig lokal.
**Instagram** ist bewusst nicht eingebaut. Es gibt keine offizielle Schnittstelle für private Konten,
und Bots führen oft zur Kontosperre.

## Dienste verbinden (optional, `backend/.env`)
- **Gmail:** 2-Faktor an → [App-Passwort](https://myaccount.google.com/apppasswords) → `IMAP_USER`, `IMAP_PASSWORD`
- **Google Kalender (lesen):** Kalender-Einstellungen → „Privatadresse im iCal-Format“ → `CALENDAR_ICS_URL`
- **Spotify** (Premium): [developer.spotify.com](https://developer.spotify.com/dashboard) → App, Redirect `http://127.0.0.1:8765/callback` → ID/Secret → einmal `cd backend && ../.venv/bin/python spotify_auth.py`
- **Telegram:** @BotFather → `TELEGRAM_TOKEN`; deine ID von @userinfobot → `TELEGRAM_CHAT_ID`
- **Bilder erstellen:** `.venv/bin/pip install -r backend/requirements-extra.txt` und `IMAGE_GEN=true`

## Echte, natürliche Stimme (XTTS, auch Türkisch weiblich)
```bash
.venv/bin/pip install -r backend/requirements-extra.txt
mkdir -p voices/xtts
```
Lege eine saubere WAV-Aufnahme von 10–20 Sekunden in `voices/xtts/` (z. B. `voices/xtts/leyla.wav`). Die Stimme
erscheint in den Einstellungen und spricht Deutsch, Türkisch und Englisch.
⚠ Nimm nur deine eigene Stimme oder eine, für die du die Erlaubnis hast. XTTS ist nur für privaten Gebrauch lizenziert.

## Geschwindigkeit
„Antwort in Sekunden“ hängt von deinem Rechner ab. Typisch auf einem M-Mac mit `qwen2.5:7b`: erstes Wort nach
0,3–1 s, 30–50 Wörter/s. Die Prozess-Anzeige zeigt dir die echten Zeiten. Schneller geht es mit
`LLM_MODEL=qwen2.5:3b`, klüger (aber langsamer) mit `qwen2.5:14b`. `KEEP_ALIVE=30m` hält das Modell im Speicher.

## Versionsverwaltung (GitHub)
`install.sh` legt ein lokales Git-Repository an. Auf GitHub sichern (privat!):
```bash
gh repo create jarvis --private --source=. --push
```

## Beispiele
- „Ab jetzt nennst du mich Chef und sprichst nur Deutsch mit mir.“
- „Ich arbeite an einer App namens Nova. Heute haben wir den Login auf Dark Mode umgestellt.“ → am nächsten Tag: „Was haben wir gestern an Nova geändert?“
- „Plane mir einen Launch für Nova in 4 Wochen und zeig den Plan als Fenster.“
- „Recherchiere die besten Wege, mit einer Fitness-App Geld zu verdienen, und speichere es.“
- „Öffne Visual Studio Code.“ · „Schau auf meinen Bildschirm: Was ist das für ein Fehler?“
- „Bau mir ein 30-Sekunden-Video über Istanbul bei Nacht.“
- „Erinnere mich morgen um 9 an den Zahnarzt.“ · „Jeden Werktag um 8: fasse meine Mails zusammen.“
- „Zeig mir Tokio auf der Weltkarte.“ · „Jarvis, Selbstdiagnose.“

## Probleme?
- **❌ in der Selbstdiagnose** → dort steht jeweils die Lösung (z. B. `ollama pull nomic-embed-text`)
- **„GEDÄCHTNIS … ohne SEM“** → Embedding-Modell fehlt, dann läuft die Stichwortsuche. Nach dem Installieren: Tab 🩺 → „Gedächtnis neu indexieren“
- **Mikrofon geht am Handy nicht** → Seite muss über **https** laufen
- **Bildschirm/Klicken geht nicht** → Mac-Berechtigungen (siehe Installation)
JARVIS_EOF
mkdir -p 'backend'
cat > 'backend/.env.example' <<'JARVIS_EOF'
# ================= J.A.R.V.I.S. Konfiguration =================
# Kopie liegt in backend/.env (install.sh macht das). Nach Änderungen: Jarvis neu starten.

PORT=8443
TIMEZONE=Europe/Berlin

# ---- Gehirn (lokal über Ollama) ----
LLM_MODEL=qwen2.5:7b
VISION_MODEL=qwen2.5vl:7b
EMBED_MODEL=nomic-embed-text
# Schnelleres Modell nur fürs Lernen/Zusammenfassen (leer = LLM_MODEL), z.B. qwen2.5:3b
FAST_MODEL=
# Mit 32 GB RAM besser: LLM_MODEL=qwen2.5:14b
KEEP_ALIVE=30m

# ---- Gedächtnis ----
AUTO_LEARN=true
DAILY_SUMMARY_TIME=23:45

# ---- Spracherkennung (Whisper): tiny | base | small | medium | large-v3
WHISPER_MODEL=small

# ---- Sicherheit: nur diese Netze dürfen zugreifen (eigener Rechner, Heim-WLAN, Tailscale)
ALLOWED_NETWORKS=127.0.0.0/8,::1/128,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,fd00::/8
TOKEN_HOURS=72

# ---- Computer-Steuerung ----
COMPUTER_CONTROL=true
# false = Tippen, Klicken, Befehle, Dateien schreiben nur nach Bestätigung mit Vorschau (empfohlen!)
AUTO_APPROVE=false
# Jarvis darf nur Dateien unterhalb dieses Ordners lesen/schreiben
FILE_ROOT=~

# ---- Websuche (eigene SearXNG im Docker) ----
SEARXNG_URL=http://127.0.0.1:8888

# ---- Kalender: optional privater ICS-Link (Google Kalender → Einstellungen → "Privatadresse im iCal-Format")
CALENDAR_ICS_URL=

# ---- E-Mail (Gmail: App-Passwort unter myaccount.google.com/apppasswords)
IMAP_HOST=imap.gmail.com
IMAP_USER=
IMAP_PASSWORD=
# Gmail auf Deutsch heißt der Ordner oft "[Gmail]/Entw&APw-rfe"
IMAP_DRAFTS_FOLDER=[Gmail]/Drafts

# ---- Spotify (developer.spotify.com → App, Redirect-URI eintragen) ----
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
SPOTIFY_REDIRECT=http://127.0.0.1:8765/callback

# ---- Telegram (@BotFather → Token; deine Chat-ID über @userinfobot) ----
TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=

# ---- Bilder erstellen (erst requirements-extra.txt installieren) ----
IMAGE_GEN=false
IMAGE_MODEL=stabilityai/sdxl-turbo

# ---- Morgenbriefing ----
BRIEFING_TIME=07:00
BRIEFING_NEWS_QUERY=Nachrichten Deutschland heute
# Wetter fragt open-meteo.com (nur der Stadtname geht raus). Standard: aus.
ALLOW_WEATHER=false
BRIEFING_CITY=Berlin
JARVIS_EOF
mkdir -p 'backend/agents'
cat > 'backend/agents/__init__.py' <<'JARVIS_EOF'

JARVIS_EOF
mkdir -p 'backend/agents'
cat > 'backend/agents/computer_agent.py' <<'JARVIS_EOF'
"""COMPUTER AGENT: Apps öffnen, Bildschirm sehen (Computer Vision), tippen, klicken, Befehle, Dateien.
Alles Riskante läuft nur nach deiner Bestätigung mit Vorschau (confirm=True)."""
import base64
import platform
import subprocess
import uuid
from pathlib import Path

from core import llm
from core.config import settings
from core.tools import tool

MAC = platform.system() == "Darwin"
BLOCKED = (".ssh", ".gnupg", "Library/Keychains", ".env", "secret.key", ".aws", "Passwords")
on = lambda: settings.COMPUTER_CONTROL  # noqa: E731


def safe_path(p: str) -> Path:
    path = (settings.FILE_ROOT / Path(p).expanduser()).resolve() if not p.startswith("/") else Path(p).expanduser().resolve()
    if not str(path).startswith(str(settings.FILE_ROOT.resolve())):
        raise PermissionError(f"Nur Dateien unter {settings.FILE_ROOT} erlaubt.")
    if any(b in str(path) for b in BLOCKED):
        raise PermissionError("Dieser Pfad ist aus Sicherheitsgründen gesperrt.")
    return path


@tool("open_app", "Öffnet ein Programm auf dem Computer (z.B. Safari, Spotify, Visual Studio Code, Notes).",
      {"name": {"type": "string"}}, ["name"], enabled=on, label="App öffnen", agent="computer")
def open_app(user, name):
    cmd = ["open", "-a", name] if MAC else ["xdg-open", name] if platform.system() == "Linux" else ["cmd", "/c", "start", "", name]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return f"{name} geöffnet." if r.returncode == 0 else f"Konnte {name} nicht öffnen: {r.stderr.strip()}"


@tool("open_url", "Öffnet eine Webseite im normalen Browser des Nutzers.", {"url": {"type": "string"}}, ["url"],
      enabled=on, label="Link öffnen", agent="computer")
def open_url(user, url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    import webbrowser
    webbrowser.open(url)
    return f"{url} geöffnet."


def take_screenshot() -> Path:
    path = settings.FILES_DIR / f"{uuid.uuid4().hex}.png"
    if MAC:
        subprocess.run(["screencapture", "-x", str(path)], check=True, timeout=15)
    else:
        import pyautogui
        pyautogui.screenshot(str(path))
    return path


@tool("look_at_screen", "Macht einen Screenshot und analysiert ihn mit Computer Vision (was ist offen, Texte, Fehler, "
      "Positionen von Knöpfen).", {"question": {"type": "string"}}, ["question"], enabled=on,
      label="Bildschirm ansehen", agent="computer")
def look_at_screen(user, question):
    path = take_screenshot()
    from PIL import Image
    img = Image.open(path)
    w, h = img.size
    img.thumbnail((1600, 1600))
    small = path.with_suffix(".jpg")
    img.convert("RGB").save(small, quality=80)
    answer = llm.complete([{"role": "user", "content": f"Bildschirmfoto ({w}x{h} Pixel, verkleinert auf {img.size[0]}x{img.size[1]}). "
                            f"Wenn nach Positionen gefragt wird, gib Koordinaten im Originalmaßstab an. Frage: {question}",
                            "images": [base64.b64encode(small.read_bytes()).decode()]}], settings.VISION_MODEL)
    path.unlink(missing_ok=True)
    return {"result": answer, "attach": f"![Bildschirm](/api/files/{small.name})",
            "ui": {"widget": "image", "title": "👁 Bildschirm-Analyse", "src": f"/api/files/{small.name}", "text": answer}}


@tool("type_text", "Tippt Text in das aktuell aktive Fenster.", {"text": {"type": "string"}}, ["text"],
      enabled=on, confirm=True, label="Tippen", agent="computer", preview=lambda text: f"Tippt:\n{text}")
def type_text(user, text):
    import pyautogui
    pyautogui.write(text, interval=0.01) if text.isascii() else _paste(text)
    return "Getippt."


def _paste(text):
    import pyautogui
    subprocess.run(["pbcopy"] if MAC else ["xclip", "-selection", "clipboard"], input=text, text=True)
    pyautogui.hotkey("command" if MAC else "ctrl", "v")


@tool("press_keys", "Drückt eine Tastenkombination, z.B. 'command+s', 'enter', 'command+tab'.",
      {"keys": {"type": "string"}}, ["keys"], enabled=on, confirm=True, label="Tasten", agent="computer")
def press_keys(user, keys):
    import pyautogui
    parts = [k.strip().lower() for k in keys.split("+")]
    pyautogui.hotkey(*parts) if len(parts) > 1 else pyautogui.press(parts[0])
    return f"{keys} gedrückt."


@tool("click", "Klickt an eine Bildschirmposition (Koordinaten aus look_at_screen).",
      {"x": {"type": "integer"}, "y": {"type": "integer"}, "double": {"type": "boolean"}}, ["x", "y"],
      enabled=on, confirm=True, label="Klicken", agent="computer")
def click(user, x, y, double=False):
    import pyautogui
    pyautogui.doubleClick(x, y) if double else pyautogui.click(x, y)
    return f"Geklickt bei ({x}, {y})."


@tool("run_command", "Führt einen Terminal-Befehl aus (z.B. git status, python skript.py). Nur nach Bestätigung.",
      {"command": {"type": "string"}, "cwd": {"type": "string"}}, ["command"], enabled=on, confirm=True,
      label="Befehl", agent="computer", preview=lambda command, cwd=None: f"$ {command}\n(in {cwd or '~'})")
def run_command(user, command, cwd=None):
    wd = safe_path(cwd) if cwd else settings.FILE_ROOT
    r = subprocess.run(command, shell=True, cwd=wd, capture_output=True, text=True, timeout=120)
    out = (r.stdout + ("\n" + r.stderr if r.stderr else "")).strip()[-6000:]
    return {"result": f"Exit {r.returncode}\n{out}", "ui": {"widget": "info", "kind": "code", "title": f"$ {command}", "text": out or "(keine Ausgabe)"}}


@tool("list_files", "Listet Dateien in einem Ordner auf.", {"path": {"type": "string"}}, ["path"], enabled=on,
      label="Dateien", agent="dateien")
def list_files(user, path):
    p = safe_path(path)
    items = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))[:200]
    return "\n".join(("📁 " if i.is_dir() else "📄 ") + i.name for i in items if not i.name.startswith("."))


@tool("read_file", "Liest eine Textdatei, Code oder PDF.", {"path": {"type": "string"}}, ["path"], enabled=on,
      label="Datei lesen", agent="dateien")
def read_file(user, path):
    p = safe_path(path)
    if p.suffix.lower() == ".pdf":
        from pypdf import PdfReader
        return "\n".join(pg.extract_text() or "" for pg in PdfReader(p).pages)[:12000]
    return p.read_text(errors="ignore")[:12000]


@tool("write_file", "Schreibt/erstellt eine Datei (z.B. Code, Notizen). Nur nach Bestätigung.",
      {"path": {"type": "string"}, "content": {"type": "string"}}, ["path", "content"], enabled=on, confirm=True,
      label="Datei schreiben", agent="dateien",
      preview=lambda path, content: f"Datei: {path}\n{'─' * 30}\n{content[:3000]}")
def write_file(user, path, content):
    p = safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        p.with_suffix(p.suffix + ".bak").write_text(p.read_text(errors="ignore"))
    p.write_text(content)
    return f"Gespeichert: {p}" + (" (Backup .bak angelegt)" if p.with_suffix(p.suffix + ".bak").exists() else "")
JARVIS_EOF
mkdir -p 'backend/agents'
cat > 'backend/agents/media_agent.py' <<'JARVIS_EOF'
"""MEDIA AGENT: Bilder erstellen (lokal, SDXL-Turbo) und Videos bauen (Bilder + Stimme + ffmpeg)."""
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from core import db
from core.config import settings
from core.tools import tool
from engines import voice

_pipe = None


def _load_pipe():
    global _pipe
    if _pipe is None:
        import torch
        from diffusers import AutoPipelineForText2Image
        if torch.cuda.is_available():
            device, dtype = "cuda", torch.float16
        elif torch.backends.mps.is_available():
            device, dtype = "mps", torch.float32
        else:
            device, dtype = "cpu", torch.float32
        _pipe = AutoPipelineForText2Image.from_pretrained(settings.IMAGE_MODEL, torch_dtype=dtype).to(device)
    return _pipe


def make_image(prompt, path, size=(1024, 576)):
    if settings.IMAGE_GEN:
        img = _load_pipe()(prompt=prompt, num_inference_steps=settings.IMAGE_STEPS, guidance_scale=0.0,
                           width=size[0], height=size[1]).images[0]
        img.save(path)
    else:  # Ohne Bild-KI: stilvolle Titelkarte im Jarvis-Look
        from PIL import Image, ImageDraw
        img = Image.new("RGB", size, (2, 8, 16))
        d = ImageDraw.Draw(img)
        cx, cy = size[0] // 2, size[1] // 2
        for r, w in ((230, 2), (180, 6), (130, 2)):
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(63, 216, 255), width=w)
        words, lines, line = prompt.split(), [], ""
        for wd in words:
            if len(line + wd) > 38:
                lines.append(line)
                line = ""
            line += wd + " "
        lines.append(line)
        for i, ln in enumerate(lines[:5]):
            d.text((cx, cy - 40 + i * 22), ln.strip(), fill=(214, 245, 255), anchor="mm")
        img.save(path)


@tool("generate_image", "Erstellt ein Bild aus einer Beschreibung (lokal). Prompt am besten auf Englisch.",
      {"prompt": {"type": "string"}}, ["prompt"], enabled=lambda: settings.IMAGE_GEN, label="Bild erstellen", agent="medien")
def generate_image(user, prompt):
    name = f"{uuid.uuid4().hex}.png"
    make_image(prompt, settings.FILES_DIR / name, (1024, 1024))
    return {"result": "Bild erstellt und angezeigt.", "attach": f"![{prompt}](/api/files/{name})",
            "ui": {"widget": "image", "title": "🎨 Bild", "src": f"/api/files/{name}", "text": prompt}}


@tool("create_video", "Baut ein Video: pro Szene ein Bild + gesprochener Text (Jarvis-Stimme) mit Kamerafahrt. "
      "Gut für Erklärvideos, Social-Media-Clips, Präsentationen.",
      {"title": {"type": "string"},
       "scenes": {"type": "array", "items": {"type": "object", "properties": {
           "narration": {"type": "string", "description": "gesprochener Text der Szene"},
           "image_prompt": {"type": "string", "description": "Bildbeschreibung auf Englisch"}}}}},
      ["title", "scenes"], enabled=lambda: bool(shutil.which("ffmpeg")), label="Video bauen", agent="medien")
def create_video(user, title, scenes):
    if not scenes:
        return "Keine Szenen angegeben."
    prefs = db.all_settings(user["id"])
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        parts = []
        for i, sc in enumerate(scenes[:12]):
            img, wav, mp4 = tmp / f"{i}.png", tmp / f"{i}.wav", tmp / f"{i}.mp4"
            make_image(sc.get("image_prompt") or sc.get("narration", title), img)
            text = sc.get("narration") or " "
            voice.synthesize_to_file(text, voice.pick_voice(text, prefs), wav)
            subprocess.run([
                "ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(img), "-i", str(wav),
                "-vf", "scale=1920:1080,zoompan=z='min(zoom+0.0007,1.12)':d=1:s=1280x720:fps=30,format=yuv420p",
                "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-shortest", str(mp4)], check=True, timeout=600)
            parts.append(mp4)
        lst = tmp / "list.txt"
        lst.write_text("".join(f"file '{p}'\n" for p in parts))
        name = f"{uuid.uuid4().hex}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-c", "copy", str(settings.FILES_DIR / name)], check=True, timeout=600)
    return {"result": f"Video „{title}“ mit {len(parts)} Szenen erstellt.", "attach": f"![video](/api/files/{name})",
            "ui": {"widget": "video", "title": f"🎬 {title}", "src": f"/api/files/{name}"}}
JARVIS_EOF
mkdir -p 'backend/agents'
cat > 'backend/agents/memory_agent.py' <<'JARVIS_EOF'
"""Gedächtnis-Werkzeuge: damit Jarvis selbst speichern, suchen, verknüpfen und vergessen kann."""
import json

from core.tools import tool
from engines import memory

KIND_ENUM = list(memory.KINDS)


@tool("remember", "Speichert dauerhaft eine Information. kind: profile (persönlich), preference (Vorliebe), rule "
      "(dauerhafte Anweisung an Jarvis), goal, project, fact.",
      {"text": {"type": "string", "description": "eigenständiger Satz, z.B. 'Nutzer trinkt Kaffee ohne Zucker'"},
       "kind": {"type": "string", "enum": KIND_ENUM},
       "importance": {"type": "integer", "description": "1-5"}}, ["text"], label="Speichern", agent="memory")
def remember(user, text, kind="fact", importance=3):
    mid = memory.add(user["id"], text, kind, importance, "explizit")
    return {"result": f"Gespeichert (#{mid}, {memory.KINDS.get(kind, kind)}): {text}",
            "ui": {"widget": "memory", "action": "saved", "kind": kind, "text": text}}


@tool("recall", "Durchsucht das Langzeitgedächtnis semantisch (inkl. verknüpfter Erinnerungen).",
      {"query": {"type": "string"}, "kind": {"type": "string", "enum": KIND_ENUM}}, ["query"],
      label="Erinnern", agent="memory")
def recall(user, query, kind=None):
    hits = memory.search(user["id"], query, k=10, kinds=[kind] if kind else None)
    if not hits:
        core = [m for k in ("profile", "goal", "project", "preference", "rule") for m in memory.by_kind(user["id"], k, 10)]
        if not core:
            return "Dazu habe ich nichts gespeichert."
        return "Keine direkten Treffer. Bekannt ist:\n" + "\n".join(f"[#{m['id']} {memory.KINDS[m['kind']]}] {m['text']}" for m in core)
    return "\n".join(f"[#{h['mid']} {memory.KINDS.get(h['kind'])}{' ↔' if h.get('linked') else ''} {h['score']}] {h['text']}"
                     for h in hits)


@tool("update_memory", "Korrigiert eine gespeicherte Erinnerung (ID von recall).",
      {"memory_id": {"type": "integer"}, "text": {"type": "string"}, "kind": {"type": "string", "enum": KIND_ENUM}},
      ["memory_id", "text"], label="Korrigieren", agent="memory")
def update_memory(user, memory_id, text, kind=None):
    return "Aktualisiert." if memory.update(user["id"], int(memory_id), text, kind) else "Nicht gefunden."


@tool("forget", "Löscht eine Erinnerung per ID.", {"memory_id": {"type": "integer"}}, ["memory_id"],
      label="Vergessen", agent="memory")
def forget(user, memory_id):
    memory.delete(user["id"], int(memory_id))
    return "Gelöscht."


@tool("search_conversations", "Durchsucht frühere Gespräche. Für Fragen wie 'Was haben wir gestern am Projekt X geändert?'. "
      "date_from/date_to: 'heute', 'gestern', 'vorgestern' oder YYYY-MM-DD.",
      {"query": {"type": "string"}, "date_from": {"type": "string"}, "date_to": {"type": "string"}}, ["query"],
      label="Gespräche durchsuchen", agent="memory")
def search_conversations(user, query, date_from=None, date_to=None):
    res = memory.search_conversations(user["id"], query, date_from, date_to)
    if not res["messages"] and not res["day_summaries"]:
        return "Keine passenden früheren Gespräche gefunden."
    return json.dumps(res, ensure_ascii=False)[:9000]


@tool("search_knowledge", "Durchsucht die persönliche Wissensdatenbank (hochgeladene Dateien, gespeicherte Webseiten).",
      {"query": {"type": "string"}}, ["query"], label="Wissen", agent="memory")
def search_knowledge(user, query):
    hits = memory.search_knowledge(user["id"], query, 6)
    return "\n\n".join(f"[{h['doc']}] {h['text']}" for h in hits) or "Nichts in der Wissensdatenbank."


@tool("summarize_day", "Erstellt Zusammenfassungen der Gespräche eines Tages (heute/gestern/YYYY-MM-DD).",
      {"day": {"type": "string"}}, label="Tag zusammenfassen", agent="memory")
def summarize_day(user, day="heute"):
    memory.summarize_day(user["id"], memory.resolve_day(day))
    return "Zusammenfassung gespeichert."
JARVIS_EOF
mkdir -p 'backend/agents'
cat > 'backend/agents/scheduler.py' <<'JARVIS_EOF'
"""Hintergrund-Uhrwerk: Morgenbriefing, Erinnerungen, Automatisierungen, nächtliche Gesprächszusammenfassung."""
import asyncio
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from core import db, llm
from core.config import settings
from engines import memory
from agents import services

TZ = ZoneInfo(settings.TIMEZONE)
LANG_HINT = {"de": "auf Deutsch", "tr": "auf Türkisch (Türkçe)", "en": "auf Englisch"}


def users():
    return db.all("SELECT id, username, token_version FROM users")


# ------------------------------------------------------------------ Morgenbriefing
def build_briefing(user) -> dict:
    now = datetime.now(TZ)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    parts = [f"Datum: {now:%A, %d.%m.%Y}"]
    evs = services.events_between(user["id"], start, start + timedelta(days=1))
    parts.append("Termine heute:\n" + ("\n".join(f"- {e['start']:%H:%M} {e['title']}" for e in evs) or "- keine"))
    rem = db.all("SELECT text, due FROM reminders WHERE user_id=? AND done=0 AND due<?", (user["id"], (start + timedelta(days=1)).timestamp()))
    if rem:
        parts.append("Erinnerungen heute:\n" + "\n".join(f"- {datetime.fromtimestamp(r['due'], TZ):%H:%M} {r['text']}" for r in rem))
    if services.mail_on():
        try:
            mails = services.fetch_emails(limit=15)
            parts.append("Ungelesene E-Mails:\n" + ("\n".join(f"- {m['from']}: {m['subject']} – {m['text'][:200]}" for m in mails) or "- keine"))
        except Exception as e:  # noqa: BLE001
            parts.append(f"E-Mails: nicht abrufbar ({e})")
    if settings.ALLOW_WEATHER:
        try:
            parts.append("Wetter: " + services.weather_text(settings.BRIEFING_CITY))
        except Exception:  # noqa: BLE001
            pass
    if settings.BRIEFING_NEWS_QUERY:
        try:
            from agents.web_agent import search
            parts.append("Schlagzeilen:\n" + "\n".join(f"- {r.get('title')}" for r in search(settings.BRIEFING_NEWS_QUERY, news=True)))
        except Exception:  # noqa: BLE001
            pass
    goals = memory.by_kind(user["id"], "goal", 5) + memory.by_kind(user["id"], "project", 5)
    if goals:
        parts.append("Ziele & Projekte des Nutzers:\n" + "\n".join(f"- {g['text']}" for g in goals))
    lang = db.get_setting(user["id"], "language", "de")
    anrede = db.get_setting(user["id"], "anrede", "")
    prompt = (f"Erstelle {LANG_HINT.get(lang, 'auf Deutsch')} ein persönliches Morgenbriefing als J.A.R.V.I.S. "
              f"{'für ' + anrede if anrede else ''} (gesprochen, max. 170 Wörter, mit Begrüßung). Wichtigstes zuerst, "
              f"Mails zusammengefasst, und ein konkreter Vorschlag für heute passend zu den Zielen.\n\nDaten:\n" + "\n\n".join(parts))
    text = llm.complete([{"role": "user", "content": prompt}])
    chat_id = db.find_or_create_chat(user["id"], f"☀ Morgenbriefing {now:%d.%m.%Y}")
    db.add_message(chat_id, "assistant", text)
    nid = db.notify(user["id"], text, "briefing", chat_id)
    if services.tg_on():
        try:
            services.telegram_send("☀ " + text)
        except Exception:  # noqa: BLE001
            pass
    return {"id": nid, "chat_id": chat_id, "content": text}


# ------------------------------------------------------------------ Minütlicher Takt
def tick():
    now = datetime.now(TZ)
    for r in db.all("SELECT * FROM reminders WHERE done=0 AND due<=?", (time.time(),)):
        db.run("UPDATE reminders SET done=1 WHERE id=?", (r["id"],))
        db.notify(r["user_id"], f"⏰ Erinnerung: {r['text']}", "reminder")
        if services.tg_on():
            try:
                services.telegram_send(f"⏰ {r['text']}")
            except Exception:  # noqa: BLE001
                pass
    hhmm, wd, today = now.strftime("%H:%M"), str(now.weekday()), now.date().isoformat()
    for a in db.all("SELECT * FROM automations WHERE enabled=1 AND hhmm=? AND (last_run IS NULL OR last_run<>?)", (hhmm, today)):
        if wd not in (a["weekdays"] or "0123456"):
            continue
        db.run("UPDATE automations SET last_run=? WHERE id=?", (today, a["id"]))
        user = db.one("SELECT id, username, token_version FROM users WHERE id=?", (a["user_id"],))
        try:
            from agents import task_agent
            cid = db.find_or_create_chat(user["id"], "⚙ Automatisierungen")
            answer = asyncio.run(task_agent.run_collect(user, cid, f"[Automatisierung #{a['id']}] {a['prompt']}"))
            db.notify(user["id"], f"⚙ {a['prompt'][:60]}: {answer[:400]}", "automation", cid)
        except Exception as e:  # noqa: BLE001
            db.notify(a["user_id"], f"⚙ Automatisierung #{a['id']} fehlgeschlagen: {e}", "error")


def nightly():
    for u in users():
        try:
            memory.summarize_day(u["id"])
        except Exception as e:  # noqa: BLE001
            print(f"[Gedächtnis] Tageszusammenfassung fehlgeschlagen: {e}")


def morning():
    for u in users():
        try:
            build_briefing(u)
        except Exception as e:  # noqa: BLE001
            print(f"[Briefing] {e}")


def start():
    from apscheduler.schedulers.background import BackgroundScheduler
    s = BackgroundScheduler(timezone=settings.TIMEZONE)
    bh, bm = (int(x) for x in settings.BRIEFING_TIME.split(":"))
    nh, nm = (int(x) for x in settings.DAILY_SUMMARY_TIME.split(":"))
    s.add_job(morning, "cron", hour=bh, minute=bm, id="briefing")
    s.add_job(nightly, "cron", hour=nh, minute=nm, id="summary")
    s.add_job(tick, "interval", seconds=30, id="tick", max_instances=1)
    s.start()
    return s
JARVIS_EOF
mkdir -p 'backend/agents'
cat > 'backend/agents/security.py' <<'JARVIS_EOF'
"""SECURITY AGENT: Benutzerauthentifizierung, Netzwerk-Schutz, Sperren, Sicherheitsprotokoll.

- Nur EIN Besitzer-Konto (create_user.py verweigert weitere Konten)
- Passwörter als bcrypt-Hash, Token (JWT) mit Ablaufzeit, ungültig nach Passwortänderung
- 5 Fehlversuche -> 15 Minuten Sperre
- Zugriff nur aus deinem eigenen Netz (Rechner, Heim-WLAN, Tailscale), Internet-IPs werden abgewiesen
"""
import ipaddress
import time
from collections import defaultdict

import bcrypt
import jwt
from fastapi import HTTPException, Request

from core import db
from core.config import settings

_fails: dict[str, list[float]] = defaultdict(list)
MAX_FAILS, LOCK_SECONDS = 5, 15 * 60
NETWORKS = [ipaddress.ip_network(n.strip()) for n in settings.ALLOWED_NETWORKS.split(",") if n.strip()]


def hash_pw(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt(12)).decode()


def check_pw(pw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    except ValueError:
        return False


def ip_allowed(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    if getattr(addr, "ipv4_mapped", None):
        addr = addr.ipv4_mapped
    return any(addr in n for n in NETWORKS if n.version == addr.version)


def login_allowed(ip: str) -> bool:
    now = time.time()
    _fails[ip] = [t for t in _fails[ip] if now - t < LOCK_SECONDS]
    return len(_fails[ip]) < MAX_FAILS


def note_fail(ip: str, username: str):
    _fails[ip].append(time.time())
    db.log_security(ip, "login_fehlgeschlagen", f"Benutzer: {username[:40]}")
    if len(_fails[ip]) >= MAX_FAILS:
        db.log_security(ip, "gesperrt", "zu viele Fehlversuche")


def make_token(user) -> str:
    payload = {"sub": str(user["id"]), "v": user.get("token_version", 0),
               "exp": int(time.time()) + settings.TOKEN_HOURS * 3600}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def user_from_token(token: str):
    try:
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    u = db.one("SELECT id, username, token_version FROM users WHERE id=?", (int(data["sub"]),))
    return u if u and u["token_version"] == data.get("v", 0) else None


def current_user(request: Request):
    header = request.headers.get("authorization", "")
    token = header[7:].strip() if header.lower().startswith("bearer ") else request.query_params.get("token", "")
    user = user_from_token(token) if token else None
    if not user:
        raise HTTPException(status_code=401, detail="Nicht angemeldet")
    return user


def change_password(user_id, new_pw):
    db.run("UPDATE users SET pw_hash=?, token_version=token_version+1 WHERE id=?", (hash_pw(new_pw), user_id))
    db.log_security("-", "passwort_geändert", f"user {user_id}")
JARVIS_EOF
mkdir -p 'backend/agents'
cat > 'backend/agents/services.py' <<'JARVIS_EOF'
"""Dienste: Zeit, Kalender, Erinnerungen, Automatisierungen, E-Mail, Spotify, Telegram, Wetter, Karte, Info-Fenster."""
import email
import imaplib
import re
import time
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.policy import default as default_policy
from zoneinfo import ZoneInfo

import httpx

from core import db
from core.config import settings
from core.tools import tool

TZ = ZoneInfo(settings.TIMEZONE)


def now():
    return datetime.now(TZ)


def parse_dt(s: str) -> datetime:
    s = s.strip().replace("Z", "+00:00")
    for fmt in (None, "%d.%m.%Y %H:%M", "%d.%m.%Y", "%Y-%m-%d %H:%M"):
        try:
            dt = datetime.fromisoformat(s) if fmt is None else datetime.strptime(s, fmt)
            return dt if dt.tzinfo else dt.replace(tzinfo=TZ)
        except ValueError:
            continue
    raise ValueError(f"Unbekanntes Datumsformat: {s} (nutze YYYY-MM-DDTHH:MM)")


@tool("get_time", "Aktuelles Datum und Uhrzeit.", label="Uhrzeit")
def get_time(user):
    return now().strftime("%A, %d.%m.%Y %H:%M Uhr (%Z)")


# ------------------------------------------------------------------ Kalender
@tool("add_event", "Trägt einen Termin in den Kalender ein.",
      {"title": {"type": "string"}, "start": {"type": "string", "description": "ISO, z.B. 2026-11-05T14:00"},
       "end": {"type": "string"}, "location": {"type": "string"}, "notes": {"type": "string"}},
      ["title", "start"], label="Termin eintragen", agent="kalender")
def add_event(user, title, start, end=None, location="", notes=""):
    s = parse_dt(start)
    e = parse_dt(end) if end else s + timedelta(hours=1)
    db.run("INSERT INTO events(user_id,title,start,end,location,notes) VALUES(?,?,?,?,?,?)",
           (user["id"], title, s.isoformat(), e.isoformat(), location, notes))
    return {"result": f"Termin '{title}' am {s:%d.%m.%Y um %H:%M} eingetragen.",
            "ui": {"widget": "info", "title": "📅 Termin", "text": f"{s:%a %d.%m. %H:%M} – {title}"}}


@tool("delete_event", "Löscht einen Termin per ID.", {"event_id": {"type": "integer"}}, ["event_id"],
      confirm=True, label="Termin löschen", agent="kalender")
def delete_event(user, event_id):
    db.run("DELETE FROM events WHERE id=? AND user_id=?", (int(event_id), user["id"]))
    return "Termin gelöscht."


def events_between(user_id, start, end):
    out = []
    for r in db.all("SELECT * FROM events WHERE user_id=?", (user_id,)):
        s = datetime.fromisoformat(r["start"])
        if start <= s < end:
            out.append({"id": r["id"], "title": r["title"], "start": s, "location": r["location"] or "", "source": "lokal"})
    if settings.CALENDAR_ICS_URL:
        try:
            import icalendar
            import recurring_ical_events
            cal = icalendar.Calendar.from_ical(httpx.get(settings.CALENDAR_ICS_URL, timeout=20).content)
            for ev in recurring_ical_events.of(cal).between(start, end):
                s = ev.get("DTSTART").dt
                s = datetime(s.year, s.month, s.day, tzinfo=TZ) if not isinstance(s, datetime) else (
                    s if s.tzinfo else s.replace(tzinfo=TZ))
                out.append({"id": None, "title": str(ev.get("SUMMARY", "")), "start": s.astimezone(TZ),
                            "location": str(ev.get("LOCATION", "") or ""), "source": "ics"})
        except Exception as e:  # noqa: BLE001
            out.append({"id": None, "title": f"(ICS nicht lesbar: {e})", "start": start, "location": "", "source": "ics"})
    return sorted(out, key=lambda x: x["start"])


@tool("list_events", "Zeigt Termine (heute bzw. die nächsten Tage).",
      {"days": {"type": "integer"}, "start_date": {"type": "string", "description": "YYYY-MM-DD"}},
      label="Termine", agent="kalender")
def list_events(user, days=1, start_date=None):
    start = (parse_dt(start_date) if start_date else now()).replace(hour=0, minute=0, second=0, microsecond=0)
    evs = events_between(user["id"], start, start + timedelta(days=int(days or 1)))
    return "\n".join(f"- [{e['id'] or 'ics'}] {e['start']:%a %d.%m. %H:%M} {e['title']}"
                     + (f" @ {e['location']}" if e["location"] else "") for e in evs) or "Keine Termine."


# ------------------------------------------------------------------ Erinnerungssystem & Automatisierung
@tool("set_reminder", "Erinnert den Nutzer zu einem Zeitpunkt (Benachrichtigung in der App + Telegram).",
      {"text": {"type": "string"}, "when": {"type": "string", "description": "ISO-Zeit, z.B. 2026-11-05T09:30"}},
      ["text", "when"], label="Erinnerung", agent="erinnerung")
def set_reminder(user, text, when):
    due = parse_dt(when)
    db.run("INSERT INTO reminders(user_id,text,due) VALUES(?,?,?)", (user["id"], text, due.timestamp()))
    return f"Ich erinnere dich am {due:%d.%m. um %H:%M}: {text}"


@tool("create_automation", "Legt eine wiederkehrende Aufgabe an, die Jarvis selbstständig ausführt "
      "(z.B. täglich 08:00 'Fasse die Tech-News zusammen').",
      {"prompt": {"type": "string", "description": "Auftrag an Jarvis"},
       "time": {"type": "string", "description": "HH:MM"},
       "weekdays": {"type": "string", "description": "0=Mo … 6=So, z.B. '01234' für Werktage"}},
      ["prompt", "time"], confirm=True, label="Automatisierung", agent="automatisierung")
def create_automation(user, prompt, time, weekdays="0123456"):
    if not re.fullmatch(r"\d{1,2}:\d{2}", time):
        return "Zeit bitte als HH:MM."
    aid = db.run("INSERT INTO automations(user_id,prompt,hhmm,weekdays) VALUES(?,?,?,?)",
                 (user["id"], prompt, time.zfill(5), weekdays))
    return f"Automatisierung #{aid} angelegt: täglich {time} – {prompt}"


@tool("list_automations", "Zeigt Automatisierungen und offene Erinnerungen.", label="Automatisierungen", agent="automatisierung")
def list_automations(user):
    a = db.all("SELECT id,prompt,hhmm,weekdays,enabled FROM automations WHERE user_id=?", (user["id"],))
    r = db.all("SELECT id,text,due FROM reminders WHERE user_id=? AND done=0 ORDER BY due", (user["id"],))
    return {"automations": a, "reminders": [{**x, "due": datetime.fromtimestamp(x["due"], TZ).strftime("%d.%m. %H:%M")} for x in r]}


# ------------------------------------------------------------------ E-Mail (IMAP direkt)
def mail_on():
    return bool(settings.IMAP_USER and settings.IMAP_PASSWORD)


def _imap():
    m = imaplib.IMAP4_SSL(settings.IMAP_HOST)
    m.login(settings.IMAP_USER, settings.IMAP_PASSWORD)
    return m


def fetch_emails(limit=10, unread_only=True, folder="INBOX"):
    m = _imap()
    try:
        m.select(folder, readonly=True)
        _, data = m.search(None, "UNSEEN" if unread_only else "ALL")
        mails = []
        for i in reversed(data[0].split()[-int(limit):]):
            _, msg_data = m.fetch(i, "(BODY.PEEK[])")
            msg = email.message_from_bytes(msg_data[0][1], policy=default_policy)
            body = msg.get_body(preferencelist=("plain", "html"))
            text = body.get_content() if body else ""
            if body and body.get_content_type() == "text/html":
                text = re.sub(r"<[^>]+>", " ", text)
            mails.append({"from": str(msg["from"]), "subject": str(msg["subject"]), "date": str(msg["date"]),
                          "text": re.sub(r"\s+", " ", text)[:700]})
        return mails
    finally:
        m.logout()


@tool("read_emails", "Liest E-Mails (Standard: ungelesene). Danach knapp zusammenfassen.",
      {"limit": {"type": "integer"}, "unread_only": {"type": "boolean"}, "folder": {"type": "string"}},
      enabled=mail_on, label="E-Mails lesen", agent="mail")
def read_emails(user, limit=10, unread_only=True, folder="INBOX"):
    return fetch_emails(limit, unread_only, folder) or "Keine (ungelesenen) E-Mails."


@tool("draft_email", "Legt einen E-Mail-ENTWURF an (wird nicht gesendet).",
      {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
      ["to", "subject", "body"], enabled=mail_on, confirm=True, label="Mail-Entwurf", agent="mail",
      preview=lambda to, subject, body: f"An: {to}\nBetreff: {subject}\n\n{body}")
def draft_email(user, to, subject, body):
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = settings.IMAP_USER, to, subject
    msg.set_content(body)
    m = _imap()
    try:
        m.append(f'"{settings.IMAP_DRAFTS_FOLDER}"', r"(\Draft)", imaplib.Time2Internaldate(time.time()), msg.as_bytes())
    finally:
        m.logout()
    return f"Entwurf an {to} gespeichert."


# ------------------------------------------------------------------ Spotify
_sp = None


def spotify_on():
    return bool(settings.SPOTIFY_CLIENT_ID and settings.SPOTIFY_CLIENT_SECRET)


def spotify_client():
    global _sp
    if _sp is None:
        import spotipy
        from spotipy.oauth2 import SpotifyOAuth
        _sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID, client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT, open_browser=True,
            scope="user-read-playback-state user-modify-playback-state user-read-currently-playing",
            cache_path=str(settings.DATA_DIR / ".spotify_cache")))
    return _sp


@tool("spotify_play", "Spielt Musik auf Spotify.", {"query": {"type": "string"},
      "kind": {"type": "string", "enum": ["track", "artist", "playlist", "album"]}}, ["query"],
      enabled=spotify_on, label="Spotify", agent="musik")
def spotify_play(user, query, kind="track"):
    sp = spotify_client()
    items = sp.search(q=query, type=kind, limit=1)[f"{kind}s"]["items"]
    if not items:
        return "Nichts gefunden."
    it = items[0]
    sp.start_playback(uris=[it["uri"]]) if kind == "track" else sp.start_playback(context_uri=it["uri"])
    return f"Spiele {it['name']}."


@tool("spotify_control", "Spotify: pause, resume, next, previous, current, volume.",
      {"action": {"type": "string", "enum": ["pause", "resume", "next", "previous", "current", "volume"]},
       "volume": {"type": "integer"}}, ["action"], enabled=spotify_on, label="Spotify", agent="musik")
def spotify_control(user, action, volume=None):
    sp = spotify_client()
    if action == "current":
        cur = sp.current_playback()
        if not cur or not cur.get("item"):
            return "Gerade läuft nichts."
        return f"{cur['item']['name']} von {', '.join(a['name'] for a in cur['item']['artists'])}"
    {"pause": sp.pause_playback, "resume": sp.start_playback, "next": sp.next_track, "previous": sp.previous_track,
     "volume": lambda: sp.volume(max(0, min(100, int(volume or 50))))}[action]()
    return f"Spotify: {action} ok."


# ------------------------------------------------------------------ Telegram
def tg_on():
    return bool(settings.TELEGRAM_TOKEN and settings.TELEGRAM_CHAT_ID)


def telegram_send(text):
    httpx.post(f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage",
               json={"chat_id": settings.TELEGRAM_CHAT_ID, "text": text[:4000]}, timeout=20)


@tool("send_telegram", "Schickt dem Nutzer selbst eine Nachricht aufs Handy (Telegram).",
      {"text": {"type": "string"}}, ["text"], enabled=tg_on, label="Telegram", agent="telegram")
def send_telegram(user, text):
    telegram_send(text)
    return "Gesendet."


# ------------------------------------------------------------------ Wetter (optional)
def weather_text(city):
    g = httpx.get("https://geocoding-api.open-meteo.com/v1/search", params={"name": city, "count": 1}, timeout=15).json()
    if not g.get("results"):
        return f"Ort {city} nicht gefunden."
    loc = g["results"][0]
    w = httpx.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": loc["latitude"], "longitude": loc["longitude"], "timezone": settings.TIMEZONE,
        "current": "temperature_2m,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max", "forecast_days": 1}, timeout=15).json()
    c, d = w["current"], w["daily"]
    return (f"{loc['name']}: jetzt {c['temperature_2m']}°C, Wind {c['wind_speed_10m']} km/h, heute "
            f"{d['temperature_2m_min'][0]}–{d['temperature_2m_max'][0]}°C, Regen {d['precipitation_probability_max'][0]}%.")


@tool("weather", "Aktuelles Wetter.", {"city": {"type": "string"}}, ["city"],
      enabled=lambda: settings.ALLOW_WEATHER, label="Wetter", agent="web")
def weather(user, city):
    return weather_text(city)


# ------------------------------------------------------------------ Bildschirm-Anzeigen (HUD)
@tool("show_map", "Zeigt einen Ort auf der Weltkugel im Dashboard an. Koordinaten selbst angeben (du kennst sie).",
      {"lat": {"type": "number"}, "lon": {"type": "number"}, "label": {"type": "string"},
       "zoom": {"type": "number", "description": "1 = ganze Welt, 4 = Land, 8 = Stadt"}},
      ["lat", "lon", "label"], label="Weltkarte", agent="anzeige")
def show_map(user, lat, lon, label, zoom=3):
    return {"result": f"Karte zeigt {label}.",
            "ui": {"widget": "map", "lat": float(lat), "lon": float(lon), "label": label, "zoom": float(zoom or 3)}}


@tool("show_info", "Öffnet ein Info-Fenster im Dashboard (Fakten, Tabellen, Schritte, Ergebnisse, Code).",
      {"title": {"type": "string"}, "text": {"type": "string", "description": "Markdown"},
       "kind": {"type": "string", "enum": ["info", "result", "code", "warning"]}}, ["title", "text"],
      label="Info-Fenster", agent="anzeige")
def show_info(user, title, text, kind="info"):
    return {"result": "Fenster geöffnet.", "ui": {"widget": "info", "title": title, "text": text, "kind": kind}}
JARVIS_EOF
mkdir -p 'backend/agents'
cat > 'backend/agents/system_agent.py' <<'JARVIS_EOF'
"""SYSTEM AGENT: Selbstdiagnose – prüft alle Bausteine und meldet Probleme."""
import importlib.util
import shutil
import time

import httpx

from core import db, llm
from core.config import settings
from core.tools import tool
from engines import memory, voice

STARTED = time.time()


def diagnose(user_id=None):
    checks = []

    def add(name, ok, detail=""):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    h = llm.health()
    add("Gehirn (Ollama)", h["ok"], ", ".join(h["models"]) if h["ok"] else h.get("error", ""))
    for label, model in (("Sprachmodell", settings.LLM_MODEL), ("Vision-Modell", settings.VISION_MODEL),
                         ("Embedding-Modell", settings.EMBED_MODEL)):
        present = model in h["models"] or (":" not in model and f"{model}:latest" in h["models"])
        add(f"{label} {model}", present, "" if present else f"fehlt → ollama pull {model}")
    add("ChromaDB (semantisches Gedächtnis)", importlib.util.find_spec("chromadb") is not None and memory._semantic_ok,
        "Stichwort-Fallback aktiv" if not memory._semantic_ok else "")
    try:
        r = httpx.get(f"{settings.SEARXNG_URL}/search", params={"q": "test", "format": "json"}, timeout=5)
        add("Websuche (SearXNG)", r.status_code == 200, f"HTTP {r.status_code}")
    except Exception as e:  # noqa: BLE001
        add("Websuche (SearXNG)", False, f"nicht erreichbar → docker compose up -d ({type(e).__name__})")
    add("Whisper (Spracherkennung)", importlib.util.find_spec("faster_whisper") is not None, settings.WHISPER_MODEL)
    vs = voice.list_voices()
    add("Stimmen (TTS)", importlib.util.find_spec("piper") is not None and len(vs) > 0, f"{len(vs)} Stimmen")
    add("Playwright (Web-Agent)", importlib.util.find_spec("playwright") is not None, "")
    add("ffmpeg (Videos)", shutil.which("ffmpeg") is not None, "" if shutil.which("ffmpeg") else "brew install ffmpeg")
    add("Bild-KI", settings.IMAGE_GEN and importlib.util.find_spec("diffusers") is not None,
        "aus (IMAGE_GEN=false)" if not settings.IMAGE_GEN else "")
    add("Computersteuerung", settings.COMPUTER_CONTROL and importlib.util.find_spec("pyautogui") is not None,
        "Bestätigung nötig" if not settings.AUTO_APPROVE else "⚠ AUTO_APPROVE an")
    du = shutil.disk_usage(settings.DATA_DIR)
    add("Speicherplatz", du.free > 5e9, f"{du.free / 1e9:.0f} GB frei")
    add("Datenbank", True, f"{settings.DB_PATH.stat().st_size / 1e6:.1f} MB")
    errors = db.all("SELECT tool, result, created FROM actions WHERE status='error' ORDER BY id DESC LIMIT 5")
    out = {"checks": checks, "uptime_s": int(time.time() - STARTED), "recent_errors": errors,
           "ok": sum(c["ok"] for c in checks), "total": len(checks)}
    if user_id:
        out["memory"] = memory.stats(user_id)
    return out


@tool("self_diagnose", "Selbstdiagnose: prüft alle Systeme von Jarvis und meldet Probleme mit Lösung.",
      label="Selbstdiagnose", agent="system")
def self_diagnose(user):
    d = diagnose(user["id"])
    txt = "\n".join(f"{'✅' if c['ok'] else '❌'} {c['name']} {c['detail']}" for c in d["checks"])
    return {"result": f"{d['ok']}/{d['total']} Systeme OK\n{txt}",
            "ui": {"widget": "info", "title": f"🩺 Diagnose {d['ok']}/{d['total']}", "text": txt, "kind": "result"}}
JARVIS_EOF
mkdir -p 'backend/agents'
cat > 'backend/agents/task_agent.py' <<'JARVIS_EOF'
"""TASK AGENT – das Herz: Verstehen → Gedächtnis → Planen → Werkzeuge → Antwort → Lernen.

Jeder Schritt wird als Event an die Oberfläche geschickt (Knoten, Prozent, Millisekunden).
"""
import asyncio
import json
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from core import db, llm, tools
from core.config import settings
from core.tools import tool
from engines import memory

LANGS = {"de": "Deutsch", "tr": "Türkisch (Türkçe)", "en": "Englisch"}

PERSONA = """Du bist J.A.R.V.I.S., der persönliche KI-Assistent deines Nutzers. Du läufst komplett lokal und privat auf seinem Rechner.
Charakter: loyal, ruhig, präzise, proaktiv, mit leichtem trockenem Humor. Du kennst deinen Nutzer und nutzt dein Gedächtnis.

ARBEITSWEISE:
1. Verstehe, was der Nutzer wirklich will. Nutze PROFIL, REGELN und ERINNERUNGEN unten.
2. Bei Aufgaben mit mehreren Schritten: rufe ZUERST plan_task auf, dann arbeite die Schritte mit Werkzeugen ab.
3. Nutze Werkzeuge aktiv statt zu raten: aktuelle Infos → web_search/research; frühere Gespräche → search_conversations;
   Orte → show_map; wichtige Ergebnisse/Tabellen/Code → show_info.
4. Selbstkorrektur: Wenn ein Werkzeug einen Fehler liefert, versuche einen anderen Weg. Prüfe dein Ergebnis kurz, bevor du antwortest.
5. Wenn der Nutzer etwas Dauerhaftes über sich sagt oder eine Regel festlegt ("ab jetzt…", "immer…", "nenn mich…"), speichere es mit remember.
6. Aktionen am Computer, Dateien schreiben, Befehle: die Bestätigung holt das System automatisch ein – erkläre kurz, was du vorhast.
7. Antworte kurz und gesprochen-tauglich (wird vorgelesen), außer der Nutzer will Details. Erfinde nie Fakten, Termine oder Mails.
8. Hilf dem Nutzer aktiv bei seinen Zielen und Projekten (auch beim Geldverdienen: Ideen, Pläne, Umsetzung) – realistisch und ehrlich."""


def system_prompt(user, mem_text):
    now = datetime.now(ZoneInfo(settings.TIMEZONE))
    lang = db.get_setting(user["id"], "language", "auto")
    anrede = db.get_setting(user["id"], "anrede") or db.get_setting(user["id"], "name")
    lang_rule = (f"SPRACHE: Antworte IMMER auf {LANGS[lang]}, egal in welcher Sprache der Nutzer schreibt."
                 if lang in LANGS else "SPRACHE: Antworte in der Sprache, in der der Nutzer schreibt (Deutsch, Türkisch oder Englisch).")
    return (f"{PERSONA}\n\n{lang_rule}\n"
            f"ANREDE: {('Sprich den Nutzer als „' + anrede + '“ an.') if anrede else 'Noch unbekannt – frag einmal freundlich, wie du ihn nennen sollst.'}\n"
            f"JETZT: {now:%A, %d.%m.%Y %H:%M} ({settings.TIMEZONE})\n\n"
            f"=== GEDÄCHTNIS ===\n{mem_text or '(noch leer – lerne den Nutzer kennen)'}")


def short_term(chat_id, limit=20):
    """Kurzzeitgedächtnis: die letzten Nachrichten dieses Chats."""
    rows = db.all("SELECT role, content FROM messages WHERE chat_id=? ORDER BY id DESC LIMIT ?", (chat_id, limit))
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


@tool("plan_task", "Zerlegt eine Aufgabe in Einzelschritte (wird im Dashboard als Knoten angezeigt). "
      "Bei jeder mehrstufigen Aufgabe zuerst aufrufen.",
      {"goal": {"type": "string"}, "steps": {"type": "array", "items": {"type": "string"}}}, ["goal", "steps"],
      label="Planen", agent="task")
def plan_task(user, goal, steps):
    return {"result": "Plan steht. Arbeite die Schritte jetzt nacheinander ab.",
            "ui": {"widget": "plan", "goal": goal, "steps": steps}}


async def run(user, chat_id, text, images=None):
    """Async-Generator mit Events: step, plan, token, tool, ui, confirm, learned, done, error."""
    images = images or []
    t_start = time.perf_counter()
    if not text and images:
        text = "Was siehst du auf diesem Bild?"
    chat = db.one("SELECT title FROM chats WHERE id=?", (chat_id,))
    title = chat["title"] if chat else ""
    if title == "Neuer Chat":
        title = text[:48]
        db.run("UPDATE chats SET title=? WHERE id=?", (title, chat_id))
    umid = db.add_message(chat_id, "user", text, has_images=bool(images))
    asyncio.get_running_loop().run_in_executor(None, memory.index_message, user["id"], chat_id, umid, "user", text, title)

    def step(sid, label, status, ms=None, detail=None, kind="core"):
        return {"type": "step", "id": sid, "label": label, "status": status, "ms": ms, "detail": detail, "kind": kind,
                "t": int((time.perf_counter() - t_start) * 1000)}

    yield step("input", "Verstehen", "done", 0, text[:80], "input")

    # ---- Gedächtnis abrufen
    yield step("memory", "Gedächtnis", "active", kind="memory")
    mem_text, mstats = await asyncio.to_thread(memory.build_context, user["id"], text, chat_id)
    yield step("memory", "Gedächtnis", "done", mstats["ms"],
               f"{mstats.get('rule', 0)} Regeln · {sum(mstats.get(k, 0) for k in ('goal', 'project', 'preference', 'profile'))} Profil · "
               f"{mstats.get('relevant', 0)} Erinnerungen · "
               f"{mstats.get('conversations', 0)} Gespräche · {mstats.get('knowledge', 0)} Wissen", "memory")

    msgs = [{"role": "system", "content": system_prompt(user, mem_text)}] + short_term(chat_id)
    if images:
        msgs[-1]["images"] = images
    model = settings.VISION_MODEL if images else settings.LLM_MODEL
    schema = None if images else tools.schemas()

    full, attachments, n_tool = "", [], 0
    try:
        for rnd in range(8):
            sid = f"think{rnd}"
            yield step(sid, "Denken" if rnd == 0 else "Auswerten", "active", kind="llm")
            t0 = time.perf_counter()
            content, calls, first_tok, detail = "", [], None, ""
            async for chunk in llm.stream_chat(msgs, schema, model):
                m = chunk.get("message", {})
                if m.get("content"):
                    if first_tok is None:
                        first_tok = int((time.perf_counter() - t0) * 1000)
                    content += m["content"]
                    yield {"type": "token", "text": m["content"]}
                if m.get("tool_calls"):
                    calls.extend(m["tool_calls"])
                if chunk.get("done") and chunk.get("eval_count"):
                    tps = chunk["eval_count"] / max(chunk.get("eval_duration", 1) / 1e9, 1e-3)
                    detail = f"{tps:.0f} Token/s"
            ms = int((time.perf_counter() - t0) * 1000)
            yield step(sid, "Denken" if rnd == 0 else "Auswerten", "done", ms,
                       detail + (f" · erstes Wort {first_tok} ms" if first_tok else ""), "llm")
            full += content
            if not calls:
                break
            msgs.append({"role": "assistant", "content": content, "tool_calls": calls})
            for c in calls:
                fn = c.get("function", {})
                name, args = fn.get("name"), fn.get("arguments") or {}
                if isinstance(args, str):
                    try:
                        args = json.loads(args or "{}")
                    except json.JSONDecodeError:
                        args = {}
                n_tool += 1
                tsid = f"tool{n_tool}"
                info = tools.info(name) or {}
                label, agent = info.get("label", name), info.get("agent", "?")
                if tools.needs_confirm(name):
                    aid = db.run("INSERT INTO actions(user_id,chat_id,tool,args,status,created) VALUES(?,?,?,?,?,?)",
                                 (user["id"], chat_id, name, json.dumps(args, ensure_ascii=False), "pending", db.now()))
                    yield step(tsid, label, "waiting", None, "wartet auf Bestätigung", agent)
                    yield {"type": "confirm", "action_id": aid, "tool": name, "label": label,
                           "preview": tools.preview_text(name, args)}
                    result = (f"Aktion #{aid} ({label}) wartet auf Bestätigung durch den Nutzer im Dashboard. "
                              "Sag ihm kurz, was passieren wird, wenn er bestätigt.")
                else:
                    yield step(tsid, label, "active", None, json.dumps(args, ensure_ascii=False)[:120], agent)
                    yield {"type": "tool", "name": name, "args": args}
                    out = await tools.execute(user, name, args, chat_id)
                    result = out["result"]
                    yield step(tsid, label, "error" if out["status"] == "error" else "done", out["ms"],
                               result[:140], agent)
                    if out.get("ui"):
                        yield {"type": "ui", **out["ui"]}
                    if out.get("attach"):
                        attachments.append(out["attach"])
                        yield {"type": "token", "text": f"\n\n{out['attach']}\n\n"}
                    if out["status"] == "error":
                        result += "\n(Selbstkorrektur: prüfe die Argumente oder versuche einen anderen Weg.)"
                msgs.append({"role": "tool", "content": result[:9000], "tool_name": name})
    except Exception as e:  # noqa: BLE001
        err = f"⚠ Fehler: {e}"
        yield {"type": "error", "text": err}
        yield step("error", "Fehler", "error", None, str(e)[:140], "system")
        full += f"\n{err}"

    final = (full.strip() + ("\n\n" + "\n".join(a for a in attachments if a not in full) if attachments else "")).strip()
    amid = db.add_message(chat_id, "assistant", final or "…")
    total = int((time.perf_counter() - t_start) * 1000)
    yield step("answer", "Antwort", "done", total, f"{len(final)} Zeichen", "output")
    yield {"type": "done", "message_id": amid, "text": final, "total_ms": total}

    # ---- Lernen (im Hintergrund, blockiert die Antwort nicht)
    yield step("learn", "Lernen", "active", kind="memory")
    try:
        await asyncio.to_thread(memory.index_message, user["id"], chat_id, amid, "assistant", final, title)
        learned = await asyncio.to_thread(memory.learn, user["id"], text, final)
    except Exception as e:  # noqa: BLE001
        learned = []
        print(f"[Lernen] {e}")
    yield step("learn", "Lernen", "done", None, f"{len(learned)} neue Infos" if learned else "nichts Neues", "memory")
    if learned:
        yield {"type": "learned", "items": learned}


async def run_collect(user, chat_id, text, images=None) -> str:
    result = ""
    async for ev in run(user, chat_id, text, images):
        if ev["type"] == "done":
            result = ev["text"]
    return result


def approve(user, action_id, approved: bool):
    """Führt eine bestätigte Aktion aus (oder lehnt sie ab) und schreibt das Ergebnis in den Chat."""
    a = db.one("SELECT * FROM actions WHERE id=? AND user_id=? AND status='pending'", (action_id, user["id"]))
    if not a:
        return {"error": "Aktion nicht gefunden oder schon erledigt."}
    label = (tools.info(a["tool"]) or {}).get("label", a["tool"])
    if not approved:
        db.run("UPDATE actions SET status='rejected' WHERE id=?", (action_id,))
        if a["chat_id"]:
            db.add_message(a["chat_id"], "assistant", f"✖ Aktion „{label}“ abgelehnt.")
        return {"status": "rejected"}
    db.run("UPDATE actions SET status='approved' WHERE id=?", (action_id,))
    out = tools.run_sync(user, a["tool"], json.loads(a["args"] or "{}"), a["chat_id"])
    msg = f"{'✔' if out['status'] == 'done' else '⚠'} **{label}** ausgeführt:\n{out['result'][:3000]}"
    if out.get("attach"):
        msg += f"\n\n{out['attach']}"
    if a["chat_id"]:
        db.add_message(a["chat_id"], "assistant", msg)
    return {"status": out["status"], "result": out["result"], "ui": out.get("ui"), "ms": out["ms"], "message": msg}
JARVIS_EOF
mkdir -p 'backend/agents'
cat > 'backend/agents/telegram_bot.py' <<'JARVIS_EOF'
"""Telegram: von unterwegs schreiben/sprechen. Antwortet NUR deiner Chat-ID; Fremde werden protokolliert."""
import asyncio
import tempfile
import threading
import time

import httpx

from core import db
from core.config import settings
from engines import voice

API = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}"


def _send(chat_id, text):
    httpx.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text[:4000]}, timeout=20)


def _voice_to_text(file_id):
    info = httpx.get(f"{API}/getFile", params={"file_id": file_id}, timeout=20).json()["result"]
    data = httpx.get(f"https://api.telegram.org/file/bot{settings.TELEGRAM_TOKEN}/{info['file_path']}", timeout=60).content
    with tempfile.NamedTemporaryFile(suffix=".ogg") as f:
        f.write(data)
        f.flush()
        return voice.transcribe(f.name)["text"]


def _loop():
    from agents import task_agent
    user = db.one("SELECT id, username, token_version FROM users ORDER BY id LIMIT 1")
    if not user:
        return print("[Telegram] Kein Nutzer – Bot pausiert.")
    offset = 0
    while True:
        try:
            r = httpx.get(f"{API}/getUpdates", params={"timeout": 50, "offset": offset}, timeout=60).json()
            for upd in r.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message") or {}
                chat_id = str(msg.get("chat", {}).get("id", ""))
                if chat_id != str(settings.TELEGRAM_CHAT_ID):
                    db.log_security(f"telegram:{chat_id}", "fremder_telegram_zugriff", str(msg.get("from", {}).get("username")))
                    continue
                text = msg.get("text")
                if not text and msg.get("voice"):
                    text = _voice_to_text(msg["voice"]["file_id"])
                    _send(chat_id, f"🎙 {text}")
                if not text or text.strip() == "/start":
                    continue
                cid = db.find_or_create_chat(user["id"], "📱 Telegram")
                _send(chat_id, asyncio.run(task_agent.run_collect(user, cid, text)))
        except Exception as e:  # noqa: BLE001
            print(f"[Telegram] {e}")
            time.sleep(5)


def start():
    if settings.TELEGRAM_TOKEN and settings.TELEGRAM_CHAT_ID:
        threading.Thread(target=_loop, daemon=True).start()
JARVIS_EOF
mkdir -p 'backend/agents'
cat > 'backend/agents/web_agent.py' <<'JARVIS_EOF'
"""WEB AGENT: Websuche (eigene SearXNG), Webseiten lesen (Playwright), selbstständige Recherche."""
import re
import uuid

import httpx

from core.config import settings
from core.tools import tool
from engines import memory


def search(query, news=False, n=6):
    params = {"q": query, "format": "json"}
    if news:
        params["categories"] = "news"
    r = httpx.get(f"{settings.SEARXNG_URL}/search", params=params, timeout=20)
    r.raise_for_status()
    return r.json().get("results", [])[:n]


@tool("web_search", "Sucht im Internet (private, eigene Suchmaschine). Für aktuelle Infos, News, Fakten.",
      {"query": {"type": "string"}, "news": {"type": "boolean"}}, ["query"], label="Websuche", agent="web")
def web_search(user, query, news=False):
    res = search(query, news)
    if not res:
        return "Keine Ergebnisse."
    txt = "\n".join(f"- {x.get('title')} ({x.get('url')}): {(x.get('content') or '')[:300]}" for x in res)
    return {"result": txt, "ui": {"widget": "info", "title": f"🔎 {query}",
                                  "text": "\n".join(f"• [{x.get('title')}]({x.get('url')})" for x in res)}}


def fetch_page(url, screenshot=False):
    """Lädt eine Seite wie ein echter Browser (Playwright). Fallback: einfacher Abruf."""
    shot = None
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(headless=True)
            pg = b.new_page(viewport={"width": 1280, "height": 900})
            pg.goto(url, timeout=30000, wait_until="domcontentloaded")
            pg.wait_for_timeout(1200)
            title, text = pg.title(), pg.inner_text("body")
            if screenshot:
                shot = f"{uuid.uuid4().hex}.png"
                pg.screenshot(path=str(settings.FILES_DIR / shot))
            b.close()
    except ImportError:
        from bs4 import BeautifulSoup
        r = httpx.get(url, timeout=20, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        for t in soup(["script", "style", "nav", "footer", "noscript"]):
            t.decompose()
        title, text = (soup.title.string if soup.title else url), soup.get_text(" ")
    return title, re.sub(r"\s+", " ", text).strip(), shot


@tool("browse_page", "Öffnet eine Webseite im unsichtbaren Browser, liest den Inhalt und macht optional einen Screenshot.",
      {"url": {"type": "string"}, "screenshot": {"type": "boolean"}}, ["url"], label="Webseite lesen", agent="web")
def browse_page(user, url, screenshot=True):
    if not url.startswith(("http://", "https://")):
        return "Nur http/https-Links."
    title, text, shot = fetch_page(url, screenshot)
    out = {"result": f"{title}\n\n{text[:7000]}"}
    if shot:
        out["ui"] = {"widget": "image", "title": f"🌐 {title}", "src": f"/api/files/{shot}", "text": url}
    return out


@tool("research", "Selbstständige Recherche: sucht, liest die besten Quellen und liefert das Material für eine "
      "fundierte Antwort mit Quellen. save=true speichert das Ergebnis in der Wissensdatenbank.",
      {"question": {"type": "string"}, "save": {"type": "boolean"}}, ["question"], label="Recherche", agent="web")
def research(user, question, save=False):
    results = search(question, n=8)
    material = []
    for r in results[:3]:
        try:
            title, text, _ = fetch_page(r["url"])
            material.append(f"### {title}\nQuelle: {r['url']}\n{text[:3500]}")
        except Exception as e:  # noqa: BLE001
            material.append(f"### {r.get('title')} (nicht lesbar: {e})\n{r.get('content', '')}")
    others = "\n".join(f"- {r.get('title')}: {r.get('url')}" for r in results[3:])
    txt = "\n\n".join(material) + (f"\n\nWeitere Quellen:\n{others}" if others else "")
    if save:
        memory.add_knowledge(user["id"], f"Recherche: {question}", txt)
    return txt[:12000]


@tool("save_webpage_to_knowledge", "Speichert eine Webseite dauerhaft in der Wissensdatenbank.",
      {"url": {"type": "string"}}, ["url"], label="Wissen speichern", agent="memory")
def save_webpage(user, url):
    title, text, _ = fetch_page(url)
    r = memory.add_knowledge(user["id"], f"{title} ({url})", text)
    return f"„{title}“ gespeichert ({r['chunks']} Abschnitte)."
JARVIS_EOF
mkdir -p 'backend'
cat > 'backend/control_panel.py' <<'JARVIS_EOF'
"""J.A.R.V.I.S. STEUERFENSTER (Streamlit) – zentrale Verwaltung von Gedächtnis, Aktionen, Automatisierungen, Sicherheit.
Start:  streamlit run control_panel.py --server.address 127.0.0.1 --server.port 8501
Läuft nur auf deinem Rechner (127.0.0.1) und verlangt dein Passwort."""
import json
from datetime import datetime

import pandas as pd
import streamlit as st

from core import db
from agents import security, system_agent
from engines import memory

st.set_page_config(page_title="J.A.R.V.I.S. Steuerfenster", page_icon="◎", layout="wide")
st.markdown("""<style>
.stApp{background:#02060c;color:#d6f5ff} h1,h2,h3{color:#8cecff;letter-spacing:.15em;font-weight:300}
[data-testid="stMetricValue"]{color:#3fd8ff;font-family:monospace}
</style>""", unsafe_allow_html=True)
db.init()

# ---------------------------------------------------------------- Login
if "uid" not in st.session_state:
    st.title("J.A.R.V.I.S. · STEUERFENSTER")
    with st.form("login"):
        u = st.text_input("Benutzername")
        p = st.text_input("Passwort", type="password")
        if st.form_submit_button("Anmelden"):
            row = db.one("SELECT * FROM users WHERE username=?", (u,))
            if row and security.check_pw(p, row["pw_hash"]):
                st.session_state.uid = row["id"]
                db.log_security("127.0.0.1", "login_ok_steuerfenster", u)
                st.rerun()
            else:
                db.log_security("127.0.0.1", "login_fehlgeschlagen_steuerfenster", u)
                st.error("Falsch.")
    st.stop()

uid = st.session_state.uid
fmt = lambda ts: datetime.fromtimestamp(ts).strftime("%d.%m.%Y %H:%M") if ts else ""  # noqa: E731
st.title("J.A.R.V.I.S. · STEUERFENSTER")
tabs = st.tabs(["📊 Dashboard", "🧠 Gedächtnis", "👤 Profil", "💬 Gespräche", "📚 Wissen", "⚡ Aktionen",
                "⏰ Automatisierung", "🛡 Sicherheit"])

with tabs[0]:
    s = memory.stats(uid)
    cols = st.columns(6)
    for c, (label, val) in zip(cols, [("Erinnerungen", sum(v for k, v in s.items() if k in memory.KINDS)),
                                      ("Verknüpfungen", s["links"]), ("Nachrichten", s["messages"]),
                                      ("Gesprächstage", s["episodes"]), ("Dokumente", s["documents"]), ("Aktionen", s["actions"])]):
        c.metric(label, val)
    st.subheader("Selbstdiagnose")
    d = system_agent.diagnose(uid)
    st.progress(d["ok"] / d["total"], text=f"{d['ok']}/{d['total']} Systeme OK")
    st.dataframe(pd.DataFrame([{"Status": "✅" if c["ok"] else "❌", "System": c["name"], "Info": c["detail"]} for c in d["checks"]]),
                 hide_index=True, use_container_width=True)
    acts = db.all("SELECT tool, status, duration_ms FROM actions WHERE user_id=? AND duration_ms IS NOT NULL", (uid,))
    if acts:
        st.subheader("Werkzeug-Nutzung & Geschwindigkeit")
        df = pd.DataFrame(acts).groupby("tool").agg(Aufrufe=("status", "count"), Ø_ms=("duration_ms", "mean")).round(0)
        st.bar_chart(df["Aufrufe"])
        st.dataframe(df, use_container_width=True)

with tabs[1]:
    c1, c2 = st.columns([1, 2])
    kind = c1.selectbox("Art", ["alle"] + list(memory.KINDS), format_func=lambda k: memory.KINDS.get(k, "Alle"))
    q = c2.text_input("Semantische Suche")
    if q:
        rows = memory.search(uid, q, k=40, kinds=None if kind == "alle" else [kind], touch=False)
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    else:
        sql, args = "SELECT id, kind, text, importance, uses, updated FROM memories WHERE user_id=?", [uid]
        if kind != "alle":
            sql += " AND kind=?"
            args.append(kind)
        rows = db.all(sql + " ORDER BY kind, importance DESC", args)
        df = pd.DataFrame(rows or [{"id": None, "kind": "", "text": "", "importance": 3, "uses": 0, "updated": 0}])
        if rows:
            df["updated"] = df["updated"].map(fmt)
        edited = st.data_editor(df, hide_index=True, use_container_width=True, disabled=["id", "uses", "updated"],
                                column_config={"kind": st.column_config.SelectboxColumn("Art", options=list(memory.KINDS)),
                                               "importance": st.column_config.NumberColumn("Wichtigkeit", min_value=1, max_value=5)})
        if st.button("💾 Änderungen speichern") and rows:
            for _, r in edited.iterrows():
                orig = next((x for x in rows if x["id"] == r["id"]), None)
                if orig and (orig["text"] != r["text"] or orig["kind"] != r["kind"] or orig["importance"] != r["importance"]):
                    memory.update(uid, int(r["id"]), r["text"], r["kind"], int(r["importance"]))
            st.success("Gespeichert.")
    with st.form("add_mem", clear_on_submit=True):
        st.write("**Neue Erinnerung / Regel**")
        a, b, c = st.columns([1, 3, 1])
        k = a.selectbox("Art", list(memory.KINDS)[:6], format_func=memory.KINDS.get)
        t = b.text_input("Text", placeholder="z.B. Antworte mir immer auf Deutsch.")
        i = c.slider("Wichtigkeit", 1, 5, 3)
        if st.form_submit_button("Hinzufügen") and t:
            memory.add(uid, t, k, i, "steuerfenster")
            st.rerun()
    del_id = st.number_input("Erinnerung löschen (ID)", min_value=0, step=1)
    if st.button("🗑 Löschen") and del_id:
        memory.delete(uid, int(del_id))
        st.rerun()
    if st.button("🔄 Semantischen Index neu aufbauen"):
        st.json(memory.reindex(uid))

with tabs[2]:
    prof = db.all_settings(uid)
    with st.form("profile"):
        name = st.text_input("Name", prof.get("name", ""))
        anrede = st.text_input("Anrede (so spricht Jarvis dich an)", prof.get("anrede", ""))
        langs = ["auto", "de", "tr", "en"]
        lang = st.selectbox("Sprache", langs, index=langs.index(prof.get("language", "auto")) if prof.get("language", "auto") in langs else 0)
        about = st.text_area("Über mich", prof.get("about", ""))
        if st.form_submit_button("Speichern"):
            for k_, v_ in (("name", name), ("anrede", anrede), ("language", lang), ("about", about)):
                db.set_setting(uid, k_, v_)
            st.success("Profil gespeichert.")
    for kk, head in (("goal", "Ziele"), ("project", "Projekte"), ("preference", "Vorlieben"), ("rule", "Regeln")):
        st.write(f"**{head}**")
        for m in memory.by_kind(uid, kk, 50):
            st.write(f"• {m['text']}  `#{m['id']}`")

with tabs[3]:
    for e in db.all("SELECT * FROM episodes WHERE user_id=? ORDER BY day DESC LIMIT 60", (uid,)):
        with st.expander(f"{e['day']} – {e['title']}"):
            st.write(e["summary"])
    if st.button("Heutige Gespräche jetzt zusammenfassen"):
        memory.summarize_day(uid)
        st.rerun()
    q2 = st.text_input("Frühere Gespräche durchsuchen")
    if q2:
        st.json(memory.search_conversations(uid, q2))

with tabs[4]:
    up = st.file_uploader("Dokument lernen (txt, md, pdf, Code)")
    if up and st.button("In Wissensdatenbank speichern"):
        if up.name.lower().endswith(".pdf"):
            from pypdf import PdfReader
            text = "\n".join(p.extract_text() or "" for p in PdfReader(up).pages)
        else:
            text = up.read().decode("utf-8", errors="ignore")
        st.json(memory.add_knowledge(uid, up.name, text))
    docs = db.all("SELECT id, name, chunks, created FROM knowledge_docs WHERE user_id=? ORDER BY id DESC", (uid,))
    if docs:
        st.dataframe(pd.DataFrame(docs).assign(created=lambda x: x.created.map(fmt)), hide_index=True, use_container_width=True)

with tabs[5]:
    from agents import task_agent
    user = db.one("SELECT id, username, token_version FROM users WHERE id=?", (uid,))
    for a in db.all("SELECT * FROM actions WHERE user_id=? AND status='pending' ORDER BY id DESC", (uid,)):
        with st.container(border=True):
            st.write(f"**⚡ {a['tool']}** #{a['id']} · {fmt(a['created'])}")
            st.code(json.dumps(json.loads(a["args"] or "{}"), ensure_ascii=False, indent=2))
            c1, c2 = st.columns(2)
            if c1.button("✔ Ausführen", key=f"ok{a['id']}"):
                st.write(task_agent.approve(user, a["id"], True))
            if c2.button("✖ Ablehnen", key=f"no{a['id']}"):
                task_agent.approve(user, a["id"], False)
                st.rerun()
    log = db.all("SELECT id, tool, status, duration_ms, substr(result,1,200) AS ergebnis, created FROM actions "
                 "WHERE user_id=? ORDER BY id DESC LIMIT 300", (uid,))
    if log:
        st.subheader("Aktionsgedächtnis")
        st.dataframe(pd.DataFrame(log).assign(created=lambda x: x.created.map(fmt)), hide_index=True, use_container_width=True)

with tabs[6]:
    autos = db.all("SELECT * FROM automations WHERE user_id=?", (uid,))
    for a in autos:
        c1, c2, c3 = st.columns([4, 1, 1])
        c1.write(f"**{a['hhmm']}** ({a['weekdays']}) – {a['prompt']}")
        if c2.button("An/Aus", key=f"t{a['id']}"):
            db.run("UPDATE automations SET enabled=1-enabled WHERE id=?", (a["id"],))
            st.rerun()
        if c3.button("🗑", key=f"d{a['id']}"):
            db.run("DELETE FROM automations WHERE id=?", (a["id"],))
            st.rerun()
    with st.form("auto"):
        p = st.text_input("Auftrag", placeholder="Fasse jeden Morgen die wichtigsten KI-News zusammen")
        t = st.time_input("Uhrzeit")
        w = st.multiselect("Tage", list(range(7)), default=list(range(7)), format_func=lambda d: "Mo Di Mi Do Fr Sa So".split()[d])
        if st.form_submit_button("Anlegen") and p:
            db.run("INSERT INTO automations(user_id,prompt,hhmm,weekdays) VALUES(?,?,?,?)",
                   (uid, p, t.strftime("%H:%M"), "".join(map(str, w))))
            st.rerun()
    rem = db.all("SELECT id, text, due, done FROM reminders WHERE user_id=? ORDER BY due DESC LIMIT 50", (uid,))
    if rem:
        st.subheader("Erinnerungen")
        st.dataframe(pd.DataFrame(rem).assign(due=lambda x: x.due.map(fmt)), hide_index=True, use_container_width=True)

with tabs[7]:
    st.write("Nur **ein** Besitzer-Konto · Zugriff nur aus deinem Netz · bcrypt · Token-Ablauf · Sperre nach 5 Fehlversuchen")
    log = db.all("SELECT ts, ip, event, detail FROM security_log ORDER BY id DESC LIMIT 300")
    if log:
        st.dataframe(pd.DataFrame(log).assign(ts=lambda x: x.ts.map(fmt)), hide_index=True, use_container_width=True)
    if st.button("🔒 Alle Geräte abmelden"):
        db.run("UPDATE users SET token_version=token_version+1 WHERE id=?", (uid,))
        db.log_security("127.0.0.1", "alle_geräte_abgemeldet", "")
        st.success("Alle Sitzungen beendet.")
    if st.button("Steuerfenster abmelden"):
        del st.session_state["uid"]
        st.rerun()
JARVIS_EOF
mkdir -p 'backend/core'
cat > 'backend/core/__init__.py' <<'JARVIS_EOF'

JARVIS_EOF
mkdir -p 'backend/core'
cat > 'backend/core/config.py' <<'JARVIS_EOF'
"""Zentrale Konfiguration. Alle Werte kommen aus backend/.env"""
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
load_dotenv(BACKEND / ".env")


def env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def flag(key: str, default: bool = False) -> bool:
    return env(key, str(default)).lower() in ("1", "true", "yes", "ja", "on")


class Settings:
    ROOT = ROOT
    DATA_DIR = Path(env("DATA_DIR", str(ROOT / "data")))
    VOICES_DIR = Path(env("VOICES_DIR", str(ROOT / "voices")))
    FRONTEND_DIR = ROOT / "frontend"
    CERT_DIR = ROOT / "certs"

    HOST = env("HOST", "0.0.0.0")
    PORT = int(env("PORT", "8443"))
    TOKEN_HOURS = int(env("TOKEN_HOURS", "72"))
    # Nur diese Netze dürfen zugreifen (Standard: eigener Rechner, Heim-WLAN, Tailscale)
    ALLOWED_NETWORKS = env("ALLOWED_NETWORKS", "127.0.0.0/8,::1/128,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,100.64.0.0/10,fd00::/8")

    # Gehirn (Ollama, lokal)
    OLLAMA_URL = env("OLLAMA_URL", "http://127.0.0.1:11434")
    LLM_MODEL = env("LLM_MODEL", "qwen2.5:7b")
    FAST_MODEL = env("FAST_MODEL", "") or env("LLM_MODEL", "qwen2.5:7b")  # fürs Lernen/Zusammenfassen
    VISION_MODEL = env("VISION_MODEL", "qwen2.5vl:7b")
    EMBED_MODEL = env("EMBED_MODEL", "nomic-embed-text")
    NUM_CTX = int(env("NUM_CTX", "8192"))
    KEEP_ALIVE = env("KEEP_ALIVE", "30m")

    # Gedächtnis
    AUTO_LEARN = flag("AUTO_LEARN", True)
    DAILY_SUMMARY_TIME = env("DAILY_SUMMARY_TIME", "23:45")

    # Sprache
    WHISPER_MODEL = env("WHISPER_MODEL", "small")
    WHISPER_DEVICE = env("WHISPER_DEVICE", "auto")

    # Web
    SEARXNG_URL = env("SEARXNG_URL", "http://127.0.0.1:8888")

    # Computer-Steuerung
    COMPUTER_CONTROL = flag("COMPUTER_CONTROL", True)
    AUTO_APPROVE = flag("AUTO_APPROVE", False)  # False = jede riskante Aktion braucht deine Bestätigung
    FILE_ROOT = Path(env("FILE_ROOT", str(Path.home()))).expanduser()

    # Kalender / Mail / Dienste
    CALENDAR_ICS_URL = env("CALENDAR_ICS_URL")
    TIMEZONE = env("TIMEZONE", "Europe/Berlin")
    IMAP_HOST = env("IMAP_HOST", "imap.gmail.com")
    IMAP_USER = env("IMAP_USER")
    IMAP_PASSWORD = env("IMAP_PASSWORD")
    IMAP_DRAFTS_FOLDER = env("IMAP_DRAFTS_FOLDER", "[Gmail]/Drafts")
    SPOTIFY_CLIENT_ID = env("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = env("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REDIRECT = env("SPOTIFY_REDIRECT", "http://127.0.0.1:8765/callback")
    TELEGRAM_TOKEN = env("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = env("TELEGRAM_CHAT_ID")

    # Medien
    IMAGE_GEN = flag("IMAGE_GEN", False)
    IMAGE_MODEL = env("IMAGE_MODEL", "stabilityai/sdxl-turbo")
    IMAGE_STEPS = int(env("IMAGE_STEPS", "4"))

    # Briefing
    BRIEFING_TIME = env("BRIEFING_TIME", "07:00")
    BRIEFING_CITY = env("BRIEFING_CITY", "Berlin")
    BRIEFING_NEWS_QUERY = env("BRIEFING_NEWS_QUERY", "Nachrichten heute")
    ALLOW_WEATHER = flag("ALLOW_WEATHER", False)


settings = Settings()
for d in (settings.DATA_DIR, settings.DATA_DIR / "files", settings.VOICES_DIR):
    d.mkdir(parents=True, exist_ok=True)
settings.DB_PATH = settings.DATA_DIR / "jarvis.db"
settings.FILES_DIR = settings.DATA_DIR / "files"

_key_file = settings.DATA_DIR / "secret.key"
if env("SECRET_KEY"):
    settings.SECRET_KEY = env("SECRET_KEY")
else:
    if not _key_file.exists():
        _key_file.write_text(secrets.token_urlsafe(48))
        _key_file.chmod(0o600)
    settings.SECRET_KEY = _key_file.read_text().strip()
JARVIS_EOF
mkdir -p 'backend/core'
cat > 'backend/core/db.py' <<'JARVIS_EOF'
"""SQLite: dauerhafte Speicherung aller Daten (eine Datei: data/jarvis.db)."""
import sqlite3
import threading
import time

from core.config import settings

_lock = threading.RLock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, pw_hash TEXT NOT NULL,
    token_version INTEGER DEFAULT 0, created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, title TEXT NOT NULL,
    created REAL NOT NULL, updated REAL NOT NULL);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY, chat_id INTEGER NOT NULL, role TEXT NOT NULL,
    content TEXT NOT NULL, has_images INTEGER DEFAULT 0, created REAL NOT NULL);
-- Gedächtnis: profile | preference | rule | fact | goal | project | knowledge | episode
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, kind TEXT NOT NULL DEFAULT 'fact',
    text TEXT NOT NULL, importance INTEGER DEFAULT 3, source TEXT DEFAULT 'chat',
    created REAL NOT NULL, updated REAL NOT NULL, uses INTEGER DEFAULT 0, last_used REAL);
-- Verknüpfungsgedächtnis
CREATE TABLE IF NOT EXISTS memory_links (
    a INTEGER NOT NULL, b INTEGER NOT NULL, relation TEXT DEFAULT 'ähnlich', weight REAL DEFAULT 0.5,
    PRIMARY KEY (a, b));
-- Gesprächsgedächtnis: Tageszusammenfassungen
CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, chat_id INTEGER, day TEXT NOT NULL,
    title TEXT, summary TEXT NOT NULL, created REAL NOT NULL, UNIQUE(chat_id, day));
-- Wissens-/Dateigedächtnis
CREATE TABLE IF NOT EXISTS knowledge_docs (
    id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, name TEXT NOT NULL, chunks INTEGER, created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id INTEGER PRIMARY KEY, doc_id INTEGER NOT NULL, user_id INTEGER NOT NULL, text TEXT NOT NULL);
-- Aktionsgedächtnis: jedes Werkzeug, jede Aktion
CREATE TABLE IF NOT EXISTS actions (
    id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, chat_id INTEGER, tool TEXT NOT NULL,
    args TEXT, status TEXT NOT NULL, result TEXT, duration_ms INTEGER, created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, title TEXT NOT NULL,
    start TEXT NOT NULL, end TEXT, location TEXT, notes TEXT);
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, text TEXT NOT NULL, due REAL NOT NULL, done INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS automations (
    id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, prompt TEXT NOT NULL, hhmm TEXT NOT NULL,
    weekdays TEXT DEFAULT '0123456', enabled INTEGER DEFAULT 1, last_run TEXT);
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, kind TEXT, text TEXT NOT NULL,
    chat_id INTEGER, created REAL NOT NULL, seen INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS security_log (
    id INTEGER PRIMARY KEY, ts REAL NOT NULL, ip TEXT, event TEXT NOT NULL, detail TEXT);
CREATE TABLE IF NOT EXISTS user_settings (
    user_id INTEGER NOT NULL, key TEXT NOT NULL, value TEXT, PRIMARY KEY (user_id, key));
CREATE INDEX IF NOT EXISTS idx_msg_chat ON messages(chat_id);
CREATE INDEX IF NOT EXISTS idx_mem_user ON memories(user_id, kind);
CREATE INDEX IF NOT EXISTS idx_act_user ON actions(user_id);
"""

_conn = sqlite3.connect(settings.DB_PATH, check_same_thread=False)
_conn.row_factory = sqlite3.Row
_conn.execute("PRAGMA journal_mode=WAL")


def init():
    with _lock:
        _conn.executescript(SCHEMA)
        _conn.commit()


def all(sql, args=()):
    with _lock:
        return [dict(r) for r in _conn.execute(sql, args).fetchall()]


def one(sql, args=()):
    with _lock:
        r = _conn.execute(sql, args).fetchone()
        return dict(r) if r else None


def run(sql, args=()):
    with _lock:
        cur = _conn.execute(sql, args)
        _conn.commit()
        return cur.lastrowid


def now():
    return time.time()


def get_setting(user_id, key, default=None):
    r = one("SELECT value FROM user_settings WHERE user_id=? AND key=?", (user_id, key))
    return r["value"] if r and r["value"] not in (None, "") else default


def set_setting(user_id, key, value):
    run("INSERT INTO user_settings(user_id,key,value) VALUES(?,?,?) "
        "ON CONFLICT(user_id,key) DO UPDATE SET value=excluded.value", (user_id, key, str(value)))


def all_settings(user_id):
    return {r["key"]: r["value"] for r in all("SELECT key,value FROM user_settings WHERE user_id=?", (user_id,))}


def create_chat(user_id, title="Neuer Chat"):
    t = now()
    return run("INSERT INTO chats(user_id,title,created,updated) VALUES(?,?,?,?)", (user_id, title, t, t))


def find_or_create_chat(user_id, title):
    r = one("SELECT id FROM chats WHERE user_id=? AND title=? ORDER BY id DESC", (user_id, title))
    return r["id"] if r else create_chat(user_id, title)


def add_message(chat_id, role, content, has_images=False):
    t = now()
    mid = run("INSERT INTO messages(chat_id,role,content,has_images,created) VALUES(?,?,?,?,?)",
              (chat_id, role, content, int(has_images), t))
    run("UPDATE chats SET updated=? WHERE id=?", (t, chat_id))
    return mid


def notify(user_id, text, kind="info", chat_id=None):
    return run("INSERT INTO notifications(user_id,kind,text,chat_id,created) VALUES(?,?,?,?,?)",
               (user_id, kind, text, chat_id, now()))


def log_security(ip, event, detail=""):
    run("INSERT INTO security_log(ts,ip,event,detail) VALUES(?,?,?,?)", (now(), ip, event, detail[:500]))
JARVIS_EOF
mkdir -p 'backend/core'
cat > 'backend/core/llm.py' <<'JARVIS_EOF'
"""LLM-API: Verbindung zum lokalen Ollama-Server (Intelligenz & Antworten, Embeddings)."""
import json

import httpx

from core.config import settings


def _payload(messages, model, stream, tools=None, fmt=None):
    p = {"model": model or settings.LLM_MODEL, "messages": messages, "stream": stream,
         "keep_alive": settings.KEEP_ALIVE, "options": {"num_ctx": settings.NUM_CTX}}
    if tools:
        p["tools"] = tools
    if fmt:
        p["format"] = fmt
    return p


async def stream_chat(messages, tools=None, model=None):
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", f"{settings.OLLAMA_URL}/api/chat",
                                 json=_payload(messages, model, True, tools)) as r:
            if r.status_code != 200:
                body = (await r.aread()).decode(errors="ignore")
                raise RuntimeError(f"Ollama-Fehler {r.status_code}: {body[:300]}")
            async for line in r.aiter_lines():
                if line.strip():
                    yield json.loads(line)


def complete(messages, model=None, fmt=None) -> str:
    r = httpx.post(f"{settings.OLLAMA_URL}/api/chat", json=_payload(messages, model, False, fmt=fmt), timeout=600)
    r.raise_for_status()
    return r.json()["message"]["content"]


def complete_json(prompt, model=None):
    txt = complete([{"role": "user", "content": prompt}], model or settings.FAST_MODEL, fmt="json")
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        return None


def embed(texts: list[str]) -> list[list[float]]:
    r = httpx.post(f"{settings.OLLAMA_URL}/api/embed",
                   json={"model": settings.EMBED_MODEL, "input": texts, "keep_alive": settings.KEEP_ALIVE}, timeout=120)
    r.raise_for_status()
    return r.json()["embeddings"]


def health() -> dict:
    try:
        r = httpx.get(f"{settings.OLLAMA_URL}/api/tags", timeout=3)
        names = [m["name"] for m in r.json().get("models", [])]
        return {"ok": True, "models": names}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e), "models": []}
JARVIS_EOF
mkdir -p 'backend/core'
cat > 'backend/core/tools.py' <<'JARVIS_EOF'
"""Werkzeug-Register: alle Agents melden hier ihre Fähigkeiten an."""
import asyncio
import json
import time

from core import db
from core.config import settings

TOOLS: dict[str, dict] = {}


def tool(name, description, params=None, required=(), enabled=lambda: True, confirm=False,
         preview=None, label=None, agent="core"):
    """confirm=True -> Aktion wird erst nach deiner Bestätigung ausgeführt (Vorschau)."""
    def deco(fn):
        TOOLS[name] = {
            "fn": fn, "enabled": enabled, "confirm": confirm, "preview": preview,
            "label": label or name, "agent": agent,
            "schema": {"type": "function", "function": {
                "name": name, "description": description,
                "parameters": {"type": "object", "properties": params or {}, "required": list(required)},
            }},
        }
        return fn
    return deco


def schemas():
    return [t["schema"] for t in TOOLS.values() if t["enabled"]()]


def enabled_names():
    return [n for n, t in TOOLS.items() if t["enabled"]()]


def info(name):
    return TOOLS.get(name)


def needs_confirm(name):
    t = TOOLS.get(name)
    return bool(t and t["confirm"] and not settings.AUTO_APPROVE)


def preview_text(name, args):
    t = TOOLS.get(name)
    if t and t["preview"]:
        try:
            return t["preview"](**args)
        except Exception:  # noqa: BLE001
            pass
    return json.dumps(args, ensure_ascii=False, indent=2)


def _normalize(res):
    if isinstance(res, dict) and "result" in res:
        return {"result": str(res["result"]), "attach": res.get("attach"), "ui": res.get("ui")}
    if isinstance(res, str):
        return {"result": res, "attach": None, "ui": None}
    return {"result": json.dumps(res, ensure_ascii=False, default=str), "attach": None, "ui": None}


def run_sync(user, name, args, chat_id=None):
    """Führt ein Werkzeug aus und schreibt es ins Aktionsgedächtnis."""
    t = TOOLS.get(name)
    t0 = time.perf_counter()
    if not t or not t["enabled"]():
        out, status = _normalize(f"Werkzeug '{name}' ist nicht verfügbar."), "error"
    else:
        try:
            out, status = _normalize(t["fn"](user, **(args or {}))), "done"
        except TypeError as e:
            out, status = _normalize(f"Falsche Argumente für {name}: {e}"), "error"
        except Exception as e:  # noqa: BLE001
            out, status = _normalize(f"Fehler bei {name}: {e}"), "error"
    ms = int((time.perf_counter() - t0) * 1000)
    db.run("INSERT INTO actions(user_id,chat_id,tool,args,status,result,duration_ms,created) VALUES(?,?,?,?,?,?,?,?)",
           (user["id"], chat_id, name, json.dumps(args, ensure_ascii=False, default=str), status,
            out["result"][:2000], ms, db.now()))
    out.update(status=status, ms=ms)
    return out


async def execute(user, name, args, chat_id=None):
    return await asyncio.to_thread(run_sync, user, name, args, chat_id)
JARVIS_EOF
mkdir -p 'backend'
cat > 'backend/create_user.py' <<'JARVIS_EOF'
"""Legt DEIN Besitzer-Konto an oder ändert dessen Passwort.
Es gibt bewusst nur EIN Konto und keine Registrierung im Web – nur du kannst Jarvis benutzen."""
import getpass
import sys

from core import db
from agents import security

db.init()
owner = db.one("SELECT id, username FROM users ORDER BY id LIMIT 1")
if owner:
    print(f"Besitzer-Konto existiert bereits: {owner['username']} – nur Passwort ändern möglich.")
    name = owner["username"]
else:
    name = input("Benutzername: ").strip()
    if not name:
        sys.exit("Abgebrochen.")
pw = getpass.getpass("Passwort (min. 12 Zeichen): ")
if len(pw) < 12 or pw != getpass.getpass("Passwort wiederholen: "):
    sys.exit("Passwort zu kurz oder stimmt nicht überein.")
if owner:
    security.change_password(owner["id"], pw)
    print("Passwort geändert. Alle Geräte müssen sich neu anmelden.")
else:
    db.run("INSERT INTO users(username,pw_hash,created) VALUES(?,?,?)", (name, security.hash_pw(pw), db.now()))
    print(f"Besitzer-Konto '{name}' angelegt.")
JARVIS_EOF
mkdir -p 'backend/engines'
cat > 'backend/engines/__init__.py' <<'JARVIS_EOF'

JARVIS_EOF
mkdir -p 'backend/engines'
cat > 'backend/engines/memory.py' <<'JARVIS_EOF'
"""MEMORY ENGINE – das Gedächtnis von Jarvis.

Gedächtnisarten:
  • Persönliches Gedächtnis / Persönlichkeitsprofil  kind=profile, preference, goal, project + Profil-Einstellungen
  • Regelgedächtnis        kind=rule        (wird IMMER befolgt, z.B. "sprich nur Deutsch")
  • Kurzzeitgedächtnis     die letzten Nachrichten des aktuellen Chats
  • Langzeitgedächtnis     kind=fact u.a., dauerhaft in SQLite + semantisch in ChromaDB
  • Gesprächsgedächtnis    jede Nachricht wird indexiert + Tageszusammenfassungen (episodes)
  • Wissensgedächtnis      hochgeladene Dateien/Webseiten, in Abschnitte zerlegt (knowledge_*)
  • Verknüpfungsgedächtnis memory_links: ähnliche Erinnerungen werden automatisch verbunden
  • Aktionsgedächtnis      Tabelle actions: jedes ausgeführte Werkzeug mit Ergebnis und Dauer

Semantische Suche: Embeddings (lokal, Ollama nomic-embed-text) + ChromaDB.
Fällt das aus, wird automatisch per Stichwort in SQLite gesucht.
"""
import re
import threading
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from core import db, llm
from core.config import settings

TZ = ZoneInfo(settings.TIMEZONE)
KINDS = {
    "profile": "Persönlich", "preference": "Vorliebe", "rule": "Regel", "fact": "Fakt",
    "goal": "Ziel", "project": "Projekt", "knowledge": "Wissen", "episode": "Gespräch",
}
ALWAYS_LOADED = ("rule", "profile", "goal", "project", "preference")
PROFILE_KEYS = {"name": "Name", "anrede": "Anrede", "language": "Sprache", "about": "Über mich"}
_chroma = None
_chroma_lock = threading.Lock()
_semantic_ok = True


# ------------------------------------------------------------------ Vektor-Speicher
def _col(user_id):
    global _chroma, _semantic_ok
    if not _semantic_ok:
        return None
    try:
        with _chroma_lock:
            if _chroma is None:
                import chromadb
                _chroma = chromadb.PersistentClient(path=str(settings.DATA_DIR / "chroma"))
        return _chroma.get_or_create_collection(f"user{user_id}", metadata={"hnsw:space": "cosine"})
    except Exception as e:  # noqa: BLE001
        print(f"[Memory] ChromaDB nicht verfügbar – Stichwortsuche aktiv ({e})")
        _semantic_ok = False
        return None


def _index(user_id, ids, texts, metas):
    col = _col(user_id)
    if col is None or not ids:
        return False
    try:
        col.upsert(ids=ids, documents=texts, metadatas=metas, embeddings=llm.embed(texts))
        return True
    except Exception as e:  # noqa: BLE001
        global _semantic_ok
        print(f"[Memory] Embeddings nicht verfügbar – Stichwortsuche aktiv ({e})")
        _semantic_ok = False
        return False


def _query(user_id, text, k, where=None):
    col = _col(user_id)
    if col is None:
        return None
    try:
        n = col.count()
        if n == 0:
            return None
        res = col.query(query_embeddings=llm.embed([text]), n_results=min(k, n), where=where)
        return [{"id": i, "text": d, "meta": m, "score": round(1 - dist, 3)}
                for i, d, m, dist in zip(res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0])]
    except Exception as e:  # noqa: BLE001
        print(f"[Memory] Suche fehlgeschlagen: {e}")
        return None


def _where(*conds):
    conds = [c for c in conds if c]
    return None if not conds else conds[0] if len(conds) == 1 else {"$and": conds}


def _words(text):
    return [w for w in re.findall(r"\w+", text.lower()) if len(w) > 2]


# ------------------------------------------------------------------ Langzeit / Persönlich / Regeln
def add(user_id, text, kind="fact", importance=3, source="chat"):
    """Speichert eine Erinnerung. Ähnliches wird aktualisiert statt doppelt gespeichert."""
    text = text.strip()
    kind = kind if kind in KINDS else "fact"
    if not text:
        return None
    t = db.now()
    similar = search(user_id, text, k=4, kinds=[kind], expand=False, touch=False)
    for s in similar:
        if s["score"] >= (0.9 if _semantic_ok else 0.8) or s["text"].lower() == text.lower():
            db.run("UPDATE memories SET text=?, updated=?, importance=MAX(importance,?) WHERE id=?",
                   (text, t, importance, s["mid"]))
            _index(user_id, [f"m{s['mid']}"], [text], [{"kind": kind, "ts": t, "type": "memory"}])
            return s["mid"]
    mid = db.run("INSERT INTO memories(user_id,kind,text,importance,source,created,updated) VALUES(?,?,?,?,?,?,?)",
                 (user_id, kind, text, int(importance), source, t, t))
    _index(user_id, [f"m{mid}"], [text], [{"kind": kind, "ts": t, "type": "memory"}])
    # Verknüpfungsgedächtnis: mit thematisch verwandten Erinnerungen verbinden
    for s in search(user_id, text, k=5, expand=False, touch=False):
        if s["mid"] != mid and (0.55 if _semantic_ok else 0.4) <= s["score"] < (0.9 if _semantic_ok else 0.8):
            db.run("INSERT OR IGNORE INTO memory_links(a,b,relation,weight) VALUES(?,?,?,?)",
                   (min(mid, s["mid"]), max(mid, s["mid"]), "verwandt", s["score"]))
    return mid


def update(user_id, mid, text=None, kind=None, importance=None):
    m = db.one("SELECT * FROM memories WHERE id=? AND user_id=?", (mid, user_id))
    if not m:
        return False
    text, kind = text or m["text"], kind or m["kind"]
    imp = importance if importance is not None else m["importance"]
    db.run("UPDATE memories SET text=?, kind=?, importance=?, updated=? WHERE id=?", (text, kind, imp, db.now(), mid))
    _index(user_id, [f"m{mid}"], [text], [{"kind": kind, "ts": db.now(), "type": "memory"}])
    return True


def delete(user_id, mid):
    db.run("DELETE FROM memories WHERE id=? AND user_id=?", (mid, user_id))
    db.run("DELETE FROM memory_links WHERE a=? OR b=?", (mid, mid))
    col = _col(user_id)
    if col is not None:
        try:
            col.delete(ids=[f"m{mid}"])
        except Exception:  # noqa: BLE001
            pass


def search(user_id, query, k=8, kinds=None, expand=True, touch=True):
    """Semantische Suche im Langzeitgedächtnis (+ verknüpfte Erinnerungen)."""
    kind_filter = {"kind": {"$in": list(kinds)}} if kinds else None
    hits = _query(user_id, query, k, _where({"type": "memory"}, kind_filter))
    out = []
    if hits is not None:
        for h in hits:
            mid = int(h["id"][1:])
            row = db.one("SELECT id,kind,text,importance FROM memories WHERE id=?", (mid,))
            if row and h["score"] > 0.35:
                out.append({"mid": mid, "kind": row["kind"], "text": row["text"], "score": h["score"]})
    else:  # Stichwort-Fallback
        words = _words(query)
        sql, args = "SELECT id,kind,text FROM memories WHERE user_id=?", [user_id]
        if kinds:
            sql += f" AND kind IN ({','.join('?' * len(kinds))})"
            args += list(kinds)
        for r in db.all(sql + " ORDER BY importance DESC, updated DESC", args):
            score = sum(w in r["text"].lower() for w in words) / max(len(words), 1)
            if score > 0 or r["text"].lower() == query.lower():
                out.append({"mid": r["id"], "kind": r["kind"], "text": r["text"], "score": round(score, 3)})
        out = sorted(out, key=lambda x: -x["score"])[:k]
    if expand and out:
        ids = {o["mid"] for o in out}
        for o in list(out[:4]):
            for ln in db.all("SELECT a,b,weight FROM memory_links WHERE a=? OR b=?", (o["mid"], o["mid"])):
                other = ln["b"] if ln["a"] == o["mid"] else ln["a"]
                if other not in ids:
                    r = db.one("SELECT id,kind,text FROM memories WHERE id=?", (other,))
                    if r:
                        ids.add(other)
                        out.append({"mid": other, "kind": r["kind"], "text": r["text"],
                                    "score": round(o["score"] * ln["weight"], 3), "linked": True})
    if touch and out:
        db.run(f"UPDATE memories SET uses=uses+1, last_used=? WHERE id IN ({','.join(str(o['mid']) for o in out)})",
               (db.now(),))
    return out


def by_kind(user_id, kind, limit=30):
    return db.all("SELECT id,kind,text,importance,updated FROM memories WHERE user_id=? AND kind=? "
                  "ORDER BY importance DESC, updated DESC LIMIT ?", (user_id, kind, limit))


def profile(user_id):
    s = db.all_settings(user_id)
    return {k: s.get(k, "") for k in PROFILE_KEYS}


# ------------------------------------------------------------------ Gesprächsgedächtnis
def index_message(user_id, chat_id, msg_id, role, text, title=""):
    if len(text or "") < 12:
        return
    t = db.now()
    _index(user_id, [f"c{msg_id}"], [f"{'Nutzer' if role == 'user' else 'Jarvis'}: {text[:1500]}"],
           [{"type": "conversation", "chat_id": chat_id, "ts": t, "title": title[:80], "role": role}])


def day_range(day: str):
    d = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=TZ)
    return d.timestamp(), (d + timedelta(days=1)).timestamp()


def resolve_day(word: str | None):
    if not word:
        return None
    w = word.lower().strip()
    today = datetime.now(TZ).date()
    rel = {"heute": 0, "today": 0, "bugün": 0, "gestern": 1, "yesterday": 1, "dün": 1, "vorgestern": 2}
    if w in rel:
        return (today - timedelta(days=rel[w])).isoformat()
    return w[:10]


def search_conversations(user_id, query, date_from=None, date_to=None, k=8):
    since = day_range(resolve_day(date_from))[0] if date_from else None
    until = day_range(resolve_day(date_to or date_from))[1] if (date_to or date_from) else None
    results = []
    ts_conds = [c for c in ({"ts": {"$gte": since}} if since else None, {"ts": {"$lt": until}} if until else None) if c]
    hits = _query(user_id, query, k, _where({"type": "conversation"}, *ts_conds))
    if hits is not None:
        for h in hits:
            m = h["meta"]
            results.append({"when": datetime.fromtimestamp(m["ts"], TZ).strftime("%d.%m.%Y %H:%M"),
                            "chat": m.get("title", ""), "text": h["text"], "score": h["score"]})
    if hits is None or not results:  # Stichwort-Fallback über alle Nachrichten
        words = _words(query)
        sql = ("SELECT m.content, m.role, m.created, c.title FROM messages m JOIN chats c ON c.id=m.chat_id "
               "WHERE c.user_id=?")
        args = [user_id]
        if since:
            sql += " AND m.created>=?"
            args.append(since)
        if until:
            sql += " AND m.created<?"
            args.append(until)
        rows = db.all(sql + " ORDER BY m.id DESC LIMIT 400", args)
        scored = [(sum(w in r["content"].lower() for w in words), r) for r in rows]
        for sc, r in sorted(scored, key=lambda x: -x[0])[:k]:
            if sc or since:
                results.append({"when": datetime.fromtimestamp(r["created"], TZ).strftime("%d.%m.%Y %H:%M"),
                                "chat": r["title"], "text": f"{'Nutzer' if r['role'] == 'user' else 'Jarvis'}: {r['content'][:600]}",
                                "score": sc})
    ep_sql, ep_args = "SELECT day,title,summary FROM episodes WHERE user_id=?", [user_id]
    if date_from:
        ep_sql += " AND day>=? AND day<=?"
        ep_args += [resolve_day(date_from), resolve_day(date_to or date_from)]
    episodes = db.all(ep_sql + " ORDER BY day DESC LIMIT 6", ep_args)
    return {"messages": results, "day_summaries": episodes}


def summarize_day(user_id, day=None):
    """Fasst jeden Chat eines Tages zusammen (Gesprächsgedächtnis). Läuft automatisch jeden Abend."""
    day = day or datetime.now(TZ).date().isoformat()
    start, end = day_range(day)
    chats = db.all("SELECT DISTINCT c.id, c.title FROM chats c JOIN messages m ON m.chat_id=c.id "
                   "WHERE c.user_id=? AND m.created>=? AND m.created<?", (user_id, start, end))
    for c in chats:
        msgs = db.all("SELECT role, content FROM messages WHERE chat_id=? AND created>=? AND created<? ORDER BY id",
                      (c["id"], start, end))
        if len(msgs) < 2:
            continue
        convo = "\n".join(f"{m['role']}: {m['content'][:800]}" for m in msgs)[-12000:]
        summary = llm.complete([{"role": "user", "content":
            "Fasse dieses Gespräch präzise auf Deutsch zusammen (max. 120 Wörter). Nenne konkret: Themen, "
            "Entscheidungen, Änderungen an Projekten, offene Aufgaben.\n\n" + convo}], settings.FAST_MODEL)
        db.run("INSERT INTO episodes(user_id,chat_id,day,title,summary,created) VALUES(?,?,?,?,?,?) "
               "ON CONFLICT(chat_id,day) DO UPDATE SET summary=excluded.summary, created=excluded.created",
               (user_id, c["id"], day, c["title"], summary, db.now()))
        add(user_id, f"[{day}] Gespräch „{c['title']}“: {summary}", "episode", 3, "tageszusammenfassung")


# ------------------------------------------------------------------ Wissens-/Dateigedächtnis
def add_knowledge(user_id, name, text, chunk_size=1200):
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size - 150)] or [""]
    doc_id = db.run("INSERT INTO knowledge_docs(user_id,name,chunks,created) VALUES(?,?,?,?)",
                    (user_id, name, len(chunks), db.now()))
    ids, metas = [], []
    for ch in chunks:
        cid = db.run("INSERT INTO knowledge_chunks(doc_id,user_id,text) VALUES(?,?,?)", (doc_id, user_id, ch))
        ids.append(f"k{cid}")
        metas.append({"type": "knowledge", "doc": name[:120], "doc_id": doc_id, "ts": db.now()})
    for i in range(0, len(ids), 32):
        _index(user_id, ids[i:i + 32], chunks[i:i + 32], metas[i:i + 32])
    return {"doc_id": doc_id, "chunks": len(chunks)}


def search_knowledge(user_id, query, k=5):
    hits = _query(user_id, query, k, {"type": "knowledge"})
    if hits is not None:
        return [{"doc": h["meta"]["doc"], "text": h["text"], "score": h["score"]} for h in hits]
    words = _words(query)
    rows = db.all("SELECT k.text, d.name FROM knowledge_chunks k JOIN knowledge_docs d ON d.id=k.doc_id WHERE k.user_id=?",
                  (user_id,))
    scored = sorted(((sum(w in r["text"].lower() for w in words), r) for r in rows), key=lambda x: -x[0])
    return [{"doc": r["name"], "text": r["text"], "score": s} for s, r in scored[:k] if s]


# ------------------------------------------------------------------ Kontext für jede Antwort
def build_context(user_id, query, chat_id=None):
    """Stellt zusammen, was Jarvis für diese Nachricht wissen muss. Gibt (Text, Statistik) zurück."""
    t0 = time.perf_counter()
    prof = profile(user_id)
    parts, stats = [], {}

    p = [f"{PROFILE_KEYS[k]}: {v}" for k, v in prof.items() if v]
    if p:
        parts.append("PROFIL DES NUTZERS:\n" + "\n".join(p))
    stats["profile_fields"] = len(p)
    rules = by_kind(user_id, "rule", 40)
    stats["rule"] = len(rules)
    if rules:
        parts.append("REGELN (immer strikt befolgen, haben Vorrang):\n" + "\n".join(f"- {r['text']}" for r in rules))
    for kind, title in (("preference", "VORLIEBEN"), ("goal", "ZIELE"), ("project", "PROJEKTE"), ("profile", "PERSÖNLICHES")):
        rows = by_kind(user_id, kind, 15)
        stats[kind] = len(rows)
        if rows:
            parts.append(f"{title}:\n" + "\n".join(f"- {r['text']}" for r in rows))

    rel = [m for m in search(user_id, query, k=8) if m["kind"] not in ALWAYS_LOADED]
    stats["relevant"] = len(rel)
    if rel:
        parts.append("RELEVANTE ERINNERUNGEN:\n" + "\n".join(
            f"- ({KINDS.get(m['kind'], m['kind'])}{', verknüpft' if m.get('linked') else ''}) {m['text']}" for m in rel))

    hits = _query(user_id, query, 4, {"type": "conversation"}) or []
    old = [h for h in hits if h["meta"].get("chat_id") != chat_id and h["score"] > 0.55]
    stats["conversations"] = len(old)
    if old:
        parts.append("AUS FRÜHEREN GESPRÄCHEN:\n" + "\n".join(
            f"- {datetime.fromtimestamp(h['meta']['ts'], TZ):%d.%m.%Y} „{h['meta'].get('title', '')}“: {h['text'][:300]}"
            for h in old))

    know = search_knowledge(user_id, query, 3)
    know = [k for k in know if isinstance(k["score"], int) or k["score"] > 0.5]
    stats["knowledge"] = len(know)
    if know:
        parts.append("AUS DEINER WISSENSDATENBANK:\n" + "\n".join(f"- [{k['doc']}] {k['text'][:500]}" for k in know))

    stats["ms"] = int((time.perf_counter() - t0) * 1000)
    stats["semantic"] = _semantic_ok
    return "\n\n".join(parts), stats


# ------------------------------------------------------------------ Selbstständiges Lernen
LEARN_PROMPT = """Analysiere die letzte Nachricht des Nutzers. Extrahiere NUR dauerhaft wichtige, neue Informationen über den Nutzer.
WICHTIG: Nur was der NUTZER selbst über sich sagt oder festlegt – nie etwas aus Jarvis' Antwort, keine Vermutungen, keine Platzhalter.
Kategorien (kind): profile (persönliche Fakten: Name, Wohnort, Beruf, Familie), preference (Vorlieben/Abneigungen),
rule (dauerhafte Anweisungen an Jarvis: "ab jetzt", "immer", "nie", "in Zukunft"), goal (Ziele), project (Projekte, an denen er arbeitet,
inkl. wichtiger Änderungen/Entscheidungen), fact (sonstige wichtige Fakten).
Gib JSON zurück: {"memories":[{"kind":"...","text":"kurzer, eigenständiger Satz in der dritten Person","importance":1-5}],
"settings":{"language":"de|tr|en (nur wenn der Nutzer eine Sprachregel festlegt)","anrede":"(nur wenn er sagt, wie er angesprochen werden will)","name":"(nur wenn genannt)"}}
Keine Smalltalk-Inhalte, keine Fragen, nichts Vorübergehendes. Wenn nichts Wichtiges: {"memories":[],"settings":{}}

Bereits bekannt (nicht wiederholen):
{known}

Nutzer: {user}
Jarvis: {assistant}"""


PERSONAL = re.compile(r"\b(ich|mein\w*|mir|mich|wir|unser\w*|i|my|me|i'm|im|we|our|ben|benim|bana|beni|biz|bizim|"
                      r"ab jetzt|immer|nie|niemals|in zukunft|nenn|always|never|from now on|call me|her zaman|asla|"
                      r"artık|bundan sonra)\b", re.I)


def _grounded(fact, source):
    """Schutz vor erfundenen Erinnerungen: der Inhalt muss sich in den Worten des Nutzers wiederfinden."""
    fw = [w for w in _words(fact) if len(w) > 3 and w not in ("nutzer", "nutzers", "jarvis", "möchte", "immer")]
    if len(fw) < 2:
        return False
    src = source.lower()
    return sum(w[:5] in src for w in fw) / len(fw) >= 0.4


ANREDE_RX = re.compile(r"(?:nenn(?:e|st)?\s+(?:du\s+)?mich(?:\s+bitte)?(?:\s+ab\s+jetzt)?|sprich\s+mich\s+(?:bitte\s+)?(?:mit|als)|"
                       r"call\s+me|bana)\s+[„\"']?([A-Za-zÄÖÜäöüßÇçĞğİıŞşÖö][\wÄÖÜäöüßÇçĞğİıŞş. -]{0,25}?)[“\"']?"
                       r"(?:\s+(?:an|de|diye|bitte|please))?(?:[.!,]|$|\s+(?:und|and|ve)\b)", re.I)
LANG_RX = [("de", re.compile(r"(nur|immer|ausschließlich)\s+(auf\s+)?deutsch|always\s+(in\s+)?german|hep\s+almanca", re.I)),
           ("tr", re.compile(r"(nur|immer)\s+(auf\s+)?türkisch|always\s+(in\s+)?turkish|(hep|her zaman|sadece)\s+türkçe", re.I)),
           ("en", re.compile(r"(nur|immer)\s+(auf\s+)?englisch|always\s+(in\s+)?english|only\s+english|(hep|sadece)\s+ingilizce", re.I))]


def learn_explicit(user_id, text):
    """Feste Regeln (ohne KI-Raten): Anrede und Sprache werden exakt so übernommen, wie du sie sagst."""
    out = []
    m = ANREDE_RX.search(text)
    if m:
        val = m.group(1).strip(" .")
        if val and val.lower() not in ("bitte", "ab", "jetzt"):
            db.set_setting(user_id, "anrede", val)
            add(user_id, f"Der Nutzer möchte mit „{val}“ angesprochen werden.", "rule", 5, "explizit")
            out.append({"kind": "setting", "text": f"Anrede = {val}"})
    for lang, rx in LANG_RX:
        if rx.search(text):
            db.set_setting(user_id, "language", lang)
            add(user_id, f"Jarvis antwortet dem Nutzer immer auf {['Deutsch', 'Türkisch', 'Englisch'][['de', 'tr', 'en'].index(lang)]}.",
                "rule", 5, "explizit")
            out.append({"kind": "setting", "text": f"Sprache = {lang}"})
    return out


def learn(user_id, user_text, assistant_text):
    if not settings.AUTO_LEARN or len(user_text) < 8 or not PERSONAL.search(user_text):
        return []
    explicit = learn_explicit(user_id, user_text)
    known = "\n".join(f"- {m['text']}" for m in search(user_id, user_text, k=6, expand=False, touch=False)) or "-"
    data = llm.complete_json(LEARN_PROMPT.replace("{known}", known).replace("{user}", user_text[:2000])
                             .replace("{assistant}", assistant_text[:800]))
    if not isinstance(data, dict):
        return explicit
    learned = list(explicit)
    for m in data.get("memories", [])[:5]:
        if isinstance(m, dict) and len(str(m.get("text", ""))) >= 12 and _grounded(m["text"], user_text):
            mid = add(user_id, m["text"], m.get("kind", "fact"), int(m.get("importance", 3) or 3), "auto")
            learned.append({"id": mid, "kind": m.get("kind"), "text": m["text"]})
    for key, val in (data.get("settings") or {}).items():
        if explicit and key in ("language", "anrede"):
            continue
        if key in ("language", "anrede", "name") and isinstance(val, str) and val.strip() and "(" not in val:
            if key == "language" and val not in ("de", "tr", "en"):
                continue
            db.set_setting(user_id, key, val.strip())
            learned.append({"kind": "setting", "text": f"{key} = {val}"})
    return learned


def reindex(user_id):
    """Baut den semantischen Index komplett neu auf (z.B. nach Modellwechsel)."""
    global _semantic_ok
    _semantic_ok = True
    rows = db.all("SELECT id,kind,text,updated FROM memories WHERE user_id=?", (user_id,))
    for i in range(0, len(rows), 32):
        b = rows[i:i + 32]
        _index(user_id, [f"m{r['id']}" for r in b], [r["text"] for r in b],
               [{"kind": r["kind"], "ts": r["updated"], "type": "memory"} for r in b])
    msgs = db.all("SELECT m.id, m.chat_id, m.role, m.content, m.created, c.title FROM messages m "
                  "JOIN chats c ON c.id=m.chat_id WHERE c.user_id=? AND length(m.content)>=12", (user_id,))
    for i in range(0, len(msgs), 32):
        b = msgs[i:i + 32]
        _index(user_id, [f"c{r['id']}" for r in b],
               [f"{'Nutzer' if r['role'] == 'user' else 'Jarvis'}: {r['content'][:1500]}" for r in b],
               [{"type": "conversation", "chat_id": r["chat_id"], "ts": r["created"], "title": r["title"][:80],
                 "role": r["role"]} for r in b])
    return {"memories": len(rows), "messages": len(msgs), "semantic": _semantic_ok}


def stats(user_id):
    rows = db.all("SELECT kind, COUNT(*) n FROM memories WHERE user_id=? GROUP BY kind", (user_id,))
    out = {r["kind"]: r["n"] for r in rows}
    out["links"] = db.one("SELECT COUNT(*) n FROM memory_links l JOIN memories m ON m.id=l.a WHERE m.user_id=?", (user_id,))["n"]
    out["episodes"] = db.one("SELECT COUNT(*) n FROM episodes WHERE user_id=?", (user_id,))["n"]
    out["documents"] = db.one("SELECT COUNT(*) n FROM knowledge_docs WHERE user_id=?", (user_id,))["n"]
    out["actions"] = db.one("SELECT COUNT(*) n FROM actions WHERE user_id=?", (user_id,))["n"]
    out["messages"] = db.one("SELECT COUNT(*) n FROM messages m JOIN chats c ON c.id=m.chat_id WHERE c.user_id=?", (user_id,))["n"]
    out["semantic"] = _semantic_ok
    return out
JARVIS_EOF
mkdir -p 'backend/engines'
cat > 'backend/engines/voice.py' <<'JARVIS_EOF'
"""VOICE ENGINE: Whisper (Sprache -> Text) + Piper / XTTS (Text -> Sprache). Alles lokal."""
import io
import json
import re
import tempfile
import threading
import wave

from core.config import settings

_whisper = None
_piper_cache = {}
_xtts = None
_lock = threading.Lock()
LANG_NAMES = {"de": "Deutsch", "tr": "Türkçe", "en": "English"}


def transcribe(path: str) -> dict:
    global _whisper
    with _lock:
        if _whisper is None:
            from faster_whisper import WhisperModel
            _whisper = WhisperModel(settings.WHISPER_MODEL, device=settings.WHISPER_DEVICE, compute_type="int8")
    segments, info = _whisper.transcribe(path, vad_filter=True, beam_size=5)
    return {"text": " ".join(s.text.strip() for s in segments).strip(), "language": info.language}


def list_voices():
    voices = []
    for onnx in sorted(settings.VOICES_DIR.glob("*.onnx")):
        meta_file = onnx.with_suffix(".onnx.json")
        lang, label = onnx.name[:2], onnx.stem.split("-")[1] if "-" in onnx.stem else onnx.stem
        if meta_file.exists():
            lang = json.loads(meta_file.read_text()).get("language", {}).get("family", lang)
        voices.append({"id": f"piper:{onnx.stem}", "name": f"{label.replace('_', ' ').title()} ({LANG_NAMES.get(lang, lang)})",
                       "lang": lang, "engine": "piper"})
    xdir = settings.VOICES_DIR / "xtts"
    if xdir.exists():
        for wav in sorted(xdir.glob("*.wav")):
            voices.append({"id": f"xtts:{wav.stem}", "name": f"{wav.stem.title()} (XTTS · DE/TR/EN)",
                           "lang": "multi", "engine": "xtts"})
    return voices


def detect_lang(text: str) -> str:
    t = text.lower()
    if re.search(r"[ğışİ]", text) or re.search(r"\b(ve|bir|bu|için|değil|evet|merhaba|nasıl)\b", t):
        return "tr"
    if re.search(r"[äöüß]", t) or re.search(r"\b(und|ich|nicht|der|die|das|ist|sie|ein)\b", t):
        return "de"
    return "en"


def clean_for_speech(text: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"```.*?```", " Code. ", text, flags=re.S)
    text = re.sub(r"[*_#`>|]", "", text)
    return re.sub(r"\s+", " ", text).strip()[:2500]


def pick_voice(text: str, prefs: dict) -> str:
    lang = detect_lang(text)
    wanted = prefs.get(f"voice_{lang}") or prefs.get("voice")
    voices = list_voices()
    if wanted in {v["id"] for v in voices}:
        return wanted
    for pref in (lambda v: v["lang"] == lang, lambda v: v["engine"] == "xtts", lambda v: True):
        for v in voices:
            if pref(v):
                return v["id"]
    raise RuntimeError("Keine Stimmen installiert. Starte: python setup_voices.py")


def synthesize(text: str, voice_id: str) -> bytes:
    text = clean_for_speech(text) or "."
    engine, name = voice_id.split(":", 1)
    return _xtts_tts(text, name) if engine == "xtts" else _piper_tts(text, name)


def _piper_tts(text, name):
    from piper import PiperVoice
    with _lock:
        if name not in _piper_cache:
            _piper_cache[name] = PiperVoice.load(str(settings.VOICES_DIR / f"{name}.onnx"))
    v = _piper_cache[name]
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        (v.synthesize_wav if hasattr(v, "synthesize_wav") else v.synthesize)(text, wf)
    return buf.getvalue()


def _xtts_tts(text, name):
    global _xtts
    with _lock:
        if _xtts is None:
            from TTS.api import TTS
            _xtts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        _xtts.tts_to_file(text=text, speaker_wav=str(settings.VOICES_DIR / "xtts" / f"{name}.wav"),
                          language=detect_lang(text), file_path=f.name)
        return open(f.name, "rb").read()


def synthesize_to_file(text, voice_id, path):
    with open(path, "wb") as f:
        f.write(synthesize(text, voice_id))
JARVIS_EOF
mkdir -p 'backend'
cat > 'backend/main.py' <<'JARVIS_EOF'
"""J.A.R.V.I.S. – zentrale Steuerung (API + Oberfläche). Start: python main.py"""
import asyncio
import json
import re
import tempfile
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core import db, llm, tools
from core.config import settings
from engines import memory, voice
# Agents registrieren ihre Werkzeuge beim Import
from agents import (computer_agent, media_agent, memory_agent, scheduler, security, services,  # noqa: F401
                    system_agent, task_agent, telegram_bot, web_agent)


@asynccontextmanager
async def lifespan(app):
    db.init()
    sched = scheduler.start()
    telegram_bot.start()
    yield
    sched.shutdown(wait=False)


app = FastAPI(title="J.A.R.V.I.S.", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
User = Depends(security.current_user)


@app.middleware("http")
async def guard(request: Request, call_next):
    ip = request.client.host if request.client else ""
    if not security.ip_allowed(ip):  # Security Agent: nur eigenes Netz
        db.log_security(ip, "fremdes_netz_blockiert", request.url.path)
        return JSONResponse({"detail": "Zugriff verweigert"}, status_code=403)
    resp = await call_next(request)
    resp.headers.update({"X-Frame-Options": "SAMEORIGIN", "X-Content-Type-Options": "nosniff",
                         "Referrer-Policy": "no-referrer", "Cache-Control": "no-store" if request.url.path.startswith("/api") else "no-cache"})
    return resp


# ================================================================== Login / Profil
class LoginIn(BaseModel):
    username: str
    password: str


@app.post("/api/login")
def login(body: LoginIn, request: Request):
    ip = request.client.host if request.client else "?"
    if not security.login_allowed(ip):
        raise HTTPException(429, "Zu viele Fehlversuche. Bitte 15 Minuten warten.")
    u = db.one("SELECT * FROM users WHERE username=?", (body.username.strip(),))
    if not u or not security.check_pw(body.password, u["pw_hash"]):
        security.note_fail(ip, body.username)
        raise HTTPException(401, "Benutzername oder Passwort falsch")
    db.log_security(ip, "login_ok", u["username"])
    return {"token": security.make_token(u), "username": u["username"]}


@app.get("/api/me")
def me(user=User):
    return {"username": user["username"], "settings": db.all_settings(user["id"]), "tools": tools.enabled_names(),
            "brain": llm.health(), "models": {"llm": settings.LLM_MODEL, "vision": settings.VISION_MODEL},
            "memory": memory.stats(user["id"])}


class PwIn(BaseModel):
    old: str
    new: str


@app.post("/api/password")
def change_password(body: PwIn, user=User):
    u = db.one("SELECT pw_hash FROM users WHERE id=?", (user["id"],))
    if not security.check_pw(body.old, u["pw_hash"]):
        raise HTTPException(400, "Altes Passwort falsch")
    if len(body.new) < 10:
        raise HTTPException(400, "Mindestens 10 Zeichen")
    security.change_password(user["id"], body.new)
    u = db.one("SELECT id, token_version FROM users WHERE id=?", (user["id"],))
    return {"ok": True, "token": security.make_token(u)}


SETTING_KEYS = {"language", "voice", "voice_de", "voice_tr", "voice_en", "autospeak", "clap", "speed",
                "name", "anrede", "about"}


@app.get("/api/settings")
def get_settings(user=User):
    return db.all_settings(user["id"])


@app.put("/api/settings")
def put_settings(body: dict, user=User):
    for k, v in body.items():
        if k in SETTING_KEYS:
            db.set_setting(user["id"], k, str(v)[:2000])
    return db.all_settings(user["id"])


# ================================================================== Chats
@app.get("/api/chats")
def list_chats(user=User):
    return db.all("SELECT id,title,updated FROM chats WHERE user_id=? ORDER BY updated DESC", (user["id"],))


@app.post("/api/chats")
def new_chat(user=User):
    return db.one("SELECT id,title,updated FROM chats WHERE id=?", (db.create_chat(user["id"]),))


def own_chat(cid, user):
    c = db.one("SELECT * FROM chats WHERE id=? AND user_id=?", (cid, user["id"]))
    if not c:
        raise HTTPException(404, "Chat nicht gefunden")
    return c


@app.patch("/api/chats/{cid}")
def rename_chat(cid: int, body: dict, user=User):
    own_chat(cid, user)
    db.run("UPDATE chats SET title=? WHERE id=?", (str(body.get("title", ""))[:80] or "Chat", cid))
    return {"ok": True}


@app.delete("/api/chats/{cid}")
def delete_chat(cid: int, user=User):
    own_chat(cid, user)
    db.run("DELETE FROM messages WHERE chat_id=?", (cid,))
    db.run("DELETE FROM chats WHERE id=?", (cid,))
    return {"ok": True}


@app.get("/api/chats/{cid}/messages")
def messages(cid: int, user=User):
    own_chat(cid, user)
    return db.all("SELECT id,role,content,has_images,created FROM messages WHERE chat_id=? ORDER BY id", (cid,))


@app.get("/api/search")
def search_chats(q: str, user=User):
    return db.all("SELECT m.chat_id, c.title, substr(m.content,1,160) AS snippet FROM messages m JOIN chats c ON c.id=m.chat_id "
                  "WHERE c.user_id=? AND m.content LIKE ? ORDER BY m.id DESC LIMIT 30", (user["id"], f"%{q}%"))


class SendIn(BaseModel):
    text: str = ""
    images: list[str] = []


@app.post("/api/chats/{cid}/send")
async def send(cid: int, body: SendIn, user=User):
    own_chat(cid, user)
    imgs = [re.sub(r"^data:[^,]+,", "", i) for i in body.images][:4]

    async def gen():
        async for ev in task_agent.run(user, cid, body.text.strip(), imgs):
            yield json.dumps(ev, ensure_ascii=False, default=str) + "\n"

    return StreamingResponse(gen(), media_type="application/x-ndjson")


# ================================================================== Aktionen (Vorschau & Bestätigung)
@app.get("/api/actions")
def list_actions(status: str | None = None, user=User):
    sql, args = "SELECT * FROM actions WHERE user_id=?", [user["id"]]
    if status:
        sql += " AND status=?"
        args.append(status)
    rows = db.all(sql + " ORDER BY id DESC LIMIT 100", args)
    for r in rows:
        if r["status"] == "pending":
            r["preview"] = tools.preview_text(r["tool"], json.loads(r["args"] or "{}"))
            r["label"] = (tools.info(r["tool"]) or {}).get("label", r["tool"])
    return rows


@app.post("/api/actions/{aid}/{decision}")
async def decide_action(aid: int, decision: str, user=User):
    if decision not in ("approve", "reject"):
        raise HTTPException(400)
    return await asyncio.to_thread(task_agent.approve, user, aid, decision == "approve")


# ================================================================== Gedächtnis
@app.get("/api/memories")
def list_memories(kind: str | None = None, q: str | None = None, user=User):
    if q:
        return memory.search(user["id"], q, k=30, kinds=[kind] if kind else None, touch=False)
    sql, args = "SELECT * FROM memories WHERE user_id=?", [user["id"]]
    if kind:
        sql += " AND kind=?"
        args.append(kind)
    return db.all(sql + " ORDER BY kind, importance DESC, updated DESC LIMIT 500", args)


class MemIn(BaseModel):
    text: str
    kind: str = "fact"
    importance: int = 3


@app.post("/api/memories")
def add_memory(body: MemIn, user=User):
    return {"id": memory.add(user["id"], body.text, body.kind, body.importance, "manuell")}


@app.put("/api/memories/{mid}")
def edit_memory(mid: int, body: MemIn, user=User):
    return {"ok": memory.update(user["id"], mid, body.text, body.kind, body.importance)}


@app.delete("/api/memories/{mid}")
def delete_memory(mid: int, user=User):
    memory.delete(user["id"], mid)
    return {"ok": True}


@app.get("/api/memory/graph")
def memory_graph(user=User):
    nodes = db.all("SELECT id,kind,text,importance FROM memories WHERE user_id=? ORDER BY importance DESC, updated DESC LIMIT 150",
                   (user["id"],))
    ids = {n["id"] for n in nodes}
    links = [ln for ln in db.all("SELECT a,b,weight FROM memory_links") if ln["a"] in ids and ln["b"] in ids]
    return {"nodes": nodes, "links": links, "stats": memory.stats(user["id"])}


@app.get("/api/memory/episodes")
def episodes(user=User):
    return db.all("SELECT * FROM episodes WHERE user_id=? ORDER BY day DESC LIMIT 60", (user["id"],))


@app.post("/api/memory/reindex")
async def reindex(user=User):
    return await asyncio.to_thread(memory.reindex, user["id"])


@app.post("/api/knowledge/upload")
async def upload_knowledge(file: UploadFile = File(...), user=User):
    data = await file.read()
    name = file.filename or "Dokument"
    if name.lower().endswith(".pdf"):
        import io
        from pypdf import PdfReader
        text = "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(data)).pages)
    else:
        text = data.decode("utf-8", errors="ignore")
    if not text.strip():
        raise HTTPException(400, "Kein Text gefunden")
    res = await asyncio.to_thread(memory.add_knowledge, user["id"], name, text)
    return {"name": name, **res}


@app.get("/api/knowledge")
def knowledge(user=User):
    return db.all("SELECT * FROM knowledge_docs WHERE user_id=? ORDER BY id DESC", (user["id"],))


# ================================================================== Kalender / Benachrichtigungen
@app.get("/api/events")
def events(days: int = 7, user=User):
    start = datetime.now(services.TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    return [{**e, "start": e["start"].isoformat()} for e in services.events_between(user["id"], start, start + timedelta(days=min(days, 60)))]


@app.get("/api/notifications")
def notifications(user=User):
    return db.all("SELECT * FROM notifications WHERE user_id=? AND seen=0 ORDER BY id", (user["id"],))


@app.post("/api/notifications/{nid}/seen")
def seen(nid: int, user=User):
    db.run("UPDATE notifications SET seen=1 WHERE id=? AND user_id=?", (nid, user["id"]))
    return {"ok": True}


@app.post("/api/briefing/run")
async def run_briefing(user=User):
    return await asyncio.to_thread(scheduler.build_briefing, user)


# ================================================================== System
@app.get("/api/diagnose")
async def diagnose(user=User):
    return await asyncio.to_thread(system_agent.diagnose, user["id"])


@app.get("/api/security/log")
def security_log(user=User):
    return db.all("SELECT * FROM security_log ORDER BY id DESC LIMIT 100")


# ================================================================== Sprache
@app.post("/api/stt")
async def stt(audio: UploadFile = File(...), user=User):
    suffix = "." + (audio.filename or "a.webm").rsplit(".", 1)[-1][:5]
    with tempfile.NamedTemporaryFile(suffix=suffix) as f:
        f.write(await audio.read())
        f.flush()
        return await asyncio.to_thread(voice.transcribe, f.name)


@app.get("/api/voices")
def voices(user=User):
    return voice.list_voices()


class TtsIn(BaseModel):
    text: str
    voice: str | None = None


@app.post("/api/tts")
async def tts(body: TtsIn, user=User):
    try:
        vid = body.voice or voice.pick_voice(body.text, db.all_settings(user["id"]))
        wav = await asyncio.to_thread(voice.synthesize, body.text, vid)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"Sprachausgabe fehlgeschlagen: {e}")
    return Response(wav, media_type="audio/wav")


# ================================================================== Dateien (Bilder, Videos, Screenshots)
@app.get("/api/files/{name}")
def files(name: str, user=User):
    if not re.fullmatch(r"[a-f0-9]{32}\.(png|jpg|mp4)", name):
        raise HTTPException(404)
    path = settings.FILES_DIR / name
    if not path.exists():
        raise HTTPException(404)
    return FileResponse(path)


app.mount("/", StaticFiles(directory=settings.FRONTEND_DIR, html=True), name="ui")


if __name__ == "__main__":
    import uvicorn

    cert, key = settings.CERT_DIR / "cert.pem", settings.CERT_DIR / "key.pem"
    ssl = {"ssl_certfile": str(cert), "ssl_keyfile": str(key)} if cert.exists() and key.exists() else {}
    print(f"\n  J.A.R.V.I.S. online →  {'https' if ssl else 'http'}://localhost:{settings.PORT}\n")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, **ssl)
JARVIS_EOF
mkdir -p 'backend'
cat > 'backend/requirements-extra.txt' <<'JARVIS_EOF'
# Optional – groß (mehrere GB). Nur installieren, wenn gewünscht:
#   pip install -r requirements-extra.txt
# Bilder erstellen (lokal):
torch
diffusers>=0.30
transformers
accelerate
# Echte, sehr natürliche Stimmen in DE/TR/EN (XTTS-v2, lokal):
coqui-tts
JARVIS_EOF
mkdir -p 'backend'
cat > 'backend/requirements.txt' <<'JARVIS_EOF'
# Kern
fastapi>=0.115
uvicorn[standard]>=0.30
python-multipart>=0.0.9
python-dotenv>=1.0
httpx>=0.27
pydantic>=2.7
apscheduler>=3.10,<4
# Sicherheit
bcrypt>=4.1
PyJWT>=2.8
# Gedächtnis (semantisch)
chromadb>=0.5
# Sprache
faster-whisper>=1.0
piper-tts>=1.3
# Web-Agent
playwright>=1.45
beautifulsoup4>=4.12
# Computer-Agent & Bilder
pyautogui>=0.9.54
pillow>=10
pypdf>=4
# Kalender & Dienste
icalendar>=5.0
recurring-ical-events>=2.2
spotipy>=2.24
# Steuerfenster
streamlit>=1.36
pandas>=2
JARVIS_EOF
mkdir -p 'backend'
cat > 'backend/setup_voices.py' <<'JARVIS_EOF'
"""Lädt die Piper-Stimmen EINMALIG herunter. Danach läuft alles offline."""
import sys
import urllib.request

from core.config import settings

BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main"

# Weibliche Stimmen (Piper hat aktuell keine weibliche türkische Stimme -> dafür XTTS, siehe README)
VOICES = [
    "de_DE-kerstin-low",
    "de_DE-eva_k-x_low",
    "de_DE-ramona-low",
    "en_GB-jenny_dioco-medium",
    "en_GB-alba-medium",
    "en_US-amy-medium",
    "en_US-lessac-high",
    "en_US-hfc_female-medium",
    "tr_TR-dfki-medium",  # Türkisch (Ersatz, bis XTTS eingerichtet ist)
]


def url_for(v):
    lang, name, quality = v.split("-")
    return f"{BASE}/{lang[:2]}/{lang}/{name}/{quality}/{v}.onnx"


for v in VOICES:
    for ext in (".onnx", ".onnx.json"):
        target = settings.VOICES_DIR / f"{v}{ext}"
        if target.exists():
            continue
        print(f"↓ {v}{ext}")
        try:
            urllib.request.urlretrieve(url_for(v) + ext[5:], target)
        except Exception as e:  # noqa: BLE001
            print(f"  übersprungen: {e}", file=sys.stderr)
print(f"Fertig. Stimmen liegen in {settings.VOICES_DIR}")
JARVIS_EOF
mkdir -p 'backend'
cat > 'backend/spotify_auth.py' <<'JARVIS_EOF'
"""Einmalig ausführen: verbindet Spotify (öffnet Browser zum Bestätigen)."""
from agents.services import spotify_client

print("Spotify verbunden als:", spotify_client().current_user()["display_name"])
JARVIS_EOF
cat > 'docker-compose.yml' <<'JARVIS_EOF'
# Lokale, private Websuche. Ollama läuft auf dem Mac nativ (wegen GPU/Metal).
services:
  searxng:
    image: searxng/searxng:latest
    container_name: jarvis-searxng
    ports:
      - "127.0.0.1:8888:8080"
    volumes:
      - ./searxng:/etc/searxng
    restart: unless-stopped
JARVIS_EOF
mkdir -p 'frontend'
cat > 'frontend/app.js' <<'JARVIS_EOF'
/* J.A.R.V.I.S. – HUD-Dashboard (Desktop, mehrere Bildschirme, Handy-App) */
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const POPOUT = new URLSearchParams(location.search).get("panel");
const bus = "BroadcastChannel" in window ? new BroadcastChannel("jarvis") : null;
const S = {
  token: localStorage.getItem("jarvis_token"), chatId: null, chats: [], settings: {}, voices: [],
  pendingImages: [], busy: false, audioCtx: null, micStream: null, recording: null, clapOn: false, speaking: null,
  run: null, memKind: "", tab: "map",
};
const KINDS = { profile: "Persönlich", preference: "Vorliebe", rule: "Regel", fact: "Fakt", goal: "Ziel", project: "Projekt", knowledge: "Wissen", episode: "Gespräch" };

/* =========================================================== API */
async function api(path, opts = {}) {
  const headers = opts.headers || {};
  if (S.token) headers.Authorization = "Bearer " + S.token;
  if (opts.json !== undefined) { headers["Content-Type"] = "application/json"; opts.body = JSON.stringify(opts.json); }
  const r = await fetch(path, { ...opts, headers });
  if (r.status === 401 && path !== "/api/login") { logout(); throw new Error("Abgemeldet"); }
  if (!r.ok) { let m = r.statusText; try { m = (await r.json()).detail || m; } catch {} throw new Error(m); }
  return r;
}
const getJSON = async (p, o) => (await api(p, o)).json();
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fileUrl = (src) => `${src}?token=${encodeURIComponent(S.token)}`;

/* =========================================================== Login */
$("#loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  $("#loginErr").textContent = "";
  try {
    const d = await getJSON("/api/login", { method: "POST", json: { username: $("#lu").value, password: $("#lp").value } });
    S.token = d.token; localStorage.setItem("jarvis_token", d.token); $("#lp").value = "";
    ensureAudio(); boot();
  } catch (err) { $("#loginErr").textContent = err.message; }
});
function logout() {
  S.token = null; localStorage.removeItem("jarvis_token");
  $("#app").classList.add("hidden"); $("#login").classList.remove("hidden");
}

async function boot() {
  let me;
  try { me = await getJSON("/api/me"); } catch { return; }
  S.settings = me.settings || {};
  $("#login").classList.add("hidden"); $("#app").classList.remove("hidden");
  setPill("#brain", me.brain.ok, me.brain.ok ? "GEHIRN ONLINE" : "GEHIRN OFFLINE", me.brain.ok ? me.brain.models.join(", ") : me.brain.error);
  updateMemPill(me.memory);
  initGlobe();
  if (POPOUT) return initPopout();
  S.voices = await getJSON("/api/voices").catch(() => []);
  await loadChats();
  S.chats.length ? openChat(S.chats[0].id) : newChat();
  if (S.settings.clap === "true") toggleClap(true);
  pollNotifications(); setInterval(pollNotifications, 30000);
  loadActions();
  if (!S.settings.anrede && !S.settings.name) setTimeout(() => toast("👋 Tipp: Unter ⚙ Einstellungen kannst du festlegen, wie Jarvis dich ansprechen soll."), 1500);
}
function setPill(sel, ok, text, title) { const b = $(sel); b.textContent = text; b.className = "pill " + (ok ? "ok" : "bad"); b.title = title || ""; }
function updateMemPill(m) {
  if (!m) return;
  const n = Object.entries(m).filter(([k]) => KINDS[k]).reduce((a, [, v]) => a + v, 0);
  setPill("#memPill", true, `GEDÄCHTNIS ${n}${m.semantic ? " · SEM" : ""}`, `${n} Erinnerungen, ${m.links} Verknüpfungen, ${m.messages} Nachrichten`);
}

/* =========================================================== Chats */
async function loadChats() { S.chats = await getJSON("/api/chats"); renderChatList(S.chats); }
function renderChatList(list) {
  const ul = $("#chatList"); ul.innerHTML = "";
  for (const c of list) {
    const id = c.id || c.chat_id;
    const li = document.createElement("li");
    li.className = id === S.chatId ? "active" : "";
    li.innerHTML = `<span class="t"></span><span class="x" title="Löschen">✕</span>`;
    $(".t", li).textContent = c.snippet ? `${c.title} — ${c.snippet}` : c.title;
    li.onclick = () => { openChat(id); $("#sidebar").classList.remove("open"); };
    li.ondblclick = async () => { const t = prompt("Chat umbenennen:", c.title); if (t) { await api(`/api/chats/${id}`, { method: "PATCH", json: { title: t } }); loadChats(); } };
    $(".x", li).onclick = async (ev) => {
      ev.stopPropagation();
      if (!confirm(`Chat „${c.title}“ löschen?`)) return;
      await api(`/api/chats/${id}`, { method: "DELETE" }); await loadChats();
      if (S.chatId === id) S.chats.length ? openChat(S.chats[0].id) : newChat();
    };
    ul.appendChild(li);
  }
}
let searchT;
$("#chatSearch").addEventListener("input", (e) => {
  clearTimeout(searchT);
  const q = e.target.value.trim();
  searchT = setTimeout(async () => {
    if (!q) return renderChatList(S.chats);
    const seen = new Set();
    renderChatList((await getJSON("/api/search?q=" + encodeURIComponent(q))).filter((h) => !seen.has(h.chat_id) && seen.add(h.chat_id)));
  }, 250);
});
async function newChat() { const c = await getJSON("/api/chats", { method: "POST" }); await loadChats(); openChat(c.id); }
$("#newChat").onclick = newChat;
async function openChat(id) {
  S.chatId = id; renderChatList(S.chats);
  const msgs = await getJSON(`/api/chats/${id}/messages`);
  $("#messages").innerHTML = "";
  msgs.forEach((m) => addMessage(m.role, m.content, m.has_images ? "🖼 Bild" : ""));
  updateLayout();
}

/* =========================================================== Markdown & Nachrichten */
function md(text) {
  let h = esc(text || "");
  h = h.replace(/```(\w*)\n?([\s\S]*?)```/g, (_, l, c) => `<pre><code>${c}</code></pre>`);
  h = h.replace(/!\[([^\]]*)\]\((\/api\/files\/[a-f0-9]{32}\.(png|jpg|mp4))\)/g, (_, alt, src, ext) =>
    ext === "mp4" ? `<video controls playsinline src="${fileUrl(src)}"></video>` : `<img alt="${alt}" src="${fileUrl(src)}">`);
  h = h.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
  h = h.replace(/(^|\s)(https?:\/\/[^\s<]+)/g, '$1<a href="$2" target="_blank" rel="noopener noreferrer">$2</a>');
  h = h.replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
  h = h.replace(/^#{1,4} (.*)$/gm, "<b>$1</b>");
  return h.replace(/\n/g, "<br>");
}
function addMessage(role, content, extra = "") {
  const el = document.createElement("div");
  el.className = "msg " + role;
  el.innerHTML = `<div class="tools"></div><div class="body"></div><div class="meta"></div>`;
  $(".body", el).innerHTML = (extra ? `<small>${esc(extra)}</small><br>` : "") + md(content);
  if (role === "assistant") addActs(el, () => content);
  $("#messages").appendChild(el); scrollDown();
  return el;
}
function addActs(el, getText) {
  $(".acts", el)?.remove();
  const a = document.createElement("div"); a.className = "acts";
  a.innerHTML = `<button title="Vorlesen">🔊</button><button title="Kopieren">📋</button>`;
  a.children[0].onclick = () => speak(getText());
  a.children[1].onclick = () => navigator.clipboard?.writeText(getText());
  el.appendChild(a);
}
const scrollDown = () => { const m = $("#messages"); m.scrollTop = m.scrollHeight; };
const updateLayout = () => $("#app").classList.toggle("has-messages", $("#messages").children.length > 0);
function setCore(state, label) {
  $("#core").className = "core " + state;
  $("#coreLabel").textContent = label || { idle: "BEREIT", listening: "HÖRE ZU", thinking: "VERARBEITE", speaking: "SPRECHE" }[state];
}

/* =========================================================== Senden & Live-Events */
async function send(text) {
  text = (text || "").trim();
  if ((!text && !S.pendingImages.length) || S.busy) return;
  S.busy = true; stopSpeaking();
  const images = S.pendingImages.splice(0); renderAttachments();
  addMessage("user", text, images.length ? `🖼 ${images.length} Bild(er)` : "");
  $("#input").value = ""; autoGrow(); updateLayout();
  const el = addMessage("assistant", "");
  const body = $(".body", el), toolsEl = $(".tools", el);
  body.classList.add("cursor"); setCore("thinking");
  let full = "", spoken = false, finished = false;
  handleEvent({ type: "start", text });
  try {
    const r = await api(`/api/chats/${S.chatId}/send`, { method: "POST", json: { text, images } });
    const reader = r.body.getReader(), dec = new TextDecoder();
    let buf = "";
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      let i;
      while ((i = buf.indexOf("\n")) >= 0) {
        const line = buf.slice(0, i).trim(); buf = buf.slice(i + 1);
        if (!line) continue;
        const ev = JSON.parse(line);
        handleEvent(ev);
        if (ev.type === "token") { full += ev.text; body.innerHTML = md(full); scrollDown(); }
        else if (ev.type === "tool") toolsEl.textContent += `⚙ ${ev.name}  `;
        else if (ev.type === "step" && ev.status === "active" && !finished) setCore("thinking", ev.label.toUpperCase());
        else if (ev.type === "error") { full += "\n" + ev.text; body.innerHTML = md(full); }
        else if (ev.type === "done") {
          finished = true; full = ev.text; body.innerHTML = md(full); body.classList.remove("cursor");
          $(".meta", el).textContent = `${(ev.total_ms / 1000).toFixed(1)} s`;
          addActs(el, () => full); setCore("idle");
          if (S.settings.autospeak !== "false") { speak(full); spoken = true; }
        } else if (ev.type === "learned") {
          const n = document.createElement("div"); n.className = "learned";
          n.textContent = "🧠 Gelernt: " + ev.items.map((x) => x.text).join(" · ");
          $("#messages").appendChild(n); scrollDown(); refreshMemPill();
        }
      }
    }
  } catch (e) { full += `\n⚠ ${e.message}`; body.innerHTML = md(full); }
  body.classList.remove("cursor"); S.busy = false;
  if (!spoken) setCore("idle");
  loadChats();
}
$("#composer").addEventListener("submit", (e) => { e.preventDefault(); send($("#input").value); });
$("#input").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && !matchMedia("(max-width: 820px)").matches) { e.preventDefault(); send($("#input").value); }
});
function autoGrow() { const t = $("#input"); t.style.height = "auto"; t.style.height = Math.min(t.scrollHeight, 160) + "px"; }
$("#input").addEventListener("input", autoGrow);
const refreshMemPill = () => getJSON("/api/me").then((m) => updateMemPill(m.memory)).catch(() => {});

/* Alle Events gehen an die HUD-Panels – auch an Pop-out-Fenster auf anderen Bildschirmen */
function handleEvent(ev, fromBus = false) {
  if (!fromBus && bus) bus.postMessage(ev);
  logConsole(ev);
  if (ev.type === "start") resetProcess(ev.text);
  else if (ev.type === "step") updateProcess(ev);
  else if (ev.type === "ui") showWidget(ev);
  else if (ev.type === "confirm") { loadActions(); switchTab("actions"); toast(`⚡ Bestätigung nötig: ${ev.label}`, () => switchTab("actions")); }
  else if (ev.type === "done") finishProcess(ev.total_ms);
}
bus && (bus.onmessage = (m) => handleEvent(m.data, true));

/* =========================================================== Prozess-Visualisierung */
const PIPE = [
  { id: "input", label: "Eingabe", ico: "◉", kinds: ["input"] },
  { id: "memory", label: "Gedächtnis", ico: "🧠", kinds: ["memory"] },
  { id: "llm", label: "Gehirn", ico: "✦", kinds: ["llm", "task"] },
  { id: "agents", label: "Agents", ico: "⚙", kinds: ["computer", "web", "dateien", "medien", "kalender", "mail", "musik", "telegram", "anzeige", "erinnerung", "automatisierung", "system", "?"] },
  { id: "output", label: "Antwort", ico: "➤", kinds: ["output"] },
  { id: "learn", label: "Lernen", ico: "∞", kinds: [] },
];
function drawPipeline() {
  const svg = $("#pipeline");
  const w = 360, gap = w / PIPE.length;
  let h = "";
  PIPE.forEach((n, i) => { if (i) h += `<path class="edge" id="e-${n.id}" d="M${gap * (i - 1) + gap / 2 + 15},36 L${gap * i + gap / 2 - 15},36"/>`; });
  PIPE.forEach((n, i) => {
    const x = gap * i + gap / 2;
    h += `<g class="node" id="n-${n.id}"><circle cx="${x}" cy="36" r="15"/><text class="ico" x="${x}" y="41">${n.ico}</text>
      <text class="t" x="${x}" y="66">${n.label}</text><text class="m" id="m-${n.id}" x="${x}" y="80"></text></g>`;
  });
  svg.innerHTML = h;
}
function pipeFor(ev) {
  if (ev.id === "learn") return "learn";
  if (ev.id === "answer") return "output";
  return (PIPE.find((p) => p.kinds.includes(ev.kind)) || PIPE[3]).id;
}
function resetProcess(text) {
  S.run = { steps: {}, order: [], plan: null, planDone: 0, started: performance.now(), done: false };
  drawPipeline(); $("#timeline").innerHTML = "";
  $("#procBar").style.width = "0%"; $("#procPct").textContent = "0%"; $("#procTime").textContent = "0 ms";
  clearInterval(S.runTimer);
  S.runTimer = setInterval(() => { if (S.run && !S.run.done) $("#procTime").textContent = fmtMs(performance.now() - S.run.started); }, 100);
}
const fmtMs = (ms) => ms >= 1000 ? (ms / 1000).toFixed(2) + " s" : Math.round(ms) + " ms";
function updateProcess(ev) {
  if (!S.run) resetProcess("");
  const R = S.run;
  let li = R.steps[ev.id];
  if (!li) {
    li = document.createElement("li");
    li.innerHTML = `<span class="tl"></span><span class="tm"></span><span class="td"></span>`;
    $("#timeline").appendChild(li); R.steps[ev.id] = li; R.order.push(ev.id);
  }
  li.className = ev.status;
  $(".tl", li).textContent = `${ev.label}${ev.kind && !["core", "input", "llm", "output", "memory"].includes(ev.kind) ? " · " + ev.kind : ""}`;
  $(".tm", li).textContent = ev.ms != null ? fmtMs(ev.ms) : ev.status === "waiting" ? "⏸" : "…";
  $(".td", li).textContent = ev.detail || "";
  li.scrollIntoView({ block: "nearest" });
  // Pipeline-Knoten
  const pid = pipeFor(ev), node = $("#n-" + pid);
  if (node) {
    node.setAttribute("class", "node " + (ev.status === "waiting" ? "active" : ev.status));
    const prev = PIPE[PIPE.findIndex((p) => p.id === pid)];
    $("#e-" + prev.id)?.setAttribute("class", "edge on");
    if (ev.ms != null) $("#m-" + pid).textContent = fmtMs(ev.ms);
  }
  if (ev.id.startsWith("tool") && ev.status === "done" && R.plan) { R.planDone++; renderPlan(); }
  // Fortschritt
  const total = Math.max(R.order.length + (R.done ? 0 : 1), R.plan ? R.plan.steps.length + 4 : 0);
  const done = R.order.filter((id) => ["done", "error"].includes(R.steps[id].className)).length;
  const pct = R.done ? 100 : Math.min(99, Math.round((done / total) * 100));
  $("#procBar").style.width = pct + "%"; $("#procPct").textContent = pct + "%";
}
function renderPlan() {
  const R = S.run; if (!R?.plan) return;
  let box = $("#planBox");
  if (!box) { box = document.createElement("li"); box.id = "planBox"; box.className = "done"; $("#timeline").appendChild(box); }
  box.innerHTML = `<span class="tl">📋 Plan: ${esc(R.plan.goal)}</span><span class="tm">${R.planDone}/${R.plan.steps.length}</span>
    <ol class="plan">${R.plan.steps.map((s, i) => `<li class="${i < R.planDone ? "ok" : ""}">${i < R.planDone ? "✓ " : ""}${esc(s)}</li>`).join("")}</ol>`;
}
function finishProcess(total) {
  if (!S.run) return;
  S.run.done = true;
  $("#procBar").style.width = "100%"; $("#procPct").textContent = "100%";
  if (total != null) $("#procTime").textContent = fmtMs(total);
  $$("#pipeline .edge").forEach((e) => e.setAttribute("class", "edge"));
}

/* =========================================================== Widgets: Fenster, Karte, Bilder */
function showWidget(ev) {
  if (ev.widget === "map") { switchTab("map"); flyTo(ev.lat, ev.lon, ev.label, ev.zoom); return; }
  if (ev.widget === "plan") { if (S.run) { S.run.plan = { goal: ev.goal, steps: ev.steps || [] }; S.run.planDone = 0; renderPlan(); } return; }
  if (ev.widget === "memory") { refreshMemPill(); if (S.tab === "memory") renderMemory(); return; }
  addWindow(ev);
}
function addWindow(ev) {
  const box = $("#windows");
  if ($("p.muted", box)) box.innerHTML = "";
  const w = document.createElement("div");
  w.className = "win " + (ev.kind || "");
  let content = "";
  if (ev.widget === "image") content = `<img src="${fileUrl(ev.src)}" alt="">${ev.text ? `<div class="muted">${md(ev.text.slice(0, 600))}</div>` : ""}`;
  else if (ev.widget === "video") content = `<video controls playsinline src="${fileUrl(ev.src)}"></video>`;
  else content = ev.kind === "code" ? `<pre>${esc(ev.text)}</pre>` : md(ev.text || "");
  w.innerHTML = `<div class="wh"><span>${esc(ev.title || "Info")}</span><span><small>${new Date().toLocaleTimeString("de-DE")}</small> <button title="Schließen">✕</button></span></div>${content}`;
  $(".wh button", w).onclick = () => { w.remove(); countWindows(); };
  box.prepend(w); countWindows();
  if (S.tab !== "windows") switchTab("windows");
}
const countWindows = () => { const n = $$("#windows .win").length; $("#winCount").textContent = n ? n : ""; };

/* Weltkugel (offline, d3) */
let G = null;
async function initGlobe() {
  if (G || !window.d3 || !window.topojson) { if (!window.d3) $("#globe").innerHTML = `<p class="muted">Karte nicht installiert – ./install.sh erneut ausführen.</p>`; return; }
  const el = $("#globe"); const size = () => Math.max(220, Math.min(el.clientWidth || 380, el.clientHeight || 380));
  let world;
  try { world = await (await fetch("vendor/countries-110m.json")).json(); } catch { el.innerHTML = `<p class="muted">Kartendaten fehlen.</p>`; return; }
  const svg = d3.select(el).append("svg");
  const proj = d3.geoOrthographic().clipAngle(90).precision(0.5);
  const path = d3.geoPath(proj);
  const land = topojson.feature(world, world.objects.countries);
  svg.append("path").datum({ type: "Sphere" }).attr("class", "sphere");
  svg.append("path").datum(d3.geoGraticule10()).attr("class", "grat");
  svg.append("g").selectAll("path").data(land.features).join("path").attr("class", "land");
  const mk = svg.append("g").style("display", "none");
  mk.append("circle").attr("class", "ping").attr("r", 4); mk.append("circle").attr("class", "marker").attr("r", 3.5);
  G = { svg, proj, path, mk, rot: [-10, -30, 0], base: 1, k: 1, target: null, auto: true };
  const redraw = () => {
    const s = size();
    svg.attr("viewBox", `0 0 ${s} ${s}`);
    proj.translate([s / 2, s / 2]).scale((s / 2 - 6) * G.k).rotate(G.rot);
    svg.selectAll("path").attr("d", path);
    if (G.target) {
      const p = proj([G.target[0], G.target[1]]);
      const visible = d3.geoDistance([G.target[0], G.target[1]], [-G.rot[0], -G.rot[1]]) < Math.PI / 2;
      mk.style("display", visible ? null : "none").attr("transform", `translate(${p[0]},${p[1]})`);
    }
  };
  G.redraw = redraw;
  d3.timer(() => { if (G.auto) { G.rot[0] += 0.12; redraw(); } });
  new ResizeObserver(redraw).observe(el);
  svg.call(d3.drag().on("start", () => (G.auto = false)).on("drag", (e) => { G.rot[0] += e.dx * 0.35; G.rot[1] = Math.max(-90, Math.min(90, G.rot[1] - e.dy * 0.35)); redraw(); }));
  svg.on("wheel", (e) => { e.preventDefault(); G.k = Math.max(0.8, Math.min(12, G.k * (e.deltaY < 0 ? 1.15 : 0.87))); redraw(); });
  redraw();
}
function flyTo(lat, lon, label, zoom = 3) {
  if (!G) return;
  G.auto = false; G.target = [lon, lat];
  $("#mapLabel").textContent = `◎ ${label}  ${lat.toFixed(2)}°, ${lon.toFixed(2)}°`;
  const r0 = [...G.rot], r1 = [-lon, -lat, 0], k0 = G.k, k1 = Math.max(1, Math.min(10, zoom / 1.5));
  const ir = d3.interpolate(r0, r1);
  d3.transition().duration(1800).ease(d3.easeCubicInOut).tween("fly", () => (t) => {
    G.rot = ir(t);
    G.k = t < 0.5 ? k0 + (1 - k0) * t * 2 : 1 + (k1 - 1) * (t - 0.5) * 2;
    G.redraw();
  });
}

/* =========================================================== Tabs & Pop-out */
function switchTab(tab) {
  S.tab = tab;
  $$(".tabs button[data-tab]").forEach((b) => b.classList.toggle("on", b.dataset.tab === tab));
  $$(".tab-body").forEach((b) => b.classList.toggle("hidden", b.dataset.body !== tab));
  if (tab === "memory") renderMemory();
  if (tab === "system") renderSystem();
  if (tab === "actions") loadActions();
  if (tab === "map") G?.redraw();
}
$$(".tabs button[data-tab]").forEach((b) => (b.onclick = () => switchTab(b.dataset.tab)));
const popout = (panel) => window.open(`/?panel=${panel}`, "jarvis_" + panel, "width=720,height=820");
$("#popTab").onclick = () => popout(S.tab);
$$(".pop[data-pop]").forEach((b) => (b.onclick = () => popout(b.dataset.pop)));
function initPopout() {
  document.body.classList.add("popout");
  document.title = "J.A.R.V.I.S. · " + POPOUT;
  if (POPOUT === "process") { $(".hud-panel.grow").classList.add("hidden"); drawPipeline(); }
  else { $('[data-panel="process"]').classList.add("hidden"); switchTab(POPOUT); }
}
$("#hudBtn").onclick = () => $("#hud").classList.toggle("open");
$("#menuBtn").onclick = () => $("#sidebar").classList.toggle("open");

/* =========================================================== Konsole (technische Ansicht) */
function logConsole(ev) {
  const c = $("#console"); if (!c) return;
  const t = new Date().toLocaleTimeString("de-DE");
  let cls = "", line;
  if (ev.type === "token") return;
  if (ev.type === "step") { cls = ev.status === "error" ? "err" : ev.status === "done" ? "ok" : ""; line = `step  ${ev.id.padEnd(8)} ${ev.status.padEnd(7)} ${ev.ms != null ? fmtMs(ev.ms) : ""}  ${ev.detail || ""}`; }
  else if (ev.type === "tool") { cls = "tool"; line = `call  ${ev.name}(${JSON.stringify(ev.args)})`; }
  else if (ev.type === "ui") { cls = "ui"; line = `ui    ${ev.widget} ${ev.title || ev.label || ""}`; }
  else if (ev.type === "confirm") { cls = "tool"; line = `wait  #${ev.action_id} ${ev.tool} → Bestätigung`; }
  else if (ev.type === "error") { cls = "err"; line = `error ${ev.text}`; }
  else if (ev.type === "done") { cls = "ok"; line = `done  ${fmtMs(ev.total_ms)} · ${ev.text.length} Zeichen`; }
  else if (ev.type === "start") line = `\n▶ ${ev.text}`;
  else line = `${ev.type} ${JSON.stringify(ev).slice(0, 200)}`;
  const span = document.createElement("span"); span.className = cls; span.textContent = `[${t}] ${line}\n`;
  c.appendChild(span);
  while (c.childNodes.length > 600) c.firstChild.remove();
  c.parentElement.scrollTop = c.parentElement.scrollHeight;
}

/* =========================================================== Aktionen (Vorschau & Bestätigung) */
async function loadActions() {
  let rows = [];
  try { rows = await getJSON("/api/actions"); } catch { return; }
  const pending = rows.filter((r) => r.status === "pending");
  $("#actCount").textContent = pending.length || "";
  const box = $("#actions");
  box.innerHTML = pending.length ? "" : `<p class="muted">Keine offenen Aktionen. Riskante Schritte (Tippen, Klicken, Befehle, Dateien schreiben) erscheinen hier mit Vorschau.</p>`;
  for (const a of pending) {
    const d = document.createElement("div"); d.className = "act";
    d.innerHTML = `<b>⚡ ${esc(a.label)}</b> <small class="muted">#${a.id}</small><pre>${esc(a.preview)}</pre>
      <div class="btns"><button class="btn ok small">✔ Ausführen</button><button class="btn danger small">✖ Ablehnen</button></div>`;
    const [ok, no] = $$(".btn", d);
    ok.onclick = () => decide(a.id, true, d); no.onclick = () => decide(a.id, false, d);
    box.appendChild(d);
  }
  const hist = rows.filter((r) => r.status !== "pending").slice(0, 25);
  if (hist.length) box.insertAdjacentHTML("beforeend", `<div class="label" style="margin:12px 0 6px">AKTIONSGEDÄCHTNIS</div>` +
    hist.map((r) => `<div class="check"><span>${r.status === "done" || r.status === "approved" ? "✅" : r.status === "rejected" ? "✖" : "❌"} ${esc(r.tool)}</span><small>${r.duration_ms != null ? fmtMs(r.duration_ms) + " · " : ""}${new Date(r.created * 1000).toLocaleString("de-DE")}</small></div>`).join(""));
}
async function decide(id, ok, el) {
  $$(".btn", el).forEach((b) => (b.disabled = true));
  try {
    const r = await getJSON(`/api/actions/${id}/${ok ? "approve" : "reject"}`, { method: "POST" });
    if (r.ui) showWidget({ type: "ui", ...r.ui });
    if (r.message) addMessage("assistant", r.message);
    toast(ok ? `✔ Ausgeführt${r.ms != null ? " in " + fmtMs(r.ms) : ""}` : "✖ Abgelehnt");
  } catch (e) { toast("⚠ " + e.message); }
  loadActions();
}

/* =========================================================== Gedächtnis-Ansicht */
async function renderMemory() {
  const v = $("#memoryView");
  const q = $("#memQ")?.value || "";
  const url = `/api/memories?${S.memKind ? "kind=" + S.memKind + "&" : ""}${q ? "q=" + encodeURIComponent(q) : ""}`;
  const [rows, graph] = await Promise.all([getJSON(url), getJSON("/api/memory/graph")]);
  const st = graph.stats;
  v.innerHTML = `
    <div class="stat-grid">
      <div class="stat"><b>${Object.entries(st).filter(([k]) => KINDS[k]).reduce((a, [, n]) => a + n, 0)}</b><span>Erinnerungen</span></div>
      <div class="stat"><b>${st.links}</b><span>Verknüpfungen</span></div>
      <div class="stat"><b>${st.messages}</b><span>Nachrichten</span></div>
      <div class="stat"><b>${st.episodes}</b><span>Gesprächs-Tage</span></div>
      <div class="stat"><b>${st.documents}</b><span>Dokumente</span></div>
      <div class="stat"><b>${st.actions}</b><span>Aktionen</span></div>
    </div>
    <svg class="mem-graph" id="memGraph"></svg>
    <div class="chips">${["", ...Object.keys(KINDS)].map((k) => `<button class="chip ${S.memKind === k ? "on" : ""}" data-k="${k}">${k ? KINDS[k] : "Alle"}</button>`).join("")}</div>
    <input id="memQ" class="f" placeholder="Semantisch suchen…" value="${esc(q)}">
    <form id="memAdd" style="display:flex;gap:6px;margin:8px 0">
      <select class="f" style="width:auto" id="memKindSel">${Object.entries(KINDS).filter(([k]) => !["episode", "knowledge"].includes(k)).map(([k, n]) => `<option value="${k}">${n}</option>`).join("")}</select>
      <input class="f" id="memText" placeholder="Neue Erinnerung / Regel…"><button class="btn small">＋</button></form>
    <div>${rows.map((m) => `<div class="mem-row"><span class="kind ${m.kind}">${KINDS[m.kind] || m.kind}</span><span>${esc(m.text)}${m.score != null ? ` <small class="muted">${m.linked ? "↔ " : ""}${m.score}</small>` : ""}</span><button class="pop" data-del="${m.id ?? m.mid}">✕</button></div>`).join("") || `<p class="muted">Noch nichts gespeichert. Sag z.B. „Merk dir: Ich arbeite an einer App namens Nova.“</p>`}</div>`;
  $$(".chip", v).forEach((c) => (c.onclick = () => { S.memKind = c.dataset.k; renderMemory(); }));
  let t; $("#memQ").oninput = () => { clearTimeout(t); t = setTimeout(renderMemory, 400); };
  $("#memAdd").onsubmit = async (e) => { e.preventDefault(); if (!$("#memText").value.trim()) return; await api("/api/memories", { method: "POST", json: { text: $("#memText").value, kind: $("#memKindSel").value } }); renderMemory(); refreshMemPill(); };
  $$("[data-del]", v).forEach((b) => (b.onclick = async () => { await api(`/api/memories/${b.dataset.del}`, { method: "DELETE" }); renderMemory(); }));
  drawMemGraph(graph);
}
function drawMemGraph({ nodes, links }) {
  const svg = $("#memGraph"); if (!svg || !nodes.length) return svg && (svg.style.display = "none");
  const W = 380, H = 220, cx = W / 2, cy = H / 2;
  const col = { rule: "#ff4d5e", goal: "#4dffb0", project: "#ffb547", preference: "#b48cff", profile: "#8cecff", episode: "#6f9db3", fact: "#3fd8ff", knowledge: "#d6f5ff" };
  const kinds = Object.keys(KINDS);
  const pos = {};
  nodes.forEach((n, i) => {
    const ki = kinds.indexOf(n.kind), a = (ki / kinds.length) * Math.PI * 2 + (i % 7) * 0.12, r = 40 + (i % 5) * 16;
    pos[n.id] = [cx + Math.cos(a) * r * 1.6, cy + Math.sin(a) * r * 0.85];
  });
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.innerHTML = links.map((l) => pos[l.a] && pos[l.b] ? `<line x1="${pos[l.a][0]}" y1="${pos[l.a][1]}" x2="${pos[l.b][0]}" y2="${pos[l.b][1]}" stroke-width="${0.5 + l.weight}"/>` : "").join("") +
    nodes.map((n) => `<circle cx="${pos[n.id][0]}" cy="${pos[n.id][1]}" r="${2.5 + n.importance}" fill="${col[n.kind] || "#3fd8ff"}"><title>${esc(KINDS[n.kind])}: ${esc(n.text)}</title></circle>`).join("");
}

/* =========================================================== System / Selbstdiagnose */
async function renderSystem() {
  const v = $("#systemView");
  v.innerHTML = `<p class="muted">Diagnose läuft…</p>`;
  const d = await getJSON("/api/diagnose");
  const sec = await getJSON("/api/security/log").catch(() => []);
  v.innerHTML = `<div class="ph"><span class="label">SELBSTDIAGNOSE</span><span class="pct">${d.ok}/${d.total}</span><span class="ms">Laufzeit ${Math.round(d.uptime_s / 60)} min</span></div>
    ${d.checks.map((c) => `<div class="check"><span>${c.ok ? "✅" : "❌"} ${esc(c.name)}</span><small>${esc(c.detail)}</small></div>`).join("")}
    <div style="display:flex;gap:6px;margin:10px 0"><button class="btn small" id="reindex">🧠 Gedächtnis neu indexieren</button><button class="btn small" id="rediag">↻ Erneut prüfen</button></div>
    ${d.recent_errors.length ? `<div class="label">LETZTE FEHLER</div>${d.recent_errors.map((e) => `<div class="check"><span>❌ ${esc(e.tool)}</span><small>${esc(e.result.slice(0, 90))}</small></div>`).join("")}` : ""}
    <div class="label" style="margin-top:10px">SICHERHEITSPROTOKOLL</div>
    ${sec.slice(0, 20).map((s) => `<div class="check"><span>${s.event.includes("ok") ? "🔓" : "🛡"} ${esc(s.event)}</span><small>${esc(s.ip)} · ${new Date(s.ts * 1000).toLocaleString("de-DE")}</small></div>`).join("") || `<p class="muted">Keine Einträge.</p>`}`;
  $("#reindex").onclick = async () => { toast("🧠 Indexiere…"); const r = await getJSON("/api/memory/reindex", { method: "POST" }); toast(`🧠 ${r.memories} Erinnerungen, ${r.messages} Nachrichten indexiert${r.semantic ? "" : " (Stichwortmodus)"}`); };
  $("#rediag").onclick = renderSystem;
}

/* =========================================================== Bilder & Dokumente */
$("#fileInput").addEventListener("change", async (e) => {
  for (const f of [...e.target.files].slice(0, 4)) S.pendingImages.push(await resizeImage(f));
  e.target.value = ""; renderAttachments();
});
function resizeImage(file, max = 1280) {
  return new Promise((res) => {
    const img = new Image();
    img.onload = () => {
      const k = Math.min(1, max / Math.max(img.width, img.height)), c = document.createElement("canvas");
      c.width = img.width * k; c.height = img.height * k;
      c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
      res(c.toDataURL("image/jpeg", 0.88)); URL.revokeObjectURL(img.src);
    };
    img.src = URL.createObjectURL(file);
  });
}
function renderAttachments() {
  const p = $("#attachPreview"); p.innerHTML = "";
  S.pendingImages.forEach((src, i) => { const im = document.createElement("img"); im.src = src; im.title = "Entfernen"; im.onclick = () => { S.pendingImages.splice(i, 1); renderAttachments(); }; p.appendChild(im); });
}
$("#docInput").addEventListener("change", async (e) => {
  const f = e.target.files[0]; e.target.value = ""; if (!f) return;
  const fd = new FormData(); fd.append("file", f);
  toast(`📄 Lerne „${f.name}“…`);
  try { const r = await getJSON("/api/knowledge/upload", { method: "POST", body: fd }); toast(`📄 „${r.name}“ gespeichert (${r.chunks} Abschnitte). Frag mich dazu!`); refreshMemPill(); }
  catch (err) { toast("⚠ " + err.message); }
});

/* =========================================================== Stimme */
function ensureAudio() {
  if (!S.audioCtx) S.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  if (S.audioCtx.state === "suspended") S.audioCtx.resume();
  return S.audioCtx;
}
function stopSpeaking() { if (S.speaking) { try { S.speaking.stop(); } catch {} S.speaking = null; } }
async function speak(text) {
  if (!text || !text.trim()) return;
  stopSpeaking();
  try {
    const r = await api("/api/tts", { method: "POST", json: { text } });
    const ctx = ensureAudio(), buf = await ctx.decodeAudioData(await r.arrayBuffer());
    const src = ctx.createBufferSource(); src.buffer = buf; src.playbackRate.value = parseFloat(S.settings.speed || "1");
    const an = ctx.createAnalyser(); an.fftSize = 256; src.connect(an); an.connect(ctx.destination);
    S.speaking = src; setCore("speaking");
    const data = new Uint8Array(an.frequencyBinCount), glow = $(".glow"), inner = $(".inner");
    (function anim() {
      if (S.speaking !== src) return;
      an.getByteFrequencyData(data);
      const lvl = data.reduce((a, b) => a + b, 0) / data.length / 255;
      glow.style.transform = `scale(${1 + lvl * 1.8})`; inner.style.transform = `scale(${1 + lvl * 0.6})`;
      requestAnimationFrame(anim);
    })();
    src.onended = () => { if (S.speaking === src) S.speaking = null; glow.style.transform = inner.style.transform = ""; if (!S.busy && !S.recording) setCore("idle"); };
    src.start();
  } catch (e) { console.warn("TTS:", e); if (!S.busy) setCore("idle"); }
}

/* =========================================================== Mikrofon + Whisper */
async function getMic() {
  if (!S.micStream) {
    if (!navigator.mediaDevices?.getUserMedia) throw new Error("Mikrofon braucht HTTPS (siehe README).");
    S.micStream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
  }
  return S.micStream;
}
async function startRecording() {
  if (S.recording || S.busy) return;
  stopSpeaking();
  const ctx = ensureAudio();
  let stream; try { stream = await getMic(); } catch (e) { return toast("⚠ " + e.message); }
  const mime = MediaRecorder.isTypeSupported("audio/webm") ? "audio/webm" : "audio/mp4";
  const rec = new MediaRecorder(stream, { mimeType: mime }), chunks = [];
  rec.ondataavailable = (e) => e.data.size && chunks.push(e.data);
  S.recording = rec; $("#micBtn").classList.add("rec"); setCore("listening");
  const srcNode = ctx.createMediaStreamSource(stream), an = ctx.createAnalyser(); an.fftSize = 1024; srcNode.connect(an);
  const data = new Float32Array(an.fftSize), t0 = performance.now();
  let lastVoice = t0, spoke = false;
  (function vad() {
    if (S.recording !== rec) return;
    an.getFloatTimeDomainData(data);
    const rms = Math.sqrt(data.reduce((a, v) => a + v * v, 0) / data.length), now = performance.now();
    if (rms > 0.02) { lastVoice = now; spoke = true; }
    $(".glow").style.transform = `scale(${1 + Math.min(rms * 12, 1.5)})`;
    if ((spoke && now - lastVoice > 1300) || (!spoke && now - t0 > 7000) || now - t0 > 30000) return stopRecording();
    requestAnimationFrame(vad);
  })();
  rec.onstop = async () => {
    srcNode.disconnect(); $(".glow").style.transform = ""; $("#micBtn").classList.remove("rec"); S.recording = null;
    if (!spoke) return setCore("idle");
    setCore("thinking", "WHISPER");
    const fd = new FormData(); fd.append("audio", new Blob(chunks, { type: mime }), mime.includes("webm") ? "a.webm" : "a.m4a");
    try { const d = await getJSON("/api/stt", { method: "POST", body: fd }); d.text ? send(d.text) : setCore("idle"); }
    catch (e) { setCore("idle"); toast("⚠ Spracherkennung: " + e.message); }
  };
  rec.start();
}
function stopRecording() { if (S.recording && S.recording.state !== "inactive") S.recording.stop(); }
$("#micBtn").onclick = () => (S.recording ? stopRecording() : startRecording());

/* Klatsch-Erkennung: 2× klatschen → zuhören */
async function toggleClap(force) {
  S.clapOn = force ?? !S.clapOn;
  $("#clapBtn").classList.toggle("on", S.clapOn);
  api("/api/settings", { method: "PUT", json: { clap: String(S.clapOn) } }).catch(() => {});
  if (!S.clapOn) return;
  const ctx = ensureAudio();
  let stream; try { stream = await getMic(); } catch (e) { toast("⚠ " + e.message); return toggleClap(false); }
  const an = ctx.createAnalyser(); an.fftSize = 512; ctx.createMediaStreamSource(stream).connect(an);
  const data = new Float32Array(an.fftSize);
  let avg = 0.01, lastClap = 0, claps = [];
  (function loop() {
    if (!S.clapOn) return;
    an.getFloatTimeDomainData(data);
    let peak = 0, sum = 0;
    for (const v of data) { const a = Math.abs(v); if (a > peak) peak = a; sum += v * v; }
    const rms = Math.sqrt(sum / data.length), now = performance.now();
    if (!S.recording && !S.speaking && !S.busy && peak > 0.45 && peak > avg * 8 && now - lastClap > 120) {
      lastClap = now; claps = claps.filter((t) => now - t < 900); claps.push(now);
      if (claps.length >= 2 && claps[1] - claps[0] > 150) { claps = []; setTimeout(startRecording, 250); }
    }
    avg = avg * 0.97 + rms * 0.03;
    requestAnimationFrame(loop);
  })();
}
$("#clapBtn").onclick = () => { ensureAudio(); toggleClap(); };

/* =========================================================== Benachrichtigungen & Briefing */
function toast(text, onclick) {
  const t = document.createElement("div"); t.className = "toast"; t.textContent = text;
  t.onclick = () => { t.remove(); onclick?.(); };
  $("#toasts").appendChild(t); setTimeout(() => t.remove(), 9000);
}
async function pollNotifications() {
  let list = []; try { list = await getJSON("/api/notifications"); } catch { return; }
  for (const n of list) {
    await api(`/api/notifications/${n.id}/seen`, { method: "POST" });
    const short = n.text.length > 140 ? n.text.slice(0, 140) + "…" : n.text;
    toast(short, async () => { if (n.chat_id) { await loadChats(); openChat(n.chat_id); } });
    if (["briefing", "reminder"].includes(n.kind)) speak(n.text);
  }
  if (list.length) loadChats();
}
$("#runBriefing").onclick = async () => {
  setCore("thinking", "BRIEFING");
  try { const b = await getJSON("/api/briefing/run", { method: "POST" }); await api(`/api/notifications/${b.id}/seen`, { method: "POST" }); await loadChats(); openChat(b.chat_id); speak(b.content); }
  catch (e) { toast("⚠ " + e.message); }
  setCore("idle");
};

/* =========================================================== Modals: Einstellungen, Kalender */
function modal(title, html) { $("#modalTitle").textContent = title; $("#modalBody").innerHTML = html; $("#modal").classList.remove("hidden"); }
$("#modalClose").onclick = () => $("#modal").classList.add("hidden");
$("#modal").onclick = (e) => { if (e.target.id === "modal") $("#modal").classList.add("hidden"); };
const voiceSelect = (key, lang) => `<select class="f" data-k="${key}"><option value="">Automatisch</option>${S.voices.filter((v) => v.lang === lang || v.lang === "multi").map((v) => `<option value="${v.id}" ${S.settings[key] === v.id ? "selected" : ""}>${esc(v.name)}</option>`).join("")}</select>`;

$("#settingsBtn").onclick = () => {
  const s = S.settings;
  modal("EINSTELLUNGEN · PERSÖNLICHKEITSPROFIL", `
    <div class="field">Dein Name <input class="f" data-k="name" value="${esc(s.name || "")}" placeholder="z.B. Alex"></div>
    <div class="field">So soll Jarvis dich ansprechen <input class="f" data-k="anrede" value="${esc(s.anrede || "")}" placeholder="z.B. Boss, Chef, Abla, Sir"></div>
    <div class="field">Über mich (Beruf, Ziele, Stil…) <textarea class="f" data-k="about" rows="3">${esc(s.about || "")}</textarea></div>
    <div class="field">Sprache von Jarvis
      <select class="f" data-k="language">${[["auto", "Automatisch (wie ich schreibe)"], ["de", "Immer Deutsch"], ["tr", "Her zaman Türkçe"], ["en", "Always English"]].map(([v, n]) => `<option value="${v}" ${(s.language || "auto") === v ? "selected" : ""}>${n}</option>`).join("")}</select></div>
    <div class="field">Stimme Deutsch ${voiceSelect("voice_de", "de")}</div>
    <div class="field">Stimme Türkisch ${voiceSelect("voice_tr", "tr")}</div>
    <div class="field">Stimme Englisch ${voiceSelect("voice_en", "en")}</div>
    <div class="field"><button class="btn" id="testVoice">🔊 Stimme testen</button></div>
    <div class="field">Sprechtempo <select class="f" data-k="speed">${["0.9", "1", "1.1", "1.25"].map((v) => `<option ${(s.speed || "1") === v ? "selected" : ""}>${v}</option>`).join("")}</select></div>
    <label class="field toggle"><input type="checkbox" id="autospeak" ${s.autospeak !== "false" ? "checked" : ""}> Antworten automatisch vorlesen</label>
    <hr style="border-color:var(--line)">
    <div class="field">Passwort ändern (meldet alle Geräte ab)
      <input class="f" type="password" id="pwOld" placeholder="Altes Passwort" autocomplete="current-password">
      <input class="f" type="password" id="pwNew" placeholder="Neues Passwort (min. 10 Zeichen)" autocomplete="new-password">
      <button class="btn" id="pwSave">Passwort speichern</button></div>
    <button class="btn danger" id="logoutBtn">Abmelden</button>`);
  $$("#modalBody [data-k]").forEach((el) => (el.onchange = async () => { S.settings = await getJSON("/api/settings", { method: "PUT", json: { [el.dataset.k]: el.value } }); }));
  $("#autospeak").onchange = async (e) => { S.settings = await getJSON("/api/settings", { method: "PUT", json: { autospeak: String(e.target.checked) } }); };
  $("#testVoice").onclick = () => speak({ tr: "Merhaba, ben Jarvis. Size nasıl yardımcı olabilirim?", en: "Good evening. Jarvis at your service.", de: "Guten Abend. Jarvis steht zu Diensten." }[S.settings.language] || "Guten Abend. Jarvis steht zu Diensten.");
  $("#pwSave").onclick = async () => {
    try { const r = await getJSON("/api/password", { method: "POST", json: { old: $("#pwOld").value, new: $("#pwNew").value } }); S.token = r.token; localStorage.setItem("jarvis_token", r.token); toast("🔐 Passwort geändert."); }
    catch (e) { toast("⚠ " + e.message); }
  };
  $("#logoutBtn").onclick = () => { $("#modal").classList.add("hidden"); logout(); };
};
$('[data-open="calendar"]').onclick = async () => {
  const evs = await getJSON("/api/events?days=14");
  const fmt = (iso) => new Date(iso).toLocaleString("de-DE", { weekday: "short", day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
  modal("KALENDER · 14 TAGE", (evs.map((e) => `<div class="list-row"><span>${fmt(e.start)}</span><span>${esc(e.title)}${e.location ? " · " + esc(e.location) : ""}</span></div>`).join("") || "<p>Keine Termine.</p>") +
    `<p class="label" style="margin-top:14px">Sag z.B.: „Trag morgen um 15 Uhr Zahnarzt ein.“</p>`);
};

/* =========================================================== HUD-Details */
(function ticks() {
  const g = $(".ticks");
  for (let i = 0; i < 60; i++) {
    const a = (i / 60) * Math.PI * 2, r1 = i % 5 ? 96 : 92, r2 = 99;
    const l = document.createElementNS("http://www.w3.org/2000/svg", "line");
    l.setAttribute("x1", 100 + r1 * Math.cos(a)); l.setAttribute("y1", 100 + r1 * Math.sin(a));
    l.setAttribute("x2", 100 + r2 * Math.cos(a)); l.setAttribute("y2", 100 + r2 * Math.sin(a));
    g.appendChild(l);
  }
})();
setInterval(() => { $("#clock").textContent = new Date().toLocaleTimeString("de-DE"); }, 1000);
drawPipeline();
document.addEventListener("keydown", (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "j") { e.preventDefault(); S.recording ? stopRecording() : startRecording(); }
  if (e.key === "Escape") { stopSpeaking(); stopRecording(); }
});
if ("serviceWorker" in navigator && !POPOUT) navigator.serviceWorker.register("sw.js").catch(() => {});
if (S.token) boot();
JARVIS_EOF
mkdir -p 'frontend'
cat > 'frontend/icon.svg' <<'JARVIS_EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <radialGradient id="g" cx="50%" cy="50%" r="50%">
      <stop offset="0" stop-color="#e8fbff"/>
      <stop offset=".35" stop-color="#3fd8ff"/>
      <stop offset="1" stop-color="#3fd8ff" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="512" height="512" rx="112" fill="#02060c"/>
  <circle cx="256" cy="256" r="190" fill="none" stroke="#3fd8ff" stroke-width="6" stroke-dasharray="4 14" opacity=".6"/>
  <circle cx="256" cy="256" r="150" fill="none" stroke="#3fd8ff" stroke-width="16" stroke-dasharray="180 50 30 50" opacity=".85"/>
  <circle cx="256" cy="256" r="108" fill="none" stroke="#8cecff" stroke-width="5" stroke-dasharray="300 120"/>
  <circle cx="256" cy="256" r="80" fill="url(#g)"/>
</svg>
JARVIS_EOF
mkdir -p 'frontend'
cat > 'frontend/index.html' <<'JARVIS_EOF'
<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#02060c">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <title>J.A.R.V.I.S.</title>
  <link rel="manifest" href="manifest.json">
  <link rel="icon" href="icon.svg">
  <link rel="apple-touch-icon" href="icon.svg">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="grid-bg"></div>
  <div class="scanline"></div>

  <!-- ===================== LOGIN ===================== -->
  <section id="login" class="login">
    <form id="loginForm" class="panel login-box">
      <div class="mini-core"><span></span><span></span><span></span></div>
      <h1>J.A.R.V.I.S.</h1>
      <p class="sub">Sicherer Zugang · nur Besitzer · lokal &amp; privat</p>
      <input id="lu" autocomplete="username" placeholder="Benutzername" required>
      <input id="lp" type="password" autocomplete="current-password" placeholder="Passwort" required>
      <button class="btn primary" type="submit">Identität bestätigen</button>
      <p id="loginErr" class="err"></p>
    </form>
  </section>

  <!-- ===================== APP ===================== -->
  <div id="app" class="app hidden">
    <!-- Protokolle -->
    <aside id="sidebar" class="sidebar panel">
      <div class="side-head"><span class="label">PROTOKOLLE</span><button id="newChat" class="icon-btn sm" title="Neuer Chat">＋</button></div>
      <input id="chatSearch" class="search" placeholder="Chats durchsuchen…">
      <ul id="chatList" class="chat-list"></ul>
      <div class="side-foot">
        <button class="btn ghost" data-open="calendar">📅 Kalender</button>
        <button class="btn ghost" id="runBriefing">☀ Morgenbriefing</button>
        <label class="btn ghost">📄 Wissen hochladen<input id="docInput" type="file" accept=".txt,.md,.pdf,.csv,.json,.py,.js,.html" hidden></label>
      </div>
    </aside>

    <!-- Zentrale -->
    <main class="main">
      <header class="topbar">
        <button id="menuBtn" class="icon-btn sm mobile-only">☰</button>
        <div class="brand">J.A.R.V.I.S.<small id="status">ALLE SYSTEME BEREIT</small></div>
        <div class="hud-stats">
          <span id="clock">--:--</span>
          <span id="brain" class="pill">GEHIRN …</span>
          <span id="memPill" class="pill">GEDÄCHTNIS …</span>
        </div>
        <button id="hudBtn" class="icon-btn sm mobile-only" title="HUD">◎</button>
        <button id="settingsBtn" class="icon-btn sm" title="Einstellungen">⚙</button>
      </header>

      <div class="stage">
        <div id="core" class="core idle">
          <svg viewBox="0 0 200 200">
            <circle class="r r1" cx="100" cy="100" r="92"/><circle class="r r2" cx="100" cy="100" r="80"/>
            <circle class="r r3" cx="100" cy="100" r="66"/><circle class="r r4" cx="100" cy="100" r="52"/>
            <g class="ticks"></g>
            <circle class="glow" cx="100" cy="100" r="34"/><circle class="inner" cx="100" cy="100" r="22"/>
          </svg>
          <div id="coreLabel" class="core-label">BEREIT</div>
        </div>
      </div>

      <div id="messages" class="messages"></div>

      <form id="composer" class="composer panel">
        <div id="attachPreview" class="attach-preview"></div>
        <div class="row">
          <label class="icon-btn" title="Bild anhängen">🖼<input id="fileInput" type="file" accept="image/*" multiple hidden></label>
          <textarea id="input" rows="1" placeholder="Sprich mit Jarvis… / Jarvis'le konuş… / Talk to Jarvis…"></textarea>
          <button type="button" id="clapBtn" class="icon-btn" title="Klatsch-Erkennung (2× klatschen)">👏</button>
          <button type="button" id="micBtn" class="icon-btn mic" title="Sprechen (Cmd/Strg + J)">🎙</button>
          <button type="submit" class="icon-btn send" title="Senden">➤</button>
        </div>
      </form>
    </main>

    <!-- HUD: Prozess + Fenster -->
    <aside id="hud" class="hud">
      <section class="panel hud-panel" data-panel="process">
        <div class="ph"><span class="label">PROZESS</span><span id="procPct" class="pct">0%</span><span id="procTime" class="ms">0 ms</span><button class="pop" data-pop="process" title="In eigenem Fenster">⧉</button></div>
        <div class="progress"><div id="procBar"></div></div>
        <svg id="pipeline" viewBox="0 0 360 92"></svg>
        <ol id="timeline" class="timeline"></ol>
      </section>

      <section class="panel hud-panel grow">
        <nav class="tabs">
          <button data-tab="map" class="on">🌍 Karte</button>
          <button data-tab="windows">🗔 Fenster <b id="winCount"></b></button>
          <button data-tab="actions">⚡ Aktionen <b id="actCount"></b></button>
          <button data-tab="console">⌨ Konsole</button>
          <button data-tab="memory">🧠 Gedächtnis</button>
          <button data-tab="system">🩺 System</button>
          <button class="pop" id="popTab" title="Aktuellen Tab in eigenem Fenster">⧉</button>
        </nav>
        <div class="tab-body" data-body="map"><div id="globe" class="globe"></div><div id="mapLabel" class="map-label"></div></div>
        <div class="tab-body hidden" data-body="windows"><div id="windows" class="windows"><p class="muted">Info-Fenster erscheinen hier, wenn Jarvis etwas anzeigt.</p></div></div>
        <div class="tab-body hidden" data-body="actions"><div id="actions" class="actions-list"></div></div>
        <div class="tab-body hidden" data-body="console"><pre id="console" class="console"></pre></div>
        <div class="tab-body hidden" data-body="memory"><div id="memoryView"></div></div>
        <div class="tab-body hidden" data-body="system"><div id="systemView"></div></div>
      </section>
    </aside>
  </div>

  <div id="toasts" class="toasts"></div>

  <div id="modal" class="modal hidden">
    <div class="panel modal-box">
      <div class="modal-head"><span id="modalTitle" class="label"></span><button id="modalClose" class="icon-btn sm">✕</button></div>
      <div id="modalBody"></div>
    </div>
  </div>

  <script src="vendor/d3.min.js"></script>
  <script src="vendor/topojson-client.min.js"></script>
  <script src="app.js"></script>
</body>
</html>
JARVIS_EOF
mkdir -p 'frontend'
cat > 'frontend/manifest.json' <<'JARVIS_EOF'
{
  "name": "J.A.R.V.I.S.",
  "short_name": "Jarvis",
  "description": "Privater, lokaler KI-Assistent",
  "start_url": "/",
  "display": "standalone",
  "orientation": "portrait",
  "background_color": "#02060c",
  "theme_color": "#02060c",
  "icons": [
    { "src": "icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable" }
  ]
}
JARVIS_EOF
mkdir -p 'frontend'
cat > 'frontend/style.css' <<'JARVIS_EOF'
:root {
  --bg: #02060c;
  --panel: rgba(8, 24, 40, .55);
  --line: rgba(64, 210, 255, .26);
  --cyan: #3fd8ff;
  --cyan-2: #8cecff;
  --amber: #ffb547;
  --red: #ff4d5e;
  --green: #4dffb0;
  --violet: #b48cff;
  --text: #d6f5ff;
  --muted: #6f9db3;
  --font: "SF Pro Display", "Segoe UI", system-ui, -apple-system, Roboto, sans-serif;
  --mono: "SF Mono", ui-monospace, Menlo, Consolas, monospace;
  --accent: var(--cyan);
}
* { box-sizing: border-box; }
html, body { margin: 0; height: 100%; background: var(--bg); color: var(--text); font-family: var(--font); overflow: hidden; }
.hidden { display: none !important; }
.muted { color: var(--muted); font-size: 13px; }
button, input, textarea, select { font: inherit; color: inherit; }
select option { background: #061220; }

.grid-bg { position: fixed; inset: 0; pointer-events: none;
  background: radial-gradient(circle at 50% 28%, rgba(63, 216, 255, .10), transparent 55%),
    linear-gradient(rgba(63, 216, 255, .045) 1px, transparent 1px) 0 0 / 40px 40px,
    linear-gradient(90deg, rgba(63, 216, 255, .045) 1px, transparent 1px) 0 0 / 40px 40px; }
.scanline { position: fixed; inset: 0; pointer-events: none; background: linear-gradient(transparent 50%, rgba(63,216,255,.02) 50%) 0 0 / 100% 4px; }
.panel { background: var(--panel); border: 1px solid var(--line); border-radius: 14px;
  backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 0 24px rgba(63, 216, 255, .07), inset 0 0 18px rgba(63, 216, 255, .04); }
.label { font-family: var(--mono); font-size: 11px; letter-spacing: .25em; color: var(--muted); }
.btn { border: 1px solid var(--line); background: transparent; padding: 9px 13px; border-radius: 10px; cursor: pointer; transition: .2s; display: inline-block; }
.btn:hover { border-color: var(--cyan); box-shadow: 0 0 12px rgba(63, 216, 255, .3); }
.btn.primary { background: linear-gradient(90deg, rgba(63,216,255,.25), rgba(63,216,255,.08)); border-color: var(--cyan); letter-spacing: .08em; }
.btn.ghost { width: 100%; text-align: left; font-size: 14px; }
.btn.ok { border-color: var(--green); color: var(--green); }
.btn.danger { border-color: var(--red); color: var(--red); }
.btn.small { padding: 5px 9px; font-size: 12px; }
.icon-btn { width: 42px; height: 42px; min-width: 42px; display: grid; place-items: center; border-radius: 50%; border: 1px solid var(--line); background: transparent; cursor: pointer; font-size: 17px; transition: .2s; }
.icon-btn.sm { width: 34px; height: 34px; min-width: 34px; font-size: 14px; }
.icon-btn:hover, .icon-btn.on { border-color: var(--cyan); box-shadow: 0 0 14px rgba(63, 216, 255, .45); }
.icon-btn.on { background: rgba(63, 216, 255, .18); }
.mic.rec { border-color: var(--red); box-shadow: 0 0 18px var(--red); animation: pulse 1s infinite; }
.err { color: var(--red); min-height: 1em; font-size: 14px; }
input.f, textarea.f, select.f, .search, .login-box input { width: 100%; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--line); background: rgba(0,0,0,.35); outline: none; }
input.f:focus, textarea.f:focus, .search:focus { border-color: var(--cyan); }

/* ---------- Login ---------- */
.login { position: fixed; inset: 0; display: grid; place-items: center; padding: 16px; z-index: 5; }
.login-box { width: min(380px, 100%); padding: 32px 26px; display: flex; flex-direction: column; gap: 12px; text-align: center; }
.login-box h1 { margin: 6px 0 0; letter-spacing: .35em; font-weight: 300; color: var(--cyan-2); text-shadow: 0 0 18px var(--cyan); }
.sub { margin: 0 0 10px; color: var(--muted); font-size: 13px; }
.mini-core { position: relative; width: 70px; height: 70px; margin: 0 auto; }
.mini-core span { position: absolute; inset: 0; border-radius: 50%; border: 2px solid transparent; border-top-color: var(--cyan); animation: spin 2.4s linear infinite; }
.mini-core span:nth-child(2) { inset: 10px; animation-duration: 1.6s; animation-direction: reverse; border-top-color: var(--cyan-2); }
.mini-core span:nth-child(3) { inset: 24px; background: radial-gradient(var(--cyan-2), transparent 70%); border: none; animation: pulse 2s infinite; }

/* ---------- Layout ---------- */
.app { position: relative; display: grid; grid-template-columns: 250px minmax(0, 1fr) 420px; gap: 12px; height: 100dvh; padding: 12px; padding-top: max(12px, env(safe-area-inset-top)); }
.sidebar { display: flex; flex-direction: column; padding: 12px; gap: 10px; min-height: 0; }
.side-head { display: flex; justify-content: space-between; align-items: center; }
.chat-list { list-style: none; margin: 0; padding: 0; overflow-y: auto; flex: 1; display: flex; flex-direction: column; gap: 3px; }
.chat-list li { padding: 9px 11px; border-radius: 10px; cursor: pointer; font-size: 14px; display: flex; justify-content: space-between; gap: 6px; border: 1px solid transparent; }
.chat-list li:hover { background: rgba(63, 216, 255, .07); }
.chat-list li.active { border-color: var(--line); background: rgba(63, 216, 255, .12); }
.chat-list li .t { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.chat-list li .x { opacity: 0; color: var(--muted); }
.chat-list li:hover .x { opacity: 1; }
.side-foot { display: flex; flex-direction: column; gap: 6px; }

.main { display: flex; flex-direction: column; min-height: 0; min-width: 0; }
.topbar { display: flex; align-items: center; gap: 10px; padding: 2px 2px 8px; }
.brand { font-weight: 300; letter-spacing: .35em; color: var(--cyan-2); text-shadow: 0 0 12px var(--cyan); white-space: nowrap; }
.brand small { display: block; font-family: var(--mono); font-size: 9px; letter-spacing: .3em; color: var(--muted); text-shadow: none; }
.hud-stats { margin-left: auto; display: flex; gap: 8px; align-items: center; font-family: var(--mono); font-size: 11px; color: var(--muted); }
.pill { border: 1px solid var(--line); padding: 4px 9px; border-radius: 99px; white-space: nowrap; }
.pill.ok { color: var(--green); border-color: rgba(77, 255, 176, .4); }
.pill.bad { color: var(--red); border-color: rgba(255, 77, 94, .5); }
.mobile-only { display: none; }

/* ---------- Kern ---------- */
.stage { display: grid; place-items: center; padding: 4px 0 18px; }
.core { position: relative; width: clamp(120px, 20vh, 210px); aspect-ratio: 1; transition: width .4s; }
.core svg { width: 100%; height: 100%; overflow: visible; }
.core .r { fill: none; stroke: var(--accent); transform-origin: 100px 100px; transition: stroke .4s; }
.r1 { stroke-width: 1; stroke-dasharray: 2 6; opacity: .6; animation: spin 40s linear infinite; }
.r2 { stroke-width: 3; stroke-dasharray: 90 30 10 30; opacity: .8; animation: spin 14s linear infinite reverse; }
.r3 { stroke-width: 1.5; stroke-dasharray: 160 60; opacity: .7; animation: spin 9s linear infinite; }
.r4 { stroke-width: 6; stroke-dasharray: 4 8; opacity: .45; animation: spin 20s linear infinite reverse; }
.ticks line { stroke: var(--accent); stroke-width: 1; opacity: .5; }
.glow { fill: var(--accent); opacity: .18; filter: blur(6px); transform-origin: 100px 100px; transition: transform .08s; }
.inner { fill: var(--accent); opacity: .85; filter: drop-shadow(0 0 12px var(--accent)); transform-origin: 100px 100px; transition: transform .08s; }
.core-label { position: absolute; left: -40px; right: -40px; bottom: -20px; text-align: center; font-family: var(--mono); font-size: 10px; letter-spacing: .35em; color: var(--accent); }
.core.listening { --accent: var(--red); }
.core.listening .r2, .core.listening .r3 { animation-duration: 3s; }
.core.thinking { --accent: var(--amber); }
.core.thinking .r2 { animation-duration: 1.4s; } .core.thinking .r3 { animation-duration: 1s; }
.core.speaking { --accent: var(--cyan-2); }
.app.has-messages .core { width: clamp(80px, 11vh, 120px); }

/* ---------- Nachrichten ---------- */
.messages { flex: 1; overflow-y: auto; padding: 14px 4px 10px; display: flex; flex-direction: column; gap: 10px; min-height: 0; }
.msg { max-width: min(760px, 94%); padding: 11px 15px; border-radius: 14px; line-height: 1.5; font-size: 15px; overflow-wrap: anywhere; animation: fadein .25s; }
.msg.user { align-self: flex-end; background: rgba(63, 216, 255, .14); border: 1px solid var(--line); }
.msg.assistant { align-self: flex-start; background: rgba(0, 0, 0, .35); border-left: 2px solid var(--cyan); }
.msg img, .msg video, .win img, .win video { max-width: 100%; border-radius: 10px; margin-top: 8px; display: block; }
.msg code, .win code { font-family: var(--mono); background: rgba(63, 216, 255, .1); padding: 1px 5px; border-radius: 4px; }
.msg pre, .win pre { background: rgba(0, 0, 0, .5); padding: 10px; border-radius: 8px; overflow-x: auto; font-size: 12px; }
.msg a, .win a { color: var(--cyan-2); }
.msg .tools { font-family: var(--mono); font-size: 11px; color: var(--amber); margin-bottom: 4px; }
.msg .tools:empty { display: none; }
.msg .meta { font-family: var(--mono); font-size: 10px; color: var(--muted); margin-top: 6px; }
.msg .acts { margin-top: 4px; display: flex; gap: 6px; opacity: .45; }
.msg .acts button { background: none; border: none; cursor: pointer; padding: 2px; font-size: 13px; }
.msg:hover .acts { opacity: 1; }
.learned { align-self: flex-start; font-family: var(--mono); font-size: 11px; color: var(--violet); border: 1px dashed rgba(180,140,255,.4); border-radius: 10px; padding: 6px 10px; }
.cursor::after { content: "▍"; animation: blink 1s infinite; color: var(--cyan); }

.composer { padding: 8px; margin-bottom: env(safe-area-inset-bottom); }
.composer .row { display: flex; gap: 8px; align-items: flex-end; }
.composer textarea { flex: 1; resize: none; max-height: 160px; background: transparent; border: none; outline: none; padding: 11px 6px; font-size: 16px; min-width: 0; }
.send { background: rgba(63, 216, 255, .18); }
.attach-preview { display: flex; gap: 6px; flex-wrap: wrap; }
.attach-preview img { height: 54px; border-radius: 8px; border: 1px solid var(--line); cursor: pointer; margin: 2px; }

/* ---------- HUD ---------- */
.hud { display: flex; flex-direction: column; gap: 12px; min-height: 0; }
.hud-panel { padding: 10px 12px; display: flex; flex-direction: column; min-height: 0; }
.hud-panel.grow { flex: 1; }
.ph { display: flex; align-items: center; gap: 10px; }
.pct { margin-left: auto; font-family: var(--mono); font-size: 18px; color: var(--cyan-2); text-shadow: 0 0 10px var(--cyan); }
.ms { font-family: var(--mono); font-size: 11px; color: var(--muted); min-width: 60px; text-align: right; }
.pop { background: none; border: 1px solid var(--line); color: var(--muted); border-radius: 6px; cursor: pointer; padding: 2px 6px; font-size: 12px; }
.pop:hover { color: var(--cyan); border-color: var(--cyan); }
.progress { height: 3px; background: rgba(63,216,255,.12); border-radius: 3px; margin: 8px 0 4px; overflow: hidden; }
#procBar { height: 100%; width: 0; background: linear-gradient(90deg, var(--cyan), var(--cyan-2)); box-shadow: 0 0 10px var(--cyan); transition: width .3s; }
#pipeline { width: 100%; height: auto; }
#pipeline .edge { stroke: var(--line); stroke-width: 1.5; fill: none; }
#pipeline .edge.on { stroke: var(--cyan); stroke-dasharray: 4 4; animation: flow .6s linear infinite; }
#pipeline .node circle { fill: rgba(0,0,0,.5); stroke: var(--line); stroke-width: 1.5; transition: .3s; }
#pipeline .node text { fill: var(--muted); font-family: var(--mono); font-size: 8px; text-anchor: middle; }
#pipeline .node .ico { font-size: 13px; fill: var(--text); }
#pipeline .node.active circle { stroke: var(--amber); fill: rgba(255,181,71,.15); filter: drop-shadow(0 0 6px var(--amber)); animation: pulse .8s infinite; }
#pipeline .node.done circle { stroke: var(--cyan); fill: rgba(63,216,255,.15); filter: drop-shadow(0 0 4px var(--cyan)); }
#pipeline .node.error circle { stroke: var(--red); }
#pipeline .node.done text.t { fill: var(--cyan-2); }
.timeline { list-style: none; margin: 4px 0 0; padding: 0 0 0 4px; max-height: 24vh; overflow-y: auto; font-size: 12px; }
.timeline li { position: relative; padding: 4px 0 6px 18px; border-left: 1px solid var(--line); display: grid; grid-template-columns: 1fr auto; gap: 2px 8px; animation: fadein .2s; }
.timeline li::before { content: ""; position: absolute; left: -5px; top: 7px; width: 9px; height: 9px; border-radius: 50%; background: var(--bg); border: 1.5px solid var(--muted); }
.timeline li.done::before { border-color: var(--cyan); background: var(--cyan); box-shadow: 0 0 6px var(--cyan); }
.timeline li.active::before, .timeline li.waiting::before { border-color: var(--amber); animation: pulse .8s infinite; }
.timeline li.error::before { border-color: var(--red); background: var(--red); }
.timeline .tl { color: var(--text); }
.timeline .tm { font-family: var(--mono); color: var(--muted); font-size: 11px; }
.timeline .td { grid-column: 1 / -1; color: var(--muted); font-size: 11px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.timeline .plan { grid-column: 1 / -1; margin: 4px 0 0; padding-left: 16px; color: var(--muted); }
.timeline .plan li.ok { color: var(--green); }

.tabs { display: flex; gap: 2px; flex-wrap: wrap; border-bottom: 1px solid var(--line); padding-bottom: 6px; margin-bottom: 8px; }
.tabs button { background: none; border: none; color: var(--muted); padding: 5px 7px; border-radius: 6px; cursor: pointer; font-size: 12px; }
.tabs button.on { color: var(--cyan-2); background: rgba(63,216,255,.12); }
.tabs b { color: var(--amber); font-weight: 600; }
.tabs .pop { margin-left: auto; }
.tab-body { flex: 1; overflow-y: auto; min-height: 0; position: relative; }
.globe { width: 100%; height: 100%; min-height: 260px; }
.globe svg { width: 100%; height: 100%; }
.globe .sphere { fill: rgba(63,216,255,.04); stroke: var(--line); }
.globe .grat { fill: none; stroke: rgba(63,216,255,.12); stroke-width: .5; }
.globe .land { fill: rgba(63,216,255,.16); stroke: rgba(140,236,255,.55); stroke-width: .4; }
.globe .marker { fill: var(--amber); }
.globe .ping { fill: none; stroke: var(--amber); stroke-width: 1.5; animation: ping 1.6s ease-out infinite; transform-box: fill-box; transform-origin: center; }
.map-label { position: absolute; left: 8px; bottom: 6px; font-family: var(--mono); font-size: 12px; color: var(--amber); letter-spacing: .1em; }
.windows { display: flex; flex-direction: column; gap: 8px; }
.win { border: 1px solid var(--line); border-radius: 10px; padding: 8px 10px; background: rgba(0,0,0,.3); font-size: 13px; animation: fadein .3s; }
.win.result { border-color: rgba(77,255,176,.4); } .win.warning { border-color: var(--amber); } .win.code { font-family: var(--mono); }
.win .wh { display: flex; justify-content: space-between; color: var(--cyan-2); font-size: 12px; margin-bottom: 4px; }
.win .wh button { background: none; border: none; color: var(--muted); cursor: pointer; }
.console { margin: 0; font-family: var(--mono); font-size: 11px; line-height: 1.5; color: var(--cyan-2); white-space: pre-wrap; word-break: break-all; }
.console .tool { color: var(--amber); } .console .ui { color: var(--violet); } .console .err { color: var(--red); } .console .ok { color: var(--green); }
.actions-list .act { border: 1px solid var(--amber); border-radius: 10px; padding: 10px; margin-bottom: 8px; background: rgba(255,181,71,.06); }
.actions-list .act.done { border-color: var(--line); background: none; opacity: .75; }
.actions-list pre { white-space: pre-wrap; font-size: 12px; max-height: 200px; overflow: auto; background: rgba(0,0,0,.4); padding: 8px; border-radius: 6px; }
.actions-list .btns { display: flex; gap: 8px; }
.chips { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 8px; }
.chip { border: 1px solid var(--line); border-radius: 99px; padding: 3px 9px; font-size: 11px; cursor: pointer; background: none; }
.chip.on { background: rgba(63,216,255,.18); border-color: var(--cyan); }
.mem-row { display: grid; grid-template-columns: auto 1fr auto; gap: 8px; align-items: start; padding: 6px 0; border-bottom: 1px solid rgba(63,216,255,.1); font-size: 13px; }
.kind { font-family: var(--mono); font-size: 10px; padding: 1px 6px; border-radius: 4px; border: 1px solid var(--line); color: var(--cyan-2); white-space: nowrap; }
.kind.rule { color: var(--red); border-color: rgba(255,77,94,.5); } .kind.goal { color: var(--green); } .kind.project { color: var(--amber); } .kind.preference { color: var(--violet); }
.mem-graph { width: 100%; height: 220px; }
.mem-graph line { stroke: rgba(63,216,255,.3); } .mem-graph circle { stroke: var(--bg); }
.stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-bottom: 10px; }
.stat { border: 1px solid var(--line); border-radius: 8px; padding: 6px; text-align: center; }
.stat b { display: block; font-size: 18px; color: var(--cyan-2); font-family: var(--mono); }
.stat span { font-size: 10px; color: var(--muted); }
.check { display: flex; gap: 8px; font-size: 13px; padding: 4px 0; border-bottom: 1px solid rgba(63,216,255,.08); }
.check small { color: var(--muted); margin-left: auto; text-align: right; }

/* ---------- Pop-out (zweiter Bildschirm) ---------- */
body.popout .app { grid-template-columns: 1fr; }
body.popout .sidebar, body.popout .main { display: none; }
body.popout .hud { height: 100%; }
body.popout .timeline { max-height: none; }

/* ---------- Toasts & Modal ---------- */
.toasts { position: fixed; top: 14px; left: 50%; transform: translateX(-50%); z-index: 20; display: flex; flex-direction: column; gap: 8px; width: min(520px, 92vw); }
.toast { background: rgba(4,16,28,.95); border: 1px solid var(--amber); color: var(--text); border-radius: 12px; padding: 10px 14px; font-size: 14px; cursor: pointer; animation: fadein .3s; box-shadow: 0 0 20px rgba(255,181,71,.2); }
.modal { position: fixed; inset: 0; background: rgba(0,0,0,.6); display: grid; place-items: center; z-index: 10; padding: 16px; }
.modal-box { width: min(560px, 100%); max-height: 86dvh; overflow-y: auto; padding: 18px; }
.modal-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; font-size: 14px; }
.list-row { display: flex; justify-content: space-between; gap: 10px; padding: 8px 0; border-bottom: 1px solid var(--line); font-size: 14px; }
.toggle { flex-direction: row; align-items: center; gap: 10px; cursor: pointer; }

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes pulse { 50% { opacity: .5; } }
@keyframes blink { 50% { opacity: 0; } }
@keyframes flow { to { stroke-dashoffset: -8; } }
@keyframes ping { from { transform: scale(1); opacity: 1; } to { transform: scale(4); opacity: 0; } }
@keyframes fadein { from { opacity: 0; transform: translateY(6px); } }

/* ---------- Tablet / Handy ---------- */
@media (max-width: 1180px) {
  .app { grid-template-columns: 230px minmax(0, 1fr); }
  .hud { position: fixed; z-index: 8; top: 0; right: 0; bottom: 0; width: min(440px, 100%); padding: 12px; padding-top: max(12px, env(safe-area-inset-top)); background: rgba(2,8,14,.97); transform: translateX(105%); transition: transform .25s; }
  .hud.open { transform: none; }
  #hudBtn { display: grid; }
}
@media (max-width: 820px) {
  .app { grid-template-columns: minmax(0, 1fr); padding: 10px 16px; padding-top: max(10px, env(safe-area-inset-top)); }
  .sidebar { position: fixed; z-index: 8; top: 0; bottom: 0; left: 0; width: 82%; max-width: 320px; border-radius: 0 14px 14px 0; transform: translateX(-105%); transition: transform .25s; background: rgba(2,10,18,.97); padding-top: max(14px, env(safe-area-inset-top)); }
  .sidebar.open { transform: none; }
  .mobile-only { display: grid; }
  .brand { font-size: 13px; letter-spacing: .22em; }
  .brand small, #clock, #memPill { display: none; }
  .composer .icon-btn { width: 38px; height: 38px; min-width: 38px; }
  .composer .row { gap: 5px; }
}
JARVIS_EOF
mkdir -p 'frontend'
cat > 'frontend/sw.js' <<'JARVIS_EOF'
// Service Worker: macht Jarvis auf dem Handy installierbar. API-Aufrufe werden nie gecacht.
const CACHE = "jarvis-v2";
const SHELL = ["/", "/index.html", "/style.css", "/app.js", "/manifest.json", "/icon.svg", "/vendor/d3.min.js", "/vendor/topojson-client.min.js"];

self.addEventListener("install", (e) => e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL))));
self.addEventListener("activate", (e) =>
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))));
self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (url.pathname.startsWith("/api/") || e.request.method !== "GET") return;
  e.respondWith(fetch(e.request).then((r) => {
    const copy = r.clone();
    caches.open(CACHE).then((c) => c.put(e.request, copy));
    return r;
  }).catch(() => caches.match(e.request)));
});
JARVIS_EOF
cat > 'install.sh' <<'JARVIS_EOF'
#!/usr/bin/env bash
# J.A.R.V.I.S. – einmalige Installation (macOS / Linux)
set -e
cd "$(dirname "$0")"
echo "== J.A.R.V.I.S. Installation =="

# 1) Python 3.12 (3.11/3.12 nötig – neuere Versionen haben oft noch keine KI-Pakete)
PY=$(command -v python3.12 || command -v python3.11 || true)
if [ -z "$PY" ]; then
  if command -v brew >/dev/null; then brew install python@3.12; PY=$(command -v python3.12); else
    echo "❌ Bitte Python 3.12 installieren (Mac: brew install python@3.12)"; exit 1; fi
fi
echo "→ $($PY --version)"
[ -d .venv ] || $PY -m venv .venv
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r backend/requirements.txt
python -m playwright install chromium          # unsichtbarer Browser für den Web-Agent
command -v ffmpeg >/dev/null || { command -v brew >/dev/null && brew install ffmpeg || echo "⚠ ffmpeg fehlt (für Videos)"; }

# 2) Konfiguration
[ -f backend/.env ] || cp backend/.env.example backend/.env
chmod 600 backend/.env
if grep -q CHANGE_ME searxng/settings.yml; then
  KEY=$(python -c "import secrets;print(secrets.token_hex(32))")
  sed -i.bak "s/CHANGE_ME_install_sh_ersetzt_das/$KEY/" searxng/settings.yml && rm -f searxng/settings.yml.bak
fi

# 3) Weltkarte & Grafik-Bibliotheken einmalig lokal speichern (danach offline)
mkdir -p frontend/vendor
curl -fsSL https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js -o frontend/vendor/d3.min.js
curl -fsSL https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js -o frontend/vendor/topojson-client.min.js
curl -fsSL https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json -o frontend/vendor/countries-110m.json

# 4) Gehirn (Ollama, lokal)
if ! command -v ollama >/dev/null; then
  echo "⚠ Ollama fehlt → https://ollama.com/download (Mac: brew install ollama). Danach install.sh erneut starten."
else
  pgrep -x ollama >/dev/null || (ollama serve >/dev/null 2>&1 &) ; sleep 3
  for M in LLM_MODEL VISION_MODEL EMBED_MODEL; do ollama pull "$(grep "^$M=" backend/.env | cut -d= -f2)"; done
fi

# 5) Private Websuche (SearXNG in Docker)
command -v docker >/dev/null && docker compose up -d || echo "⚠ Docker fehlt – Websuche erst nach Docker Desktop/OrbStack."

# 6) Stimmen (einmaliger Download)
(cd backend && python setup_voices.py)

# 7) HTTPS-Zertifikat (fürs Handy-Mikrofon)
mkdir -p certs
if [ ! -f certs/cert.pem ]; then
  IP=$(ipconfig getifaddr en0 2>/dev/null || hostname -I 2>/dev/null | awk '{print $1}' || echo 127.0.0.1)
  openssl req -x509 -newkey rsa:2048 -nodes -days 825 -keyout certs/key.pem -out certs/cert.pem \
    -subj "/CN=jarvis.local" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1,IP:${IP}" 2>/dev/null
  chmod 600 certs/key.pem
fi

# 8) Dein Besitzer-Konto
(cd backend && python create_user.py)

# 9) Versionsverwaltung
if [ ! -d .git ]; then git init -q && git add -A && git commit -qm "J.A.R.V.I.S. Grundinstallation" && echo "→ Git-Repository angelegt"; fi

echo; echo "✔ Fertig. Starten mit:  ./start.sh"
echo "  Mac: Für Bildschirm-Steuerung in Systemeinstellungen → Datenschutz → 'Bildschirmaufnahme' und 'Bedienungshilfen' dem Terminal erlauben."
JARVIS_EOF
mkdir -p 'searxng'
cat > 'searxng/settings.yml' <<'JARVIS_EOF'
use_default_settings: true
general:
  instance_name: "jarvis-search"
server:
  secret_key: "CHANGE_ME_install_sh_ersetzt_das"
  limiter: false
  image_proxy: false
search:
  safe_search: 0
  formats:
    - html
    - json
JARVIS_EOF
cat > 'start.sh' <<'JARVIS_EOF'
#!/usr/bin/env bash
# J.A.R.V.I.S. starten: Dashboard (Port 8443) + Steuerfenster (Port 8501, nur dieser Rechner)
cd "$(dirname "$0")"
source .venv/bin/activate
pgrep -x ollama >/dev/null || (ollama serve >/dev/null 2>&1 &)
command -v docker >/dev/null && docker compose up -d >/dev/null 2>&1
IP=$(ipconfig getifaddr en0 2>/dev/null || hostname -I 2>/dev/null | awk '{print $1}')
(cd backend && streamlit run control_panel.py --server.address 127.0.0.1 --server.port 8501 \
   --server.headless true --browser.gatherUsageStats false >/dev/null 2>&1 &)
echo "Dashboard:      https://localhost:8443"
echo "Handy (WLAN):   https://${IP}:8443"
echo "Steuerfenster:  http://127.0.0.1:8501"
cd backend && exec python main.py
JARVIS_EOF
mkdir -p 'voices'
cat > 'voices/.gitkeep' <<'JARVIS_EOF'

JARVIS_EOF
chmod +x install.sh start.sh
echo "✔ Jarvis-Ordner erstellt. Weiter mit:  cd jarvis && ./install.sh"
