"""Local automatic watermark detection + LaMA inpainting (no paid API)."""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("HF_HOME", str(ROOT / "models" / "huggingface"))
os.environ.setdefault("TORCH_HOME", str(ROOT / "models" / "torch"))
os.environ.setdefault("WMR_DATA_DIR", str(ROOT / "models" / "upstream"))
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
sys.path.insert(0, str(ROOT / "vendor" / "watermark_remover"))

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps
import torch
from transformers import AutoProcessor, Florence2ForConditionalGeneration
from remwm import detect_only
from lama_inpaint.runtime import LamaInpaint

MODEL_ID = "florence-community/Florence-2-base"
MODEL_REVISION = "00921df66db728a9ceb750f5eca43e5c203a2051"
Image.MAX_IMAGE_PIXELS = 24_000_000


class WatermarkPipeline:
    def __init__(self, device="auto"):
        self.device = "cuda" if device == "auto" and torch.cuda.is_available() else device
        if self.device == "auto":
            self.device = "cpu"
        if self.device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA is not available. Use --device cpu.")
        torch.set_num_threads(min(8, os.cpu_count() or 1))
        self.processor = None
        self.detector = None
        self.inpainter = None

    def prepare(self):
        if self.detector is None:
            print("Loading Florence-2 detection model...", flush=True)
            local_model = ROOT / "models" / "florence-base"
            source = str(local_model) if (local_model / ".complete").is_file() else MODEL_ID
            self.processor = AutoProcessor.from_pretrained(
                source, revision=MODEL_REVISION, trust_remote_code=False
            )
            self.detector = Florence2ForConditionalGeneration.from_pretrained(
                source, revision=MODEL_REVISION, trust_remote_code=False,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                attn_implementation="eager", use_safetensors=True,
            ).eval().to(self.device)
        if self.inpainter is None:
            print("Loading checksum-verified LaMA model...", flush=True)
            # Leave GPU memory for detection; i7 CPU runs the repair model.
            self.inpainter = LamaInpaint("cpu")

    def verify_region(self, image):
        """Require a second description of the crop before erasing its contents.

        An open-vocabulary detector may return a normal object even when no
        watermark exists. Ambiguous regions are left unchanged.
        """
        inputs = self.processor(text="<DETAILED_CAPTION>", images=image, return_tensors="pt")
        inputs = {
            key: value.to(self.device).to(self.detector.dtype) if value.is_floating_point()
            else value.to(self.device) for key, value in inputs.items()
        }
        with torch.inference_mode():
            tokens = self.detector.generate(**inputs, max_new_tokens=128, do_sample=False, num_beams=1)
        caption = self.processor.batch_decode(tokens, skip_special_tokens=True)[0]
        confirmed = bool(re.search(
            r"\b(watermarks?|logos?|texts?|letters?|words?|writing|symbols?|signatures?|stamps?|lettering|typography)\b",
            caption, re.I,
        ))
        return confirmed, caption

    def process(self, image_path, output_dir, max_edge=1600):
        start = time.perf_counter()
        image_path = Path(image_path)
        if image_path.stat().st_size > 20 * 1024 * 1024:
            raise ValueError("Please choose an image smaller than 20 MB.")
        if not 256 <= max_edge <= 2048:
            raise ValueError("max_edge must be between 256 and 2048.")
        with Image.open(image_path) as source:
            if source.width * source.height > Image.MAX_IMAGE_PIXELS:
                raise ValueError("Please choose an image smaller than 24 megapixels.")
            image = ImageOps.exif_transpose(source).convert("RGB")
        original_size = image.size
        image.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
        self.prepare()
        print("Detecting watermark regions...", flush=True)
        with torch.inference_mode():
            detections = detect_only(
                image, self.detector, self.processor, self.device,
                max_bbox_percent=85, detection_prompt="watermark",
            )
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        preview = image.copy()
        preview_draw = ImageDraw.Draw(preview)
        boxes = []
        verification = []
        unverified_regions = 0
        for item in detections:
            if not item["accepted"]:
                continue
            left, top, right, bottom = item["bbox"]
            left, top = max(0, left - 4), max(0, top - 4)
            right, bottom = min(image.width, right + 4), min(image.height, bottom + 4)
            if left >= right or top >= bottom:
                continue
            confirmed, caption = self.verify_region(image.crop((left, top, right, bottom)))
            verification.append({"box": [left, top, right, bottom], "confirmed": confirmed, "caption": caption})
            if not confirmed:
                unverified_regions += 1
                continue
            draw.rectangle((left, top, right, bottom), fill=255)
            preview_draw.rectangle((left, top, right, bottom), outline="#ff4040", width=3)
            boxes.append([left, top, right, bottom])

        if boxes:
            print(f"Repairing {len(boxes)} detected region(s)...", flush=True)
            with torch.inference_mode():
                bgr = self.inpainter(np.array(image), np.array(mask))
            result = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        else:
            # Explicitly report a miss instead of claiming an unchanged image is repaired.
            result = image.copy()

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        image.save(output_dir / "original.png")
        result.save(output_dir / "result.png")
        preview.save(output_dir / "detection.png")
        mask.save(output_dir / "mask.png")
        comparison = Image.new("RGB", (image.width * 2, image.height), "white")
        comparison.paste(image, (0, 0))
        comparison.paste(result, (image.width, 0))
        comparison.save(output_dir / "comparison.png")
        metadata = {
            "status": "completed" if boxes else "no_watermark",
            "regions": len(boxes), "boxes": boxes,
            "skippedRegions": sum(not item["accepted"] for item in detections),
            "unverifiedRegions": unverified_regions, "verification": verification,
            "originalSize": list(original_size), "outputSize": list(image.size),
            "resized": original_size != image.size,
            "seconds": round(time.perf_counter() - start, 2),
            "device": self.device,
        }
        (output_dir / "report.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--max-edge", type=int, default=1600)
    parser.add_argument("--prepare", action="store_true", help="Download and load models only")
    args = parser.parse_args()
    pipeline = WatermarkPipeline(args.device)
    if args.prepare:
        pipeline.prepare()
        print("Models are ready.")
        return
    if args.input is None:
        parser.error("Choose an input image, or use --prepare.")
    output = args.output or ROOT / "outputs" / time.strftime("%Y%m%d-%H%M%S")
    print(json.dumps(pipeline.process(args.input, output, args.max_edge), indent=2))
    print(f"Result folder: {output.resolve()}")


if __name__ == "__main__":
    main()
