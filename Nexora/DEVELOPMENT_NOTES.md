# Nexora KPI — notes for future edits

## Current release

- Latest patched visual: `nexoraKPI_5.9.7.0_patched.pbiviz`
- Latest commit: `cbfec55 Fix Nexora target cross-highlighting`
- Branch: `main`
- The build is pushed to `origin/main`.

## Build architecture

- The editable source is not a TypeScript project. The original visual is the bundled
  `nexoraKPI74A92BB1DAE480BBC09C4B425BA7001.5.9.1.0.pbiviz`.
- `rebuild_visual.py` reads the original archive, patches its embedded JavaScript/CSS,
  updates capabilities and resources, and writes the next `.pbiviz` archive.
- Do not edit the generated `.pbiviz` by hand. Make changes in `rebuild_visual.py`,
  rebuild, inspect the archive, and commit the generated artifact.
- The current generated resource GUID is
  `nexoraKPI7B4E1D9A6C2F4380B5E7A1D3C9F62480`.

## Important fix: Target and external selections

Power BI can keep the full `values` array and provide the selected portion in
`highlights` during cross-highlighting. The main Value measure already used the
highlighted array, but Target previously read only `u.values`, so Target stayed at
the unselected value when another visual was selected.

The current Target extraction uses:

```js
const values = u.values || [];
const effective = u.highlights && u.highlights.length === values.length
    ? u.highlights
    : values;
```

If Target behavior is changed later, preserve this distinction. Also remember that
`ALL()`/`REMOVEFILTERS()` inside the user’s DAX measure can intentionally ignore
filters; that is separate from the visual-side fix.

## Features added across the patched releases

- Russian localization and Russian-first labels/resources.
- Target label measure (`targetLabel`) evaluated in the current context.
- Three context-aware back-note measures: `note`, `note2`, and `note3`.
- Target label position, size and color settings.
- Gauge delta position and delta font-size settings.
- Persisted gradient setting under `gradientBackground.enabled`.
- Keyboard semantics/selection for the card, tooltip identities, zero-comparison guard,
  and cleanup of the value animation frame.
- External landing links removed from the generated visual.

## Verification checklist

After changing the patch script:

1. Run `python3 Nexora/rebuild_visual.py`.
2. Run `unzip -t Nexora/nexoraKPI_<version>_patched.pbiviz`.
3. Confirm the embedded JavaScript contains the Target `highlights` fallback and has
   no duplicate old Target extraction block.
4. Run `node --check` against the embedded JavaScript when possible.
5. Test in Power BI with a slicer/report filter and with a selection in another visual.

## Repository safety

- Preserve existing user changes and unrelated generated artifacts.
- Do not use destructive Git commands such as `git reset --hard` or `git checkout --`
  without explicit approval.
