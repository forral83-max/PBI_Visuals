## Local development build

The checked-in `Pie Plume.pbiviz` keeps the normal offline license validation.
To create a separate local development artifact without visual watermarks, run:

```bash
python3 "Pie Plum/build_dev.py"
```

The script writes `Pie Plum/Pie Plume_1.0.0.2_dev.pbiviz` and leaves
the published artifact unchanged. The development build has a compile-time `DEV_LICENSE_MODE`
flag and removes the watermark footer/tile rendering from the embedded visual.
It does not generate or accept a forged license key.
