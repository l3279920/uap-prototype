#!/usr/bin/env python3
"""Drive real interactions and capture paired viewport-sized flow screenshots."""
from __future__ import annotations
import argparse, contextlib, functools, http.server, socketserver, threading, time
from pathlib import Path
from PIL import Image, ImageStat
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'prototype_screenshots'
VIEWPORTS={'desktop':{'width':1440,'height':900},'mobile':{'width':390,'height':844}}
class Server(socketserver.ThreadingMixIn,socketserver.TCPServer):
 allow_reuse_address=True;daemon_threads=True
 def handle_error(self,request,client_address): pass
@contextlib.contextmanager
def server(port):
 handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT));srv=Server(('127.0.0.1',port),handler);threading.Thread(target=srv.serve_forever,daemon=True).start();time.sleep(.15)
 try: yield
 finally:srv.shutdown();srv.server_close()
def snap(page,device,num,slug,focus=None,y=None):
 page.evaluate("document.activeElement && document.activeElement.blur()")
 if focus:
  target=page.locator(focus);target.scroll_into_view_if_needed();page.evaluate("([el,y])=>window.scrollBy(0,el.getBoundingClientRect().top-y)",[target.element_handle(),y or (78 if device=='mobile' else 88)])
 if page.locator('#toast.show').count(): page.wait_for_timeout(1900)
 page.wait_for_timeout(180)
 skip=page.locator('.skip').bounding_box();assert skip and skip['y']+skip['height']<=0,'skip link visible without focus'
 top=page.locator('.topbar').bounding_box();assert top and abs(top['y'])<1,'sticky header not at viewport top'
 rail=page.locator('.rail').bounding_box();vp=VIEWPORTS[device]
 assert rail and (abs(rail['y']-top['height'])<1 if device=='desktop' else abs(rail['y']+rail['height']-vp['height'])<1),'navigation not at expected viewport edge'
 path=OUT/f'{device}_{num:02d}_{slug}.png';page.screenshot(path=str(path),full_page=False);print(path.name)
def conclusion(page):
 f=page.get_by_test_id('conclusion-form');f.locator('[name=support]').fill('CBP provenance establishes an official recording and release; it does not identify the objects.');f.locator('[name=conflict]').fill('AARO and civilian reconstructions disagree about speed, separation, and apparent water interaction.');f.locator('[name=weakness]').fill('Every path estimate depends on scene geometry and sensor assumptions.');f.locator('[name=missing]').fill('The bundled weather extract has no post-event observation; synchronized platform telemetry is also unavailable.');f.locator('[name=trigger]').fill('Independently verified telemetry and sensor geometry would prompt revision.');page.get_by_test_id('save-conclusion').click()
def seed_tremonton(page):
 page.get_by_test_id('home-button').click();page.get_by_test_id('open-case-tremonton').click();f=page.get_by_test_id('conclusion-form');f.locator('[name=support]').fill('The film and later case record establish one underlying filmed observation.');f.locator('[name=conflict]').fill('Analyses differ over birds and unresolved image behavior.');f.locator('[name=weakness]').fill('Generation and custody history are incomplete.');f.locator('[name=missing]').fill('A camera-original generation with documented custody is absent.');f.locator('[name=trigger]').fill('An earlier documented generation would prompt revision.');page.get_by_test_id('save-conclusion').click()
def aguadilla(page,d):
 page.get_by_test_id('open-case-aguadilla').click();snap(page,d,1,'aguadilla_case_open','.case-header')
 for rid in ['ag-video','ag-provenance','ag-aaro']:
  page.get_by_test_id(f'view-{rid}').click()
  if rid=='ag-video':snap(page,d,2,'aguadilla_official_record')
  page.get_by_test_id('close-record').click()
 snap(page,d,3,'aguadilla_sources_viewed','[data-testid="record-ag-aaro"]')
 page.get_by_test_id('view-ag-weather').click();page.get_by_test_id('close-record').click()
 for i in range(3):page.locator(f'[data-weather="{i}"]').click()
 snap(page,d,4,'aguadilla_weather_gap','[data-testid="aguadilla-lab"]')
 page.get_by_test_id('check-motion').click();snap(page,d,5,'aguadilla_platform_motion','[data-testid="motion-finding"]',560 if d=='mobile' else 700)
 for rid in ['ag-scu','ag-lianza','ag-rebuttal']:
  page.get_by_test_id(f'view-{rid}').click();page.get_by_test_id('close-record').click()
 page.get_by_test_id('check-claims').click();snap(page,d,6,'aguadilla_disputed_claims','[data-testid="claims-finding"]',560 if d=='mobile' else 700)
 checks=page.locator('#compareArea input[type=checkbox]');checks.nth(2).check();checks=page.locator('#compareArea input[type=checkbox]');checks.nth(4).check();page.get_by_test_id('comparison-note').fill('These analyses use different geometry and interpret apparent occlusion differently.');page.get_by_test_id('save-comparison').click();snap(page,d,7,'aguadilla_comparison','.comparison-entry',620 if d=='mobile' else 700)
 conclusion(page);snap(page,d,8,'aguadilla_conclusion','[data-testid="saved-conclusion"]')
def release(page,d):
 seed_tremonton(page);page.get_by_test_id('release-nav').click();snap(page,d,9,'pr159_intake','.release-header')
 page.get_by_test_id('inspect-release').click();snap(page,d,10,'pr159_metadata','[data-testid="release-metadata"]')
 page.get_by_test_id('sync-seek').fill('24');snap(page,d,11,'pr159_sync_compare','[data-testid="version-comparison"]')
 page.get_by_test_id('complete-version-compare').click();snap(page,d,12,'pr159_relationship_options','[data-testid="release-form"]')
 page.locator('input[value=same-version]').check();page.get_by_test_id('relationship-reason').fill('The date, place, duration, and imagery match one underlying film; resolution and publication chain differ.');snap(page,d,13,'pr159_reason_authored','[data-testid="relationship-reason"]',600 if d=='mobile' else 700)
 page.get_by_test_id('save-relationship').click();snap(page,d,14,'pr159_archive_result','[data-testid="release-result"]')
 page.get_by_test_id('reopen-tremonton').click();focus='.case-header' if d=='mobile' else '[data-testid="saved-conclusion"]';snap(page,d,15,'tremonton_reopened',focus)
def validate():
 files=sorted(OUT.glob('*.png'));assert len(files)==30,f'expected 30 screenshots, found {len(files)}'
 for p in files:
  with Image.open(p) as im:
   device=p.name.split('_',1)[0];expected=(VIEWPORTS[device]['width'],VIEWPORTS[device]['height']);assert im.size==expected,f'wrong viewport dimensions: {p} {im.size} != {expected}'
   assert im.getbbox(),f'empty image: {p}';stat=ImageStat.Stat(im.convert('L'));assert stat.var[0]>100,f'visually blank: {p} variance={stat.var[0]:.1f}'
 print(f'PASS image validation: {len(files)} nonblank viewport PNG files')
def run(base):
 OUT.mkdir(exist_ok=True);[p.unlink() for p in OUT.glob('*.png')]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True)
  for d,vp in VIEWPORTS.items():
   page=browser.new_page(viewport=vp);page.goto(base,wait_until='networkidle');page.evaluate('localStorage.clear()');page.reload();aguadilla(page,d);release(page,d);page.close()
  browser.close()
 validate()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--port',type=int,default=8766);ap.add_argument('--no-server',action='store_true');a=ap.parse_args();base=f'http://127.0.0.1:{a.port}/prototype/'
 if a.no_server:run(base)
 else:
  with server(a.port):run(base)
if __name__=='__main__':main()
