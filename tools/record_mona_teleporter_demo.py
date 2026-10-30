"""Record a Mona Teleporter demo in the badger.github.io simulator.

Needs Playwright (with Chromium) and ffmpeg. Writes demo/mona_teleporter.webm and .mp4.
"""

import base64
import pathlib
import subprocess
import tempfile

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
APP = ROOT / "badge" / "apps" / "mona_teleporter"
OUT = ROOT / "demo"
EDITOR_URL = "https://badger.github.io/editor"
SCALE = 2

# (button title, seconds to wait afterwards)
STORYBOARD = (
    (None, 2.5),
    *(("Right", 1.2),) * 8,
    ("Right", 1.2),
    ("Select", 2.0),
    ("Right", 1.5),
    ("Up", 2.2),
    ("Down", 1.0),
    ("Right", 1.8),
)

# The editor's "Connect badge" reads a BADGER folder via showDirectoryPicker;
# serve it a fake one from origin-private storage holding just this app.
LOAD_APP_JS = """async (files) => {
  const root = await navigator.storage.getDirectory();
  const apps = await root.getDirectoryHandle('apps', {create: true});
  const dir = await apps.getDirectoryHandle('mona_teleporter', {create: true});
  for (const [path, b64] of Object.entries(files)) {
    const parts = path.split('/');
    const name = parts.pop();
    let d = dir;
    for (const s of parts) d = await d.getDirectoryHandle(s, {create: true});
    const w = await (await d.getFileHandle(name, {create: true})).createWritable();
    await w.write(Uint8Array.from(atob(b64), c => c.charCodeAt(0)));
    await w.close();
  }
  window.showDirectoryPicker = async () => root;
}"""

START_RECORDING_JS = """() => {
  const canvas = document.getElementById('badge-screen');
  const rec = new MediaRecorder(canvas.captureStream(30), {
    mimeType: 'video/webm;codecs=vp9', videoBitsPerSecond: 8_000_000,
  });
  window.__chunks = [];
  rec.ondataavailable = e => e.data.size && window.__chunks.push(e.data);
  rec.start();
  window.__rec = rec;
  return [canvas.width, canvas.height];
}"""

STOP_RECORDING_JS = """() => new Promise(resolve => {
  window.__rec.onstop = async () => {
    const buf = await new Blob(window.__chunks).arrayBuffer();
    let s = '';
    const bytes = new Uint8Array(buf);
    for (let i = 0; i < bytes.length; i += 0x8000)
      s += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
    resolve(btoa(s));
  };
  window.__rec.stop();
})"""


def app_files():
    return {
        str(p.relative_to(APP)): base64.b64encode(p.read_bytes()).decode()
        for p in APP.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and not p.name.startswith(".")
    }


def record(raw_path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 1000})
        page.goto(EDITOR_URL, wait_until="networkidle")
        page.evaluate(LOAD_APP_JS, app_files())

        page.click("#connect-disk")
        page.wait_for_selector("#disk-status:has-text('1 apps')")
        page.click("#device-app")
        page.click("dialog[open] button:has-text('Edit')")
        page.wait_for_selector(".project-file:has-text('assets/diner.png')")

        page.click("#run")
        page.wait_for_timeout(5000)

        size = page.evaluate(START_RECORDING_JS)
        for button, wait in STORYBOARD:
            if button:
                page.click(f".badge-control[title='{button}']", delay=150)
            page.wait_for_timeout(int(wait * 1000))
        raw_path.write_bytes(base64.b64decode(page.evaluate(STOP_RECORDING_JS)))
        browser.close()
    return size


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def main():
    OUT.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        raw = pathlib.Path(tmp) / "raw.webm"
        width, height = record(raw)
        scale = f"scale={width * SCALE}:{height * SCALE}:flags=neighbor,fps=30"
        ffmpeg("-i", str(raw), "-vf", scale, "-c:v", "libvpx-vp9", "-b:v", "0",
               "-crf", "24", "-an", str(OUT / "mona_teleporter.webm"))
        ffmpeg("-i", str(raw), "-vf", scale, "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-crf", "18", "-movflags", "+faststart", "-an", str(OUT / "mona_teleporter.mp4"))
    print(f"Wrote {OUT / 'mona_teleporter.webm'} and {OUT / 'mona_teleporter.mp4'}")


if __name__ == "__main__":
    main()
