import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def find_pdf(folder: Path) -> Path:
    candidates = set()
    for pattern in ("*.pdf", "*.PDF"):
        for p in folder.glob(pattern):
            if p.is_file():
                candidates.add(p.resolve())
    candidates = sorted(candidates)
    if len(candidates) == 0:
        print(f"No PDF found in {folder}")
        sys.exit(1)
    if len(candidates) > 1:
        print(f"Multiple PDFs found in {folder}. Put exactly one PDF.")
        for p in candidates:
            print(f"  - {p.name}")
        sys.exit(1)
    return candidates[0]


def parse_range(s: str, total: int, next_start: int) -> tuple[int, int]:
    s = s.strip().replace(" ", "")
    if "-" not in s:
        raise ValueError("Use format start-end, e.g. 1-200")
    parts = s.split("-")
    if len(parts) != 2:
        raise ValueError("Use format start-end, e.g. 1-200")
    try:
        start = int(parts[0])
        end = int(parts[1])
    except ValueError:
        raise ValueError("Start and end must be integers")
    if start < 1:
        raise ValueError("Pages start at 1")
    if end > total:
        raise ValueError(f"End page {end} exceeds total pages {total}")
    if start > end:
        raise ValueError("Start must be <= end")
    if start != next_start:
        raise ValueError(f"Next range must start at page {next_start}")
    return start, end


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python pdf_splitter.py /path/to/folder")
        print("Folder must contain exactly one PDF file.")
        sys.exit(1)
    folder = Path(sys.argv[1]).expanduser().resolve()
    if not folder.is_dir():
        print(f"Not a directory: {folder}")
        sys.exit(1)
    pdf_path = find_pdf(folder)
    print(f"Found: {pdf_path.name}")
    try:
        reader = PdfReader(str(pdf_path))
    except Exception as e:
        print(f"Failed to open PDF: {e}")
        sys.exit(1)
    total = len(reader.pages)
    print(f"Total pages: {total}")
    if total == 0:
        print("PDF has 0 pages.")
        sys.exit(1)
    ranges: list[tuple[int, int]] = []
    next_start = 1
    range_num = 1
    while next_start <= total:
        remaining = total - next_start + 1
        print(f"\nPages left: {remaining} (from {next_start} to {total})")
        while True:
            try:
                raw = input(
                    f"Enter range {range_num} (e.g. {next_start}-{min(next_start + 199, total)}): "
                ).strip()
                if not raw:
                    continue
                start, end = parse_range(raw, total, next_start)
                ranges.append((start, end))
                next_start = end + 1
                range_num += 1
                break
            except ValueError as e:
                print(f"  Error: {e}")
            except (KeyboardInterrupt, EOFError):
                print("\nCancelled.")
                sys.exit(0)
    print("\n--- Summary ---")
    for i, (s, e) in enumerate(ranges, 1):
        print(f"  Part {i}: pages {s}-{e} ({e - s + 1} pages)")
    try:
        confirm = input("\nConfirm and split? [y/N]: ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        sys.exit(0)
    if confirm not in ("y", "yes"):
        print("Cancelled.")
        sys.exit(0)
    base = pdf_path.stem
    out_dir = folder / f"{base}_split"
    out_dir.mkdir(exist_ok=True)
    print(f"\nWriting to {out_dir}")
    for i, (start, end) in enumerate(ranges, 1):
        writer = PdfWriter()
        for p in range(start - 1, end):
            writer.add_page(reader.pages[p])
        out_name = f"{base}_part{i:02d}_p{start}-{end}.pdf"
        out_path = out_dir / out_name
        with open(out_path, "wb") as f:
            writer.write(f)
        size_mb = out_path.stat().st_size / (1024 * 1024)
        print(f"  Created: {out_name} ({size_mb:.2f} MB, {end - start + 1} pages)")
    print("\nDone.")


if __name__ == "__main__":
    main()
