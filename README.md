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
python pdf_splitter.py /path/to/folder
```

3. The tool reports the total page count.
4. Enter sequential page ranges (1-based) until every page is covered.
5. Confirm. Output is written to a `*_split` subfolder.

### Example

```
Found: report.pdf
Total pages: 1000

Pages left: 1000 (from 1 to 1000)
Enter range 1 (e.g. 1-200): 1-200

Pages left: 800 (from 201 to 1000)
Enter range 2 (e.g. 201-400): 201-400

Pages left: 600 (from 401 to 1000)
Enter range 3 (e.g. 401-600): 401-1000

--- Summary ---
  Part 1: pages 1-200 (200 pages)
  Part 2: pages 201-400 (200 pages)
  Part 3: pages 401-1000 (600 pages)

Confirm and split? [y/N]: y

Writing to .../report_split
  Created: report_part01_p1-200.pdf (...)
  Created: report_part02_p201-400.pdf (...)
  Created: report_part03_p401-1000.pdf (...)

Done.
```

## Rules enforced

- Pages are 1-based.
- Ranges must be contiguous and sequential (no gaps, no overlaps).
- Folder must contain exactly one PDF.
- Output filenames include part number and page range.

## License

MIT
