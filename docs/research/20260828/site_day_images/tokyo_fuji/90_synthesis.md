# Tokyo + Fuji day-sheet image recommendations

## Recommended set

| Priority | Place / route day | Stable Commons file page | Direct download / web-size URL | Attribution and license | Editorial use |
|---|---|---|---|---|---|
| 1 | **Day 01 — Shinjuku** | [Night in Shinjuku.JPG](https://commons.wikimedia.org/wiki/File:Night_in_Shinjuku.JPG) | [1920 px](https://commons.wikimedia.org/wiki/Special:Redirect/file/Night_in_Shinjuku.JPG?width=1920) · [original](https://commons.wikimedia.org/wiki/Special:Redirect/file/Night_in_Shinjuku.JPG) | Martin Falbisoner · CC BY-SA 3.0 | Premium night-energy opener; wide, high resolution, already assessed as a Wikimedia Quality Image. |
| 2 | **Day 02 — Asakusa / Sensō-ji** | [Main building, Sensoji Temple, Asakusa, Tokyo.jpg](https://commons.wikimedia.org/wiki/File:Main_building,_Sensoji_Temple,_Asakusa,_Tokyo.jpg) | [1600 px](https://commons.wikimedia.org/wiki/Special:Redirect/file/Main_building%2C_Sensoji_Temple%2C_Asakusa%2C_Tokyo.jpg?width=1600) · [original](https://commons.wikimedia.org/wiki/Special:Redirect/file/Main_building%2C_Sensoji_Temple%2C_Asakusa%2C_Tokyo.jpg) | Daderot · public domain | Clean place-identification image; keep as the calm daylight counterpoint to Akihabara. |
| 3 | **Day 02 — Akihabara** | [Akihabara Night.jpg](https://commons.wikimedia.org/wiki/File:Akihabara_Night.jpg) | [1920 px](https://commons.wikimedia.org/wiki/Special:Redirect/file/Akihabara_Night.jpg?width=1920) · [original](https://commons.wikimedia.org/wiki/Special:Redirect/file/Akihabara_Night.jpg) | Lars Heineken / ElHeineken · CC BY 4.0 | Use the complete streetscape or only a mild crop. Commons warns that billboards are de minimis only in the wider scene; do not isolate a single copyrighted ad/character. |
| 4 | **Day 03 — Shibuya / JoJo area** | [Shibuya Crossing.jpg](https://commons.wikimedia.org/wiki/File:Shibuya_Crossing.jpg) | [1920 px](https://commons.wikimedia.org/wiki/Special:Redirect/file/Shibuya_Crossing.jpg?width=1920) · [original](https://commons.wikimedia.org/wiki/Special:Redirect/file/Shibuya_Crossing.jpg) | Landry Miguel · CC BY-SA 4.0 | Cinematic wide night view that represents the Shibuya block without leaning on copyrighted JoJo character art. |
| 5 | **Day 04 + optional Day 05 morning — Lake Kawaguchiko / Fuji** | [Mount Fuji from Lake Kawaguchi (2015-10-26).jpg](https://commons.wikimedia.org/wiki/File:Mount_Fuji_from_Lake_Kawaguchi_(2015-10-26).jpg) | [1920 px](https://commons.wikimedia.org/wiki/Special:Redirect/file/Mount_Fuji_from_Lake_Kawaguchi_%282015-10-26%29.jpg?width=1920) · [original](https://commons.wikimedia.org/wiki/Special:Redirect/file/Mount_Fuji_from_Lake_Kawaguchi_%282015-10-26%29.jpg) | Alpsdake · CC BY-SA 4.0 | Best literal lake-and-Fuji image, with reflection. Reuse as the main Day 04 visual; Day 05 can reference it as a smaller continuation rather than adding another large photo. |
| 6 | **Day 04/05 backup — Fujikawaguchiko transit context** | [Fujikawaguchiko view of Mt. Fuji.jpg](https://commons.wikimedia.org/wiki/File:Fujikawaguchiko_view_of_Mt._Fuji.jpg) | [1920 px](https://commons.wikimedia.org/wiki/Special:Redirect/file/Fujikawaguchiko_view_of_Mt._Fuji.jpg?width=1920) · [original](https://commons.wikimedia.org/wiki/Special:Redirect/file/Fujikawaguchiko_view_of_Mt._Fuji.jpg) | Harperawl / structured creator SpikyLlama · CC0 1.0 | Flexible crop/optimization backup with Fujikyu railway context; useful if Day 05 needs its own secondary visual. |

## Compact attribution strings

- `Night in Shinjuku — Martin Falbisoner, CC BY-SA 3.0, via Wikimedia Commons.`
- `Sensō-ji main hall — Daderot, public domain, via Wikimedia Commons.`
- `Akihabara Night — Lars Heineken (ElHeineken), CC BY 4.0, via Wikimedia Commons; resized/cropped if applicable.`
- `Shibuya Crossing — Landry Miguel, CC BY-SA 4.0, via Wikimedia Commons; resized/cropped if applicable.`
- `Mount Fuji from Lake Kawaguchi — Alpsdake, CC BY-SA 4.0, via Wikimedia Commons; resized/cropped if applicable.`
- `Fujikawaguchiko view of Mt. Fuji — Harperawl / SpikyLlama, CC0 1.0, via Wikimedia Commons.`

## Implementation guidance for the parent task

- Keep the day sheet restrained: one dominant image per day; Day 02 may use two compact 3:2 tiles because it genuinely contains two visually distinct halves (Sensō-ji and Akihabara).
- Download images locally and generate optimized 1600–1920 px AVIF/WebP variants; do not hotlink full-resolution files.
- Lazy-load detail images and load only the selected day's assets when the sheet opens.
- Preserve a small credits block/link inside the day sheet or site footer. For BY-SA images, show author, license and source-page link, and indicate crops/resizing.
- Avoid a character-specific JoJo image unless a separately cleared promotional asset is available; the Shibuya city image communicates the plan naturally and avoids copyrighted-art complications.

## Traceability

All recommendations and license notes above are synthesized from the persisted source checkpoints in [20_sources.md](./20_sources.md), with alternatives recorded in [10_discovery.md](./10_discovery.md).
