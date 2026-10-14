"""Optional end-to-end smoke test: python tests/browser_qa.py (requires Playwright Chromium)."""
import os
import subprocess
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def assembled_html():
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    html=html.replace('<link rel="stylesheet" href="styles.css">', '<style>'+ (ROOT/'styles.css').read_text(encoding='utf-8')+'</style>')
    html=html.replace('<script defer src="data/corpus.js"></script><script defer src="app.js"></script>', '<script>'+(ROOT/'data/corpus.js').read_text(encoding='utf-8')+'</script><script>'+(ROOT/'app.js').read_text(encoding='utf-8')+'</script>')
    return html

try:
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True, executable_path="/usr/bin/chromium", args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1470,'height':1000},device_scale_factor=1)
        errors=[]
        page.on('pageerror',lambda e: errors.append(str(e)))
        page.set_content(assembled_html(),wait_until='load')
        page.locator('.graph-node').first.wait_for()
        assert page.locator('.graph-node').count()==21, page.locator('.graph-node').count()
        assert page.locator('.claim-card').count()==5
        assert '42%' in page.locator('#inspectorContent').inner_text()
        page.get_by_role('button',name='Trace the 42% claim').click()
        assert '42%' in page.locator('#inspectorContent').inner_text()
        page.locator('[data-card="c1"]').click()
        assert '€8.4m' in page.locator('#inspectorContent').inner_text()
        page.locator('[data-select-source="s2"]').first.click()
        assert 'Quarterly Outlay Note' in page.locator('#inspectorContent').inner_text()
        page.locator('[data-select-claim="c1"]').click()
        page.locator('#reviewInput').fill('Verify audited outlays before publication.')
        page.get_by_role('button',name='Save review note').click()
        assert 'Clear note' in page.locator('#inspectorContent').inner_text()
        page.locator('#claimSearch').fill('near misses')
        assert page.locator('.claim-card').count()==1
        page.locator('#claimSearch').fill('')
        page.get_by_role('button',name='Review needed').click()
        assert page.locator('.claim-card').count()==4
        page.get_by_role('button',name='Review needed').click()
        page.locator('[data-graph="sources"]').click()
        assert page.locator('[data-graph="sources"]').get_attribute('class').endswith('active')
        page.locator('#resetGraph').click()
        assert page.locator('[data-graph="all"]').get_attribute('class').endswith('active')
        with page.expect_download() as download_info:
            page.locator('#exportButton').click()
        dl=download_info.value
        assert dl.suggested_filename=='safetrace-case-001-brief.md'
        dl.save_as(str(ROOT/'sample-export.md'))
        assert 'Verify audited outlays before publication.' in (ROOT/'sample-export.md').read_text()
        page.screenshot(path=str(ROOT/'desktop-preview.png'),full_page=True)
        mobile=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1)
        mobile.set_content(assembled_html(),wait_until='load')
        assert mobile.locator('.graph-node').count()==21
        assert mobile.evaluate('document.documentElement.scrollWidth <= window.innerWidth+2'), mobile.evaluate('document.documentElement.scrollWidth')
        mobile.screenshot(path=str(ROOT/'mobile-preview.png'),full_page=True)
        assert not errors,errors
        print('Browser QA OK: 21 graph nodes, 5 claims, source inspection, review notes, filters, graph modes, export, mobile, 0 JS errors')
        browser.close()
finally:
    pass
