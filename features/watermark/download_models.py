"""Download pinned public model files with resume and integrity verification."""
import hashlib
import json
from pathlib import Path
import subprocess
import re
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parent
REVISION = "00921df66db728a9ceb750f5eca43e5c203a2051"
REPOSITORY = "florence-community/Florence-2-base"


def download(url, destination, size=None):
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(destination.name + ".part")
    if size is not None and size > 16 * 1024 * 1024:
        # Bounded ranges resume reliably even when a long proxy connection stalls.
        first_offset = partial.stat().st_size if partial.exists() else 0

        def fetch_range(offset):
            end = min(offset + 8 * 1024 * 1024, size) - 1
            chunk = partial.with_name(partial.name + f".{offset}.chunk")
            headers = partial.with_name(partial.name + f".{offset}.headers")
            subprocess.run([
                "curl.exe", "-fsSL", "--retry", "3", "--retry-delay", "2",
                "--connect-timeout", "30", "--max-time", "120",
                "--speed-limit", "1024", "--speed-time", "30",
                "--range", f"{offset}-{end}", "--max-filesize", str(end - offset + 1),
                "-D", str(headers), url, "-o", str(chunk),
            ], check=True)
            ranges = re.findall(r"content-range:\s*bytes\s+(\d+)-(\d+)/(\d+)", headers.read_text(), re.I)
            if not ranges or tuple(map(int, ranges[-1])) != (offset, end, size):
                raise RuntimeError("Download server returned an unexpected byte range")
            if chunk.stat().st_size != end - offset + 1:
                raise RuntimeError("Incomplete model download range")
            headers.unlink()
            return chunk, end

        with ThreadPoolExecutor(max_workers=3) as pool:
            for chunk, end in pool.map(fetch_range, range(first_offset, size, 8 * 1024 * 1024)):
                with partial.open("ab") as output, chunk.open("rb") as source:
                    while data := source.read(1024 * 1024):
                        output.write(data)
                chunk.unlink()
                print(f"{destination.name}: {end + 1:,} / {size:,} bytes", flush=True)
        partial.replace(destination)
        return
    subprocess.run([
        "curl.exe", "-fsSL", "--retry", "3", "--retry-delay", "2",
        "--connect-timeout", "30", "--max-time", "1800",
        "--speed-limit", "1024", "--speed-time", "60",
        "--continue-at", "-", url, "-o", str(partial),
    ], check=True)
    partial.replace(destination)


def valid(path, size, digest, git_blob=False):
    if not path.is_file() or path.stat().st_size != size:
        return False
    checksum = hashlib.sha1() if git_blob else hashlib.sha256()
    if git_blob:
        checksum.update(f"blob {size}\0".encode())
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            checksum.update(chunk)
    return checksum.hexdigest() == digest


def main():
    metadata = ROOT / ".runtime" / "florence-files.json"
    if not metadata.is_file():
        download(f"https://huggingface.co/api/models/{REPOSITORY}/revision/{REVISION}?blobs=true", metadata)
    manifest = json.loads(metadata.read_text(encoding="utf-8"))
    if manifest["sha"] != REVISION:
        raise RuntimeError("Unexpected model revision")
    target = ROOT / "models" / "florence-base"
    for item in manifest["siblings"]:
        name = item["rfilename"]
        if not (name.endswith((".json", ".txt", ".safetensors")) or name == "README.md"):
            continue
        if Path(name).name != name:
            raise RuntimeError("Unexpected nested model path")
        path = target / name
        size = item["size"]
        is_blob = "lfs" not in item
        digest = item["blobId"] if is_blob else item["lfs"]["sha256"]
        if not valid(path, size, digest, is_blob):
            print(f"Downloading Florence-2: {name} ({size // 1024} KB)", flush=True)
            download(f"https://huggingface.co/{REPOSITORY}/resolve/{REVISION}/{name}?download=true", path, size)
            if not valid(path, size, digest, is_blob):
                raise RuntimeError(f"Integrity verification failed: {name}")
    (target / ".complete").write_text(REVISION)
    lama = ROOT / "models" / "torch" / "hub" / "checkpoints" / "big-lama.pt"
    digest = "344c77bbcb158f17dd143070d1e789f38a66c04202311ae3a258ef66667a9ea9"
    if not valid(lama, 205669692, digest):
        print("Downloading LaMA (196 MB)...", flush=True)
        download("https://github.com/Sanster/models/releases/download/add_big_lama/big-lama.pt?download=true", lama, 205669692)
        if not valid(lama, 205669692, digest):
            raise RuntimeError("LaMA integrity verification failed")
    print("Model downloads verified.", flush=True)


if __name__ == "__main__":
    main()
