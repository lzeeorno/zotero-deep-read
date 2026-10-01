#!/usr/bin/env python3
"""Render manually prepared v3 semantic notes onto a new PDF copy."""
import argparse
import json
from pathlib import Path
import fitz

RED = (1, 0, 0)


def rect_on_page(value, page, field):
    r = fitz.Rect(value)
    if r.is_empty or r.is_infinite or not page.rect.contains(r):
        raise ValueError(f'{field}: invalid or outside page {page.number + 1}')
    return r


def overlaps(a, b):
    return not (a & b).is_empty


def annotate(source, notes_path, output, font=None, preview_dir=None):
    source, output = Path(source), Path(output)
    if output.exists() or source.resolve() == output.resolve():
        raise ValueError('Choose a new output path; preserve the source and existing files.')
    notes = json.loads(Path(notes_path).read_text(encoding='utf-8'))['notes']
    if not notes:
        raise ValueError('No semantic notes supplied.')
    doc = fitz.open(source)
    placements = {}
    try:
        for i, note in enumerate(notes, 1):
            note_id = f'N{i:02d}'
            page_number = note['page']
            if not isinstance(page_number, int) or not 1 <= page_number <= len(doc):
                raise ValueError(f'{note_id}: page must be a 1-based integer in the document.')
            page = doc[page_number - 1]
            box = rect_on_page(note['rect'], page, 'rect')
            badge = rect_on_page(note['badge_rect'], page, 'badge_rect')
            label = rect_on_page(note['label_rect'], page, 'label_rect')
            if badge.y1 > box.y0 or not (abs(badge.x0-box.x0) <= 12 or abs(badge.x1-box.x1) <= 12):
                raise ValueError(f'{note_id}: badge must be outside the upper left/right corner.')
            for r in (badge, label):
                if any(overlaps(r, fitz.Rect(w[:4])) for w in page.get_text('words')):
                    raise ValueError(f'{note_id}: badge/label overlaps page text; select empty space.')
                if any(overlaps(r, other) for other in placements.get(page_number, [])):
                    raise ValueError(f'{note_id}: badge/label overlaps another note placement.')
            if overlaps(badge, label):
                raise ValueError(f'{note_id}: badge and label overlap.')
            placements.setdefault(page_number, []).extend([badge, label])
            for field in ('label', 'subject', 'detail'):
                if not isinstance(note[field], str) or not note[field].strip():
                    raise ValueError(f'{note_id}: {field} must contain text.')
            fontname = 'deepread' if font else 'china-s'
            if font:
                page.insert_font(fontname=fontname, fontfile=str(font))
            remainder = page.insert_textbox(label, f'{note_id}｜{note["label"]}',
                fontsize=6.9, fontname=fontname, color=RED, overlay=True)
            if remainder < 0:
                raise ValueError(f'{note_id}: label does not fit; enlarge its empty rectangle or shorten it.')
            remainder = page.insert_textbox(badge, note_id, fontsize=6.4,
                fontname='hebo', color=RED, overlay=True)
            if remainder < 0:
                raise ValueError(f'{note_id}: badge does not fit.')
            annot = page.add_rect_annot(box)
            annot.set_colors(stroke=RED)
            annot.set_border(width=1.25)
            annot.set_info(title=f'{note_id} · Zotero Deep Read',
                subject=f'{note_id} · {note["subject"]}',
                content=f'【{note_id} · {note["subject"]}】\n\n{note["detail"]}')
            annot.update()
        output.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(output), garbage=4, deflate=True)
    finally:
        doc.close()
    with fitz.open(output) as check:
        for i, note in enumerate(notes, 1):
            page = check[note['page'] - 1]
            matching = [a for a in page.annots() or []
                        if a.info.get('subject') == f'N{i:02d} · {note["subject"]}']
            if len(matching) != 1 or note['detail'] not in matching[0].info['content']:
                raise ValueError(f'N{i:02d}: saved annotation content failed verification.')
        if preview_dir:
            preview = Path(preview_dir)
            preview.mkdir(parents=True, exist_ok=True)
            for p in sorted(placements):
                check[p - 1].get_pixmap(matrix=fitz.Matrix(1.55, 1.55), alpha=False,
                    annots=True).save(str(preview / f'page_{p:02d}.png'))
    print(json.dumps({'output': str(output.resolve()), 'notes': len(notes),
                      'annotated_pages': sorted(placements)}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('notes', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--font', type=Path)
    parser.add_argument('--preview-dir', type=Path)
    args = parser.parse_args()
    annotate(args.source, args.notes, args.output, args.font, args.preview_dir)


if __name__ == '__main__':
    main()
