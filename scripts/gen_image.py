# -*- coding: utf-8 -*-
"""Generate images with TRUE transparent backgrounds via the OpenAI image API.

Why gpt-image-1.5: it accepts background=transparent + output_format=png and returns a real alpha
channel. gpt-image-2 rejects background=transparent, so use 1.5 for cut-out characters/props/icons.

Two endpoints, auto-selected per job:
  - refs == []   -> POST /v1/images/generations  (text -> image, JSON body)
  - refs != []   -> POST /v1/images/edits         (reference-locked, multipart, input_fidelity=high)

stdlib only (urllib + manual multipart) — no `openai` package needed. Reads the key from the project
`.env` (OPENAI_API_KEY, optional OPENAI_BASE_URL), falling back to real environment variables.

Usage:
  1) edit JOBS below (or point JOBS at your own list),
  2) put your key in <project>/.env  ->  OPENAI_API_KEY=sk-...
  3) python gen_image.py            # generate all jobs
     python gen_image.py icon_wallet hero_1   # only these job names
Outputs land in <project>/out/<name>.png. Verify alpha with check_alpha.py.
"""
import base64, io, json, mimetypes, os, struct, sys, time, urllib.error, urllib.request, uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # adjust if the skill isn't at <project>/...
ENV_PATH = os.path.join(ROOT, ".env")
OUT_DIR = os.path.join(ROOT, "out")
MODEL = "gpt-image-1.5"
DEFAULT_BASE = "https://api.openai.com/v1"

# Transparency style block — APPEND to every prompt. Being explicit here is what actually yields a
# clean alpha cut-out instead of a baked-in backdrop.
STYLE = (
    "High-quality render, soft studio lighting, whole subject fully visible, nothing cropped. "
    "IMPORTANT: fully transparent background with alpha channel — no floor, no ground shadow, no "
    "backdrop, no checkerboard pattern, no glow or light halo around the subject: alpha must be fully "
    "transparent everywhere except the subject (and any props it holds) themselves."
)

# Each job: (name, size, refs, prompt). size in {1024x1024, 1024x1536, 1536x1024}.
# refs = [] -> generations (from text); refs = [paths] -> edits (keep identity across variations).
JOBS = [
    ("example_icon", "1024x1024", [],
     "Create a single app icon: a minimal neon wallet glyph, teal-on-dark, thick rounded strokes. " + STYLE),
    # ("hero_1", "1536x1024", [os.path.join(ROOT, "refs", "char.webp")],
    #  "Create a new image of <full character description reused verbatim>. New pose: <pose>. " + STYLE),
]


def load_env(path):
    env = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def png_info(data):
    """(w, h, color_type); color_type 6 == RGBA (has alpha)."""
    if data[:8] != b"\x89PNG\r\n\x1a\n" or len(data) < 26:
        return None
    w, h = struct.unpack(">II", data[16:24])
    return w, h, data[25]


def build_multipart(fields, files):
    boundary = uuid.uuid4().hex
    body = io.BytesIO()
    for name, value in fields:
        body.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    for name, path in files:
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        with open(path, "rb") as f:
            data = f.read()
        body.write(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; '
            f'filename="{os.path.basename(path)}"\r\nContent-Type: {ctype}\r\n\r\n'.encode())
        body.write(data + b"\r\n")
    body.write(f"--{boundary}--\r\n".encode())
    return boundary, body.getvalue()


def _post(url, api_key, data, headers):
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"Authorization": f"Bearer {api_key}", **headers})
    with urllib.request.urlopen(req, timeout=600) as resp:
        return json.loads(resp.read().decode("utf-8"))


def call(base_url, api_key, prompt, size, refs):
    base = base_url.rstrip("/")
    if refs:
        fields = [("model", MODEL), ("prompt", prompt), ("size", size), ("quality", "high"),
                  ("background", "transparent"), ("output_format", "png"),
                  ("input_fidelity", "high"), ("n", "1")]
        boundary, body = build_multipart(fields, [("image[]", p) for p in refs])
        return _post(base + "/images/edits", api_key, body,
                     {"Content-Type": f"multipart/form-data; boundary={boundary}"})
    payload = {"model": MODEL, "prompt": prompt, "size": size, "quality": "high",
               "background": "transparent", "output_format": "png", "n": 1}
    return _post(base + "/images/generations", api_key, json.dumps(payload).encode(),
                 {"Content-Type": "application/json"})


def main():
    only = set(sys.argv[1:])
    env = load_env(ENV_PATH)
    api_key = env.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY", "")
    base_url = env.get("OPENAI_BASE_URL") or os.environ.get("OPENAI_BASE_URL", "") or DEFAULT_BASE
    if not api_key:
        print(f"ERROR: OPENAI_API_KEY empty — put it in {ENV_PATH}")
        sys.exit(2)
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"model={MODEL}  base={base_url}  out={OUT_DIR}", flush=True)

    failures = []
    for name, size, refs, prompt in JOBS:
        if only and name not in only:
            continue
        missing = [p for p in refs if not os.path.exists(p)]
        if missing:
            print(f"[{name}] ERROR missing refs: {missing}"); failures.append((name, "missing refs")); continue
        out_path = os.path.join(OUT_DIR, f"{name}.png")
        for attempt in range(1, 4):
            t0 = time.time()
            try:
                print(f"[{name}] attempt {attempt} ({'edits' if refs else 'generations'}) ...", flush=True)
                result = call(base_url, api_key, prompt, size, refs)
                data = base64.b64decode(result["data"][0]["b64_json"])
                with open(out_path, "wb") as f:
                    f.write(data)
                info = png_info(data)
                alpha = "RGBA(alpha)" if info and info[2] == 6 else "NO-ALPHA?"
                print(f"[{name}] OK {time.time()-t0:.0f}s {len(data)//1024}KB {info[0]}x{info[1]} {alpha}", flush=True)
                break
            except urllib.error.HTTPError as e:
                detail = e.read().decode("utf-8", "replace")[:600]
                print(f"[{name}] HTTP {e.code}: {detail}", flush=True)
                retryable = e.code in (429, 500, 502, 503, 504) or (e.code == 400 and "moderation_blocked" in detail)
                if retryable and attempt < 3:
                    time.sleep(20 * attempt); continue
                failures.append((name, f"HTTP {e.code}")); break
            except Exception as e:  # noqa: BLE001
                print(f"[{name}] error: {e!r}", flush=True)
                if attempt < 3:
                    time.sleep(15); continue
                failures.append((name, repr(e))); break

    if failures:
        print("FAILED:", failures); sys.exit(1)
    print("done.")


if __name__ == "__main__":
    main()
