# PDF Splitter

Local interactive tool to split a large PDF into smaller files by page ranges.

No upload limits, no sign-ins, no online tools.

## Why

Online PDF splitters often gate large files behind accounts or size caps. This runs entirely on your machine.

## Requirements

- Python 3.9+
- `pypdf`

```bash
pip install -r requirements.txt
```

## Usage

1. Put **exactly one** PDF in a folder.
2. Run:

```bash
python main.py /path/to/folder
```

3. The tool reports the total page count.
4. Enter any page ranges you want (1-based). They do not have to start at 1 or be contiguous. Overlaps are rejected. Type `done` when finished.
5. Confirm. Optionally give each part a custom name (Enter keeps the default).
6. Output is written to a `*_split` subfolder. Skipped pages are not written.

### Example

```
Found: report.pdf
Total pages: 1000

Pages free: 1000 of 1000
Enter range 1 (e.g. 2-9): 2-200

Pages free: 801 of 1000
Already selected: 2-200
Enter range 2 (e.g. 2-9), or 'done' to finish: 500-600

Pages free: 700 of 1000
Already selected: 2-200, 500-600
Enter range 3 (e.g. 2-9), or 'done' to finish: done

--- Summary ---
  Part 1: pages 2-200 (199 pages)
  Part 2: pages 500-600 (101 pages)
  Skipped: 1, 201-499, 601-1000 (700 pages)

Confirm and split? [y/N]: y

Optional custom names (press Enter to keep default):
  Part 1 [report_part01_p2-200]: intro
  Part 2 [report_part02_p500-600]: middle

Writing to .../report_split
  Created: intro.pdf (...)
  Created: middle.pdf (...)

Done.
```

## Rules enforced

- Pages are 1-based.
- Ranges can be any non-overlapping intervals (order does not matter; they are sorted for the summary).
- Type `done` (or `d` / `stop`) after at least one range to finish.
- Folder must contain exactly one PDF.
- Default output names include part number and page range. Custom names are optional and sanitized.

## License

MIT
