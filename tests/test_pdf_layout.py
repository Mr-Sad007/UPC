from pathlib import Path
import pytest


def test_rendered_images_remain_inside_pages():
    fitz = pytest.importorskip('fitz')
    target = Path(__file__).resolve().parents[1]/'paper/paper.pdf'
    if not target.exists():
        pytest.skip('Paper is generated after numerical tests on a fresh checkout')
    doc = fitz.open(target)
    for page in doc:
        for item in page.get_images():
            for rect in page.get_image_rects(item[0]):
                assert rect.x0 >= 0 and rect.y0 >= 0
                assert rect.x1 <= page.rect.width and rect.y1 <= page.rect.height
