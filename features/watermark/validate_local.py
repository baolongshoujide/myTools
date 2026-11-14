"""Real-model local API smoke test with an owned, generated watermark image."""
import io
import json
from pathlib import Path
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import requests

ROOT = Path(__file__).resolve().parent
BASE_URL = "http://127.0.0.1:8765"


def make_fixtures(folder):
    folder.mkdir(parents=True, exist_ok=True)
    width, height = 960, 640
    y = np.linspace(0, 1, height)[:, None, None]
    pixels = np.broadcast_to(
        np.array([80, 165, 225]) * (1-y) + np.array([215, 235, 230]) * y,
        (height, width, 3),
    ).copy().astype("uint8")
    image = Image.fromarray(pixels)
    draw = ImageDraw.Draw(image)
    draw.ellipse((680, 60, 790, 170), fill=(255, 235, 160))
    draw.polygon([(0, 390), (160, 170), (370, 410), (550, 160), (800, 410), (960, 220), (960, 640), (0, 640)], fill=(70, 115, 115))
    draw.polygon([(0, 450), (280, 300), (540, 460), (740, 310), (960, 440), (960, 640), (0, 640)], fill=(65, 145, 130))
    draw.rectangle((0, 470, 960, 640), fill=(85, 165, 190))
    image.save(folder / "clean.png")
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 48)
    draw.text((130, 520), "SAMPLE WATERMARK", font=font, fill=(255, 255, 255, 210), stroke_width=1, stroke_fill=(90, 90, 90, 140))
    Image.alpha_composite(image.convert("RGBA"), layer).convert("RGB").save(folder / "watermarked.png")


def wait_for_job(session, job_id):
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        response = session.get(BASE_URL + "/jobs/" + job_id, timeout=15)
        response.raise_for_status()
        job = response.json()
        if job["status"] in {"completed", "no_watermark", "failed"}:
            return job
        print("Job status:", job["status"], flush=True)
        time.sleep(5)
    raise TimeoutError("Model processing exceeded 10 minutes")


def main():
    folder = ROOT / ".runtime" / "validation"
    make_fixtures(folder)
    session = requests.Session()
    session.trust_env = False  # Loopback requests must not use an internet proxy.
    assert session.get(BASE_URL + "/health", timeout=10).status_code == 200
    assert session.post(BASE_URL + "/jobs", files={"file": ("invalid.png", b"not an image")}, timeout=10).status_code == 400
    assert session.get(BASE_URL + "/jobs/not-a-task", timeout=10).status_code == 404
    with (folder / "watermarked.png").open("rb") as source:
        response = session.post(BASE_URL + "/jobs", files={"file": ("watermarked.png", source, "image/png")}, timeout=30)
    response.raise_for_status()
    job_id = response.json()["id"]
    with (folder / "clean.png").open("rb") as source:
        busy = session.post(BASE_URL + "/jobs", files={"file": ("clean.png", source, "image/png")}, timeout=30)
    assert busy.status_code == 429, busy.text
    positive = wait_for_job(session, job_id)
    assert positive["status"] == "completed", positive
    result = session.get(BASE_URL + f"/jobs/{job_id}/result.png", timeout=30)
    result.raise_for_status()
    (folder / "repaired.png").write_bytes(result.content)
    clean = np.array(Image.open(folder / "clean.png")).astype(float)
    marked = np.array(Image.open(folder / "watermarked.png")).astype(float)
    repaired = np.array(Image.open(io.BytesIO(result.content))).astype(float)
    before_error = float(np.abs(marked - clean).mean())
    after_error = float(np.abs(repaired - clean).mean())
    assert after_error < before_error, {"before": before_error, "after": after_error}
    with (folder / "clean.png").open("rb") as source:
        response = session.post(BASE_URL + "/jobs", files={"file": ("clean.png", source, "image/png")}, timeout=30)
    response.raise_for_status()
    negative = wait_for_job(session, response.json()["id"])
    assert negative["status"] == "no_watermark", negative
    unchanged = session.get(BASE_URL + f"/jobs/{negative['id']}/result.png", timeout=30)
    unchanged.raise_for_status()
    assert np.array_equal(np.array(Image.open(io.BytesIO(unchanged.content))), clean)
    report = {"positive": positive, "negative": negative, "meanErrorBefore": before_error, "meanErrorAfter": after_error}
    (folder / "check-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2), flush=True)
    print("Real-model API checks passed.", flush=True)


if __name__ == "__main__":
    main()
