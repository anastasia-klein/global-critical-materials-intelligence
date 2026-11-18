// Local SVG rendering. All displayed values come from core.js report queries.
import {safe,finite,COLORS} from './core.js';
export const number=(x,d=1)=>finite(x)?x.toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d}):'—';
export const percent=(x,d=1)=>finite(x)?number(x*100,d)+'%':'—';
export function compact(x){if(!finite(x))return '—';const a=Math.abs(x);return a>=1e9?number(x/1e9,1)+'bn':a>=1e6?number(x/1e6,1)+'m':a>=1e3?number(x/1e3,1)+'k':a>0&&a<1?number(x,Math.min(6,Math.ceil(-Math.log10(a))+1)):number(x,0);}
const tx=(x,y,t,cls='',extra='')=>`<text x="${x}" y="${y}" class="${cls}" ${extra}>${safe(t)}</text>`;
const ln=(x,y,a,b,cls='grid-line')=>`<line x1="${x}" y1="${y}" x2="${a}" y2="${b}" class="${cls}"/>`;
const tip=t=>`tabindex="0" data-tip="${safe(t)}" aria-label="${safe(t)}"`;
function size(host){return {w:Math.max(300,host.clientWidth),h:Math.max(200,host.clientHeight)};}
function draw(host,w,h,html,label){host.innerHTML=`<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${safe(label)}">${html}</svg>`;}
function ticks(max){const raw=Math.max(max,1e-9)/4,p=10**Math.floor(Math.log10(raw)),step=[1,2,2.5,5,10].map(v=>v*p).find(v=>v>=raw);return Array.from({length:Math.ceil(max/step)+1},(_,i)=>i*step);}
function label(host,w,h){draw(host,w,h,tx(w/2,h/2,'No observations returned for this selection','empty','text-anchor="middle"'),'No source observations');}
const countryName=s=>s==='Congo, The Democratic Republic of the'?'DR Congo':s==='Russian Federation'?'Russia':s;
function wrap(x,y,text,width){const words=countryName(text).split(' '),lines=[''];for(const word of words){const k=lines.length-1;if((lines[k]+' '+word).length*6.4>width&&lines[k])lines.push(word);else lines[k]+=(lines[k]?' ':'')+word;}return `<text x="${x}" y="${y-(lines.length-1)*6}" class="axis" text-anchor="end">${lines.map((s,i)=>`<tspan x="${x}" dy="${i?13:0}">${safe(s)}</tspan>`).join('')}</text>`;}
export function bars(host,rows,series,opts={}){const {w,h}=size(host),isPercent=opts.percent,left=Math.min(opts.left||160,w*.42),right=isPercent?55:76,top=10,bottom=35,pw=w-left-right,ph=h-top-bottom;
 const values=rows.flatMap(r=>r.values).filter(finite);if(!values.length)return label(host,w,h);
 const max=opts.max??(isPercent?Math.min(1,Math.max(...values)*1.1||1):Math.max(...values)*1.15||1);
 const ts=opts.hhi?[0,.2,.4,.6,.8,1]:isPercent?Array.from({length:5},(_,i)=>i*max/4):ticks(max);let html='';
 for(const t of ts){if(t>max)continue;const x=left+t/max*pw;html+=ln(x,top,x,h-bottom)+tx(x,h-10,opts.hhi?number(t,1):isPercent?percent(t,0):compact(t/(opts.scale||1)),'axis','text-anchor="middle"');}
 const rh=ph/rows.length,bh=Math.min(22,(rh-8)/series.length);
 rows.forEach((row,j)=>{const y=top+j*rh;html+=wrap(left-12,y+rh/2+3,row.name,left-22);
 series.forEach((s,k)=>{const v=row.values[k],yy=y+(rh-series.length*bh)/2+k*bh,valid=finite(v),shown=isPercent?percent(v):number(valid?v/(opts.scale||1):null,opts.precision??1),t=`${row.name} · ${s.name}: ${valid?shown:'Not returned by source'}${valid&&!isPercent?' '+(opts.unit||''):''}`;
 if(valid)html+=`<rect x="${left}" y="${yy}" width="${Math.max(0,v/max*pw)}" height="${Math.max(2,bh-2)}" rx="1.5" fill="${s.color}" ${tip(t)}/>`;
 html+=tx(left+(valid?v/max*pw:0)+7,yy+bh*.65,shown,'value',tip(t));});});
 draw(host,w,h,html,opts.label||'Comparison bar chart');}
