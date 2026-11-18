import test from 'node:test';
import assert from 'node:assert/strict';
import {fitViewport,SHEET} from '../layout.js';
test('complete report sheet fits common laptop viewports without either-axis overflow',()=>{
 for(const [width,height] of [[1280,600],[1280,720],[1366,624],[1440,780],[1512,864],[1728,950],[1920,1080]]){
  const fit=fitViewport(width,height);
  assert.ok(fit&&fit.scale>0);
  assert.ok(fit.width+2*SHEET.padding<=width+1e-8);
  assert.ok(fit.height+2*SHEET.padding<=height+1e-8);
  assert.ok(Math.abs(fit.width/fit.height-16/9)<1e-10);
 }
});
test('expanded details and phones retain readable natural document flow',()=>{
 assert.equal(fitViewport(1440,800,true),null);
 assert.equal(fitViewport(390,844),null);
 assert.equal(fitViewport(900,600),null);
 assert.equal(fitViewport(NaN,800),null);
});
