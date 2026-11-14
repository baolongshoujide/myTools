"""Development API. Binds to loopback; cloud task relay is a separate later step."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from pathlib import Path
from threading import Lock
import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse
from PIL import UnidentifiedImageError, Image

from pipeline import ROOT, WatermarkPipeline

pipeline = WatermarkPipeline()
executor = ThreadPoolExecutor(max_workers=1)
jobs = {}
lock = Lock()
MAX_BYTES = 20 * 1024 * 1024


@asynccontextmanager
async def lifespan(app):
    yield
    executor.shutdown(wait=True, cancel_futures=True)


app = FastAPI(title="Local watermark repair", lifespan=lifespan)


def run_job(job_id, image_path, folder):
    with lock:
        jobs[job_id]["status"] = "processing"
    try:
        report = pipeline.process(image_path, folder)
        with lock:
            jobs[job_id].update(report)
    except Exception as error:
        print(f"Job {job_id} failed: {error}", flush=True)
        with lock:
            jobs[job_id].update(status="failed", message="图片处理失败，请查看电脑端日志后重试")
    finally:
        image_path.unlink(missing_ok=True)


@app.get("/health")
def health():
    return {
        "status": "ready", "device": pipeline.device,
        "modelsLoaded": pipeline.detector is not None and pipeline.inpainter is not None,
    }


@app.post("/jobs", status_code=202)
async def create_job(file: UploadFile):
    job_id = uuid4().hex
    folder = ROOT / "outputs" / job_id
    folder.mkdir(parents=True)
    image_path = folder / "upload.bin"
    # One upload/queued/running task at a time keeps RAM and disk use bounded.
    with lock:
        if any(item["status"] in {"uploading", "queued", "processing"} for item in jobs.values()):
            folder.rmdir()
            raise HTTPException(429, "当前正在处理其他图片，请稍后重试")
        for key in list(jobs):
            if time.time() - jobs[key]["createdAt"] > 86400:
                del jobs[key]
        jobs[job_id] = {"id": job_id, "status": "uploading", "createdAt": time.time()}
    try:
        size = 0
        with image_path.open("wb") as stream:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_BYTES:
                    raise HTTPException(413, "请选择小于20MB的图片")
                stream.write(chunk)
        if size == 0:
            raise HTTPException(400, "图片文件为空")
        with Image.open(image_path) as image:
            if image.width * image.height > Image.MAX_IMAGE_PIXELS:
                raise HTTPException(413, "图片像素过大，请缩小后重试")
            image.verify()
        with lock:
            jobs[job_id]["status"] = "queued"
        executor.submit(run_job, job_id, image_path, folder)
        return {"id": job_id, "status": "queued"}
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        with lock:
            jobs.pop(job_id, None)
        image_path.unlink(missing_ok=True)
        raise HTTPException(400, "无法读取该图片，请选择PNG、JPG或WebP图片")
    except Exception:
        with lock:
            jobs.pop(job_id, None)
        image_path.unlink(missing_ok=True)
        raise
    finally:
        await file.close()


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    with lock:
        if job_id not in jobs:
            raise HTTPException(404, "任务不存在或已过期，请重新上传")
        return dict(jobs[job_id])


@app.get("/jobs/{job_id}/{filename}")
def get_image(job_id: str, filename: str):
    with lock:
        job = jobs.get(job_id)
        if job is None or job["status"] not in {"completed", "no_watermark"}:
            raise HTTPException(404, "图片尚未生成或任务已过期")
    if filename not in {"original.png", "result.png", "detection.png", "comparison.png"}:
        raise HTTPException(404, "图片不存在")
    return FileResponse(ROOT / "outputs" / job_id / filename, media_type="image/png")
