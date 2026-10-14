#!/usr/bin/env python3
"""Send one local picture or video to a Notion upload URL.

The Notion connector's create-file-upload call returns a short-lived
upload_url and an authorization header. This script does the one
multipart POST that finishes the upload, so the agent never hand-types
file bytes. Prints the Notion response as one JSON object.

Usage: python3 notion_upload.py --url <upload_url> --auth "<authorization header value>" --file <path>

Exit codes: 0 when Notion reports status "uploaded", 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path


def build_body(path: Path) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    head = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode()
    tail = f"\r\n--{boundary}--\r\n".encode()
    return head + path.read_bytes() + tail, f"multipart/form-data; boundary={boundary}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--auth", required=True, help="the authorization header value from upload_headers")
    parser.add_argument("--file", required=True)
    args = parser.parse_args()

    path = Path(args.file)
    if not path.is_file():
        print(json.dumps({"status": "error", "error": f"file not found: {path}"}))
        return 1

    body, content_type = build_body(path)
    request = urllib.request.Request(
        args.url,
        data=body,
        method="POST",
        headers={"Authorization": args.auth, "Content-Type": content_type},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.loads(response.read().decode() or "{}")
    except urllib.error.HTTPError as error:
        print(json.dumps({"status": "error", "http_status": error.code, "error": error.read().decode()[:500]}))
        return 1
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "error", "error": str(error)}))
        return 1

    print(json.dumps(result))
    return 0 if result.get("status") == "uploaded" else 1


if __name__ == "__main__":
    sys.exit(main())