export function lines(host,rows,series,opts={}){const {w,h}=size(host),left=58,right=25,top=12,bottom=36,pw=w-left-right,ph=h-top-bottom,scale=opts.scale||1,values=rows.flatMap(r=>series.map(s=>r[s.name])).filter(finite);if(!values.length)return label(host,w,h);
 const ts=ticks(Math.max(...values)/scale*1.05||1),max=ts.at(-1)||1,x=i=>left+i*pw/Math.max(rows.length-1,1),y=v=>top+ph-v/scale/max*ph;let html='';
 for(const t of ts)html+=ln(left,y(t*scale),w-right,y(t*scale))+tx(left-10,y(t*scale)+4,compact(t),'axis','text-anchor="end"');
 rows.forEach((r,i)=>{html+=tx(x(i),h-10,r.year,'axis','text-anchor="middle"');if(r.year===opts.endpoint)html+=ln(x(i),top,x(i),h-bottom,'endpoint-line');});
 for(const s of series){let path='';rows.forEach((r,i)=>{const v=r[s.name];if(finite(v)){path+=(path?' L':'M')+x(i)+' '+y(v);}else if(path){html+=`<path d="${path}" stroke="${s.color}" class="series-line"/>`;path='';}});if(path)html+=`<path d="${path}" stroke="${s.color}" class="series-line"/>`;
 rows.forEach((r,i)=>{const v=r[s.name];if(finite(v))html+=`<circle cx="${x(i)}" cy="${y(v)}" r="${r.year===opts.endpoint?4.5:3}" fill="${s.color}" ${tip(`${r.year} · ${s.name}: ${number(v/scale,1)} ${opts.unit||''}`)}/>`;});}
 draw(host,w,h,html,opts.label||'Time series');}
export function scatter(host,rows){const {w,h}=size(host),side=Math.min(w-91,h-85),l=62,t=16,b=t+side;let html=`<path d="M${l},${t}h${side}L${l},${b}Z" fill="#F6F9F3"/><path d="M${l},${b}L${l+side},${t}V${b}Z" fill="#E5F0DF"/>`;
 for(let i=0;i<=5;i++){const v=i/5,x=l+side*v,y=b-side*v;html+=ln(x,t,x,b)+ln(l,y,l+side,y)+tx(x,b+20,number(v,1),'axis','text-anchor="middle"')+tx(l-10,y+4,number(v,1),'axis','text-anchor="end"');}
 html+=ln(l,b,l+side,t,'equality-line')+tx(l+side/2,b+43,'Mining HHI · output tonnes','axis','text-anchor="middle"')+`<text transform="translate(16 ${t+side/2}) rotate(-90)" text-anchor="middle" class="axis">Refining HHI · output tonnes</text>`;
 const palette={Cu:'#00B6AD',Co:'#465B60',Li:'#FF616A',Ni:'#DBB330',C:'#697778',REE:'#77BDCF'};
 rows.forEach((r,i)=>{const a=r.Mining?.HHILower,bb=r.Refining?.HHILower;if(finite(a)&&finite(bb)){const x=l+a*side,y=b-bb*side;html+=`<circle cx="${x}" cy="${y}" r="7" fill="${palette[r.name]}" stroke="white" ${tip(`${r.label} · Mining ${number(a,3)}–${number(r.Mining.HHIUpper,3)}; Refining ${number(bb,3)}–${number(r.Refining.HHIUpper,3)}. Bounds of output-share HHI, not a physical balance.`)}/>`+tx(x,y+(r.name==='Co'?22:r.name==='REE'?-14:23),r.name,'scatter-label','text-anchor="middle"');}});
 draw(host,w,h,html,'Mining versus refining concentration, equality diagonal');}
export function worldMap(host,geo,panels){const {w,h}=size(host),project=([lo,la])=>[(lo+180)/360*w,(85-la)/145*h];let html=`<rect width="${w}" height="${h}" rx="8" fill="#F2F5F0"/>`;
 for(const feature of geo.features){const polys=feature.geometry.type==='Polygon'?[feature.geometry.coordinates]:feature.geometry.coordinates;let d='';for(const poly of polys)for(const ring of poly){let prev=null;for(const coord of ring){const [x,y]=project(coord);d+=(prev&&Math.abs(coord[0]-prev[0])<180?'L':'M')+x.toFixed(1)+','+y.toFixed(1);prev=coord;}d+='Z';}html+=`<path d="${d}" fill="#DCE7D7" stroke="#FFFFFF" stroke-width=".5"/>`;}
 // Large circles are drawn first; stage offsets are display anchors from the source project.
 const points=panels.flatMap(p=>p.rows).filter(r=>r.EntityType==='country_or_territory'&&finite(r.Share)&&r.Share>0&&finite(r.DisplayLatitude)&&finite(r.DisplayLongitude)).sort((a,b)=>b.Share-a.Share);
 points.forEach(r=>{const [x,y]=project([r.DisplayLongitude,r.DisplayLatitude]);html+=`<circle cx="${x}" cy="${y}" r="${Math.max(2.5,Math.sqrt(r.Share)*29)}" fill="${COLORS[r.Stage]}" fill-opacity=".82" stroke="white" stroke-width="1.8" ${tip(`${r.Country} · ${r.Stage}: ${percent(r.Share,2)} of stage output. Display anchor, not a facility location.`)}/>`;});
 if(!points.length)html+=tx(w/2,h/2,'No geographically identified observations','empty','text-anchor="middle"');
 draw(host,w,h,html,'World map of country shares, separate mining and refining circles');}
