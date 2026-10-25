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


def parse_range(s: str, total: int) -> tuple[int, int]:
    s = s.strip().replace(" ", "")
    if "-" not in s:
        raise ValueError("Use format start-end, e.g. 2-9")
    parts = s.split("-")
    if len(parts) != 2:
        raise ValueError("Use format start-end, e.g. 2-9")
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
    return start, end


def pages_overlap(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return not (a[1] < b[0] or b[1] < a[0])


def used_pages(ranges: list[tuple[int, int]]) -> set[int]:
    used: set[int] = set()
    for s, e in ranges:
        used.update(range(s, e + 1))
    return used


def format_skipped(skipped: list[int]) -> str:
    if not skipped:
        return ""
    chunks = []
    a = prev = skipped[0]
    for p in skipped[1:]:
        if p == prev + 1:
            prev = p
        else:
            chunks.append(f"{a}-{prev}" if a != prev else str(a))
            a = prev = p
    chunks.append(f"{a}-{prev}" if a != prev else str(a))
    return ", ".join(chunks)


def safe_filename(name: str) -> str:
    name = name.strip()
    if not name:
        return ""
    if name.lower().endswith(".pdf"):
        name = name[:-4]
    for ch in '<>:"/\\|?*':
        name = name.replace(ch, "_")
    return name.strip(" .") or ""


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py /path/to/folder")
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
    range_num = 1
    while True:
        used = used_pages(ranges)
        free = total - len(used)
        if free == 0:
            print("\nAll pages covered.")
            break
        print(f"\nPages free: {free} of {total}")
        if ranges:
            print(f"Already selected: {', '.join(f'{s}-{e}' for s, e in ranges)}")
        try:
            prompt = f"Enter range {range_num} (e.g. 2-9)"
            if ranges:
                prompt += ", or 'done' to finish"
            prompt += ": "
            raw = input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.")
            sys.exit(0)
        if not raw:
            continue
        if ranges and raw.lower() in ("done", "d", "n", "no", "stop", "finish"):
            break
        try:
            start, end = parse_range(raw, total)
            new = (start, end)
            for existing in ranges:
                if pages_overlap(new, existing):
                    raise ValueError(f"Overlaps with already selected {existing[0]}-{existing[1]}")
            ranges.append(new)
            range_num += 1
        except ValueError as e:
            print(f"  Error: {e}")
    if not ranges:
        print("No ranges selected. Nothing to do.")
        sys.exit(0)
    ranges.sort(key=lambda r: r[0])
    used = used_pages(ranges)
    skipped = sorted(set(range(1, total + 1)) - used)
    print("\n--- Summary ---")
    for i, (s, e) in enumerate(ranges, 1):
        print(f"  Part {i}: pages {s}-{e} ({e - s + 1} pages)")
    if skipped:
        print(f"  Skipped: {format_skipped(skipped)} ({len(skipped)} pages)")
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
    custom_names: list[str] = []
    print("\nOptional custom names (press Enter to keep default):")
    for i, (start, end) in enumerate(ranges, 1):
        default = f"{base}_part{i:02d}_p{start}-{end}"
        try:
            raw = input(f"  Part {i} [{default}]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nCancelled.")
            sys.exit(0)
        name = safe_filename(raw) if raw else default
        if not name:
            name = default
        custom_names.append(name)
    print(f"\nWriting to {out_dir}")
    for (start, end), name in zip(ranges, custom_names):
        writer = PdfWriter()
        for p in range(start - 1, end):
            writer.add_page(reader.pages[p])
        out_path = out_dir / f"{name}.pdf"
        n = 1
        while out_path.exists():
            out_path = out_dir / f"{name}_{n}.pdf"
            n += 1
        with open(out_path, "wb") as f:
            writer.write(f)
        size_mb = out_path.stat().st_size / (1024 * 1024)
        print(f"  Created: {out_path.name} ({size_mb:.2f} MB, {end - start + 1} pages)")
    print("\nDone.")


if __name__ == "__main__":
    main()
