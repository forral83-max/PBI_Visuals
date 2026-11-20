#!/usr/bin/env python3
"""Build a local Pie Plume artifact with the watermark disabled.

The published ``Pie Plume.pbiviz`` is never modified.  This script creates a
separate ``Pie Plume_dev.pbiviz`` from it and applies one explicit, dev-only
patch to the embedded license helper.
"""

from __future__ import annotations

import json
import os
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Pie Plume.pbiviz"
OUTPUT = ROOT / "Pie Plume_1.0.0.2_dev.pbiviz"
RESOURCE = "resources/plumePieChartA98296CC7934459199F53486CD90BFCD.pbiviz.json"
DEV_VERSION = "1.0.0.2"


def main() -> None:
    with zipfile.ZipFile(SOURCE, "r") as source_zip:
        resource = json.loads(source_zip.read(RESOURCE))
        javascript = resource["content"]["js"]

        class_marker = "class n{visualId;state="
        watermark = "watermark(e){return e&&!this.state.licensed}"
        if javascript.count(class_marker) != 1:
            raise RuntimeError("license helper marker was not found exactly once")
        if javascript.count(watermark) != 1:
            raise RuntimeError("watermark helper was not found exactly once")

        javascript = javascript.replace(
            class_marker,
            "const DEV_LICENSE_MODE=!0;" + class_marker,
            1,
        ).replace(
            watermark,
            "watermark(e){return DEV_LICENSE_MODE?!1:e&&!this.state.licensed}",
            1,
        )
        footnote_start = "renderFootNote(e){"
        footnote_end = "tip("
        start = javascript.find(footnote_start)
        end = javascript.find(footnote_end, start)
        if start < 0 or end < 0 or javascript.find(footnote_start, start + 1) >= 0:
            raise RuntimeError("watermark footer block was not found exactly once")
        javascript = (
            javascript[:start]
            + 'renderFootNote(e){(0,l.HC)(this.footerEl);this.footerEl.style.display="none";(0,l.HC)(this.tilesEl);this.tilesEl.style.display="none"}'
            + javascript[end:]
        )
        resource["content"]["js"] = javascript
        resource["content"]["css"] += ".pl-watermark,.pl-wm-tiles,.pl-wm-hint,.pl-wm-sep{display:none!important;}"
        resource["visual"]["version"] = DEV_VERSION
        patched_resource = json.dumps(
            resource,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

        package = json.loads(source_zip.read("package.json"))
        package["version"] = DEV_VERSION
        package["visual"]["version"] = DEV_VERSION
        patched_package = json.dumps(
            package,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

        output_fd, output_name = tempfile.mkstemp(
            prefix="Pie Plume_dev.",
            suffix=".pbiviz",
            dir=ROOT,
        )
        os.close(output_fd)
        try:
            with zipfile.ZipFile(output_name, "w") as output_zip:
                for item in source_zip.infolist():
                    if item.filename == RESOURCE:
                        data = patched_resource
                    elif item.filename == "package.json":
                        data = patched_package
                    else:
                        data = source_zip.read(item)
                    output_zip.writestr(item, data)
            os.replace(output_name, OUTPUT)
        finally:
            if os.path.exists(output_name):
                os.unlink(output_name)

    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
