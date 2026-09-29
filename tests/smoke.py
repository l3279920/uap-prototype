#!/usr/bin/env python3
"""End-to-end smoke checks for the Field Index prototype."""
from __future__ import annotations
import argparse, contextlib, functools, http.server, socketserver, threading, time
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
CASES=['mcminnville','tremonton','socorro','michigan','rendlesham','jal','aguadilla','gimbal']
class Server(socketserver.ThreadingMixIn,socketserver.TCPServer):
 allow_reuse_address=True;daemon_threads=True
 def handle_error(self,request,client_address): pass
@contextlib.contextmanager
def server(port):
 handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT))
 try:
  srv=Server(('127.0.0.1',port),handler)
 except OSError:
  yield; return
 thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start();time.sleep(.15)
 try: yield
 finally: srv.shutdown();srv.server_close()
def issue_watch(page,base):
 issues=[]
 page.on('console',lambda m: issues.append(f'console {m.type}: {m.text}') if m.type=='error' else None)
 page.on('pageerror',lambda e: issues.append(f'pageerror: {e}'))
 page.on('request',lambda r: issues.append(f'external request: {r.url}') if not r.url.startswith(base) and not r.url.startswith('blob:') else None)
 page.on('requestfailed',lambda r: issues.append(f'failed request: {r.url} {r.failure}') if r.failure!='net::ERR_ABORTED' else None)
 return issues
def no_overflow(page):
 assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),f"horizontal overflow: {page.evaluate('document.documentElement.scrollWidth')} > {page.evaluate('window.innerWidth')}"
def open_case(page,cid):
 page.get_by_test_id('home-button').click();page.get_by_test_id(f'open-case-{cid}').click();assert page.locator('[data-testid^="record-"]').count() >= 3;no_overflow(page)
def exercise_generic(page,cid):
 open_case(page,cid)
 records=page.locator('[data-testid^="record-"]'); assert records.count()>=3
 view=page.locator('[data-testid^="view-"]').first;view.click();expect(page.locator('#recordDialog')).to_be_visible();page.get_by_test_id('close-record').click()
 checks=page.locator('#compareArea input[type=checkbox]');checks.nth(0).check();checks=page.locator('#compareArea input[type=checkbox]');checks.nth(1).check();page.get_by_test_id('comparison-note').fill('These records differ in date, purpose, and distance from the reported event.');page.get_by_test_id('save-comparison').click();expect(page.locator('.comparison-entry')).to_have_count(1)
def aguadilla_flow(page):
 open_case(page,'aguadilla')
 for rid in ['ag-video','ag-provenance','ag-aaro','ag-weather','ag-scu']:
  page.get_by_test_id(f'view-{rid}').click();page.get_by_test_id('close-record').click()
 page.locator('[data-weather="0"]').click();page.locator('[data-weather="1"]').click();page.locator('[data-weather="2"]').click();expect(page.get_by_test_id('weather-gap')).to_be_visible();expect(page.get_by_test_id('weather-gap')).to_contain_text('3h32m');expect(page.get_by_test_id('weather-gap')).to_contain_text('2h32m');expect(page.get_by_test_id('weather-gap')).to_contain_text('1h32m');expect(page.get_by_test_id('weather-gap')).to_contain_text('no post-event observation');expect(page.get_by_test_id('weather-gap')).to_contain_text('does not bracket')
 page.get_by_test_id('check-motion').click();page.get_by_test_id('check-claims').click();expect(page.get_by_test_id('claims-finding')).to_be_visible()
 checks=page.locator('#compareArea input[type=checkbox]');checks.nth(2).check();checks=page.locator('#compareArea input[type=checkbox]');checks.nth(4).check();page.get_by_test_id('comparison-note').fill('AARO and SCU rely on different scene geometry and speed assumptions; neither is a second observation.');page.get_by_test_id('save-comparison').click()
 form=page.get_by_test_id('conclusion-form');form.locator('[name=position]').select_option(label='Evidence remains insufficient');form.locator('[name=support]').fill('The official video and provenance establish the recording and release chain.');form.locator('[name=conflict]').fill('AARO and civilian analyses disagree about path, speed, and apparent water interaction.');form.locator('[name=weakness]').fill('The inferred path depends on aircraft, sensor, and scene reconstruction inputs.');form.locator('[name=missing]').fill('No exact-time wind observation exists at the modeled object altitude and position.');form.locator('[name=trigger]').fill('Synchronized original telemetry and independently verified sensor geometry would prompt revision.');page.get_by_test_id('save-conclusion').click();expect(page.get_by_test_id('saved-conclusion')).to_be_visible()
def seed_tremonton_conclusion(page):
 open_case(page,'tremonton');form=page.get_by_test_id('conclusion-form');form.locator('[name=support]').fill('The film and Condon record establish one underlying observation and its later analysis.');form.locator('[name=conflict]').fill('Interpretations differ on birds and unresolved image behavior.');form.locator('[name=weakness]').fill('Version lineage and image generations limit comparison.');form.locator('[name=missing]').fill('The camera-original generation and complete custody history are not present.');form.locator('[name=trigger]').fill('A demonstrably earlier-generation film with documented custody would prompt revision.');page.get_by_test_id('save-conclusion').click()
def release_flow(page):
 seed_tremonton_conclusion(page);page.get_by_test_id('release-nav').click();expect(page.get_by_test_id('release-metadata')).to_contain_text('79,823,577')
 page.get_by_test_id('inspect-release').click();page.get_by_test_id('sync-seek').fill('24');expect(page.get_by_test_id('sync-time')).to_have_text('00:24');page.get_by_test_id('complete-version-compare').click();page.locator('input[value=same-version]').check();page.get_by_test_id('relationship-reason').fill('Matching event date, place, duration, and imagery indicate the same underlying film; resolution and publication chain differ.');page.get_by_test_id('save-relationship').click();expect(page.get_by_test_id('release-result')).to_contain_text('does not increase');page.get_by_test_id('reopen-tremonton').click();expect(page.get_by_test_id('saved-conclusion')).to_be_visible();expect(page.locator('.case-title')).to_contain_text('REOPENED')
def run(base):
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True)
  for name,viewport in [('desktop',{'width':1440,'height':900}),('mobile',{'width':390,'height':844})]:
   context=browser.new_context(viewport=viewport);page=context.new_page();issues=issue_watch(page,base);page.goto(base,wait_until='networkidle');expect(page.locator('[data-testid^="case-card-"]')).to_have_count(8);no_overflow(page)
   for cid in CASES: exercise_generic(page,cid)
   page.evaluate("localStorage.clear()");page.reload();aguadilla_flow(page);page.reload();page.get_by_test_id('open-case-aguadilla').click();expect(page.get_by_test_id('saved-conclusion')).to_be_visible();release_flow(page);no_overflow(page)
   assert not issues,'\n'.join(issues);context.close();print(f'PASS {name}: 8 cases, Aguadilla, PR159, persistence, requests, overflow')
  browser.close()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--port',type=int,default=8765);ap.add_argument('--no-server',action='store_true');a=ap.parse_args();base=f'http://127.0.0.1:{a.port}/prototype/'
 if a.no_server: run(base)
 else:
  with server(a.port): run(base)
if __name__=='__main__': main()
