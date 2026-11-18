// DOM contract test only: no browser automation or native rendering claims.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const load=p=>JSON.parse(readFileSync(new URL('../data/'+p,import.meta.url),'utf8'));
class Element{constructor(){this.innerHTML='';this.textContent='';this.style={};this.hidden=true;this.clientWidth=600;this.clientHeight=440;this.events={};}addEventListener(n,f){this.events[n]=f;}}
const nodes=new Map(),node=id=>{if(!nodes.has(id))nodes.set(id,new Element());return nodes.get(id);},events={};
globalThis.document={querySelector:node,getElementById:node,addEventListener:(n,f)=>events[n]=f};
globalThis.window={addEventListener:(n,f)=>events[n]=f};
globalThis.location={hash:''};globalThis.requestAnimationFrame=f=>f();
globalThis.fetch=async url=>({ok:true,json:async()=>load(url.endsWith('world.json')?'world.json':'snapshot.json')});
await import('../app.js');
function navigate(hash){location.hash=hash;events.hashchange();}
function click(dataset={},attrs=[]){node('main').events.click({target:{closest:()=>({dataset,hasAttribute:n=>attrs.includes(n)})}});events.hashchange();}
function change(field,value){node('main').events.change({target:{dataset:{field},value}});events.hashchange();}
test('initial application renders the actual Cu/2025 supply cards and SVG hosts',()=>{assert.match(node('main').innerHTML,/23,227\.0 kt/);assert.match(node('main').innerHTML,/Country shares/);assert.ok([...nodes.values()].some(n=>n.innerHTML.startsWith('<svg')));assert.doesNotMatch(node('main').innerHTML,/undefined|NaN/);});
test('material/year controls update state and return the documented lithium values',()=>{click({material:'Li'});click({year:'2030'});assert.match(location.hash,/material=Li/);assert.match(location.hash,/year=2030/);assert.match(node('main').innerHTML,/540\.2 kt/);assert.match(node('main').innerHTML,/0\.185 – 0\.198/);});
test('trade controls switch reporter and basis without combining national and bloc totals',()=>{navigate('#trade');assert.match(node('main').innerHTML,/86\.6%/);change('reporter','EU27_2020');assert.match(node('main').innerHTML,/92\.7%/);change('basis','product_mass');assert.match(location.hash,/basis=product_mass/);assert.match(node('main').innerHTML,/product tonnes/);assert.doesNotMatch(node('main').innerHTML,/undefined|NaN/);});
test('risk material buttons can return to the six-material comparison',()=>{navigate('#risk?year=2025');assert.match(node('main').innerHTML,/0\.892/);click({material:'Ni'});assert.doesNotMatch(node('main').innerHTML,/0\.892/);click({material:'Ni'});assert.match(location.hash,/material=All/);assert.match(node('main').innerHTML,/0\.892/);});
test('outlook renders three scenarios and the graphite toggle changes its exact definition',()=>{navigate('#outlook?material=Li&year=2040&allGrades=false');assert.match(node('main').innerHTML,/932\.5 kt/);assert.match(node('main').innerHTML,/765\.3/);click({material:'C'});assert.match(node('main').innerHTML,/IEA Graphite; distinct from all grades/);click({},['data-toggle']);assert.match(location.hash,/allGrades=true/);assert.match(node('main').innerHTML,/IEA all grades graphite/);assert.match(node('main').innerHTML,/aria-checked="true"/);assert.doesNotMatch(node('main').innerHTML,/undefined|NaN/);});
