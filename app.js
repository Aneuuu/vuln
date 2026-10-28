const esc=t=>t.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const inline=t=>esc(t).replace(/\[([^\]]+)\]\((https?:[^)\s]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>').replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>').replace(/`([^`]+)`/g,'<code>$1</code>').replace(/^(无新[^。；，]*)/,'<span class="quiet">$1</span>');
const kind=h=>/在野利用/.test(h)&&!/范围外/.test(h)?'kev':/严重|高危/.test(h)?'high':/中危|中低危/.test(h)?'mid':/范围外|已报过|未查到|其他/.test(h)?'misc':'rel';
function md(src){let h='',open=false,list=false;const close=()=>{if(list){h+='</ul>';list=false}};
 for(const l of src.split('\n')){let m;
  if(m=l.match(/^#\s+(.*)/)){h+=`<h1>${inline(m[1])}</h1>`}
  else if(m=l.match(/^##\s+(.*)/)){close();if(open)h+='</section>';h+=`<section data-k="${kind(m[1])}"><h2>${inline(m[1])}</h2>`;open=true}
  else if(m=l.match(/^\s*[-*]\s+(.*)/)){if(!list){h+='<ul>';list=true}h+=`<li>${inline(m[1])}</li>`}
  else if(l.trim()){close();h+=`<p>${inline(l)}</p>`}}
 close();if(open)h+='</section>';return h}
let days=[];
async function show(){const d=location.hash.slice(1)||days[0]?.date;if(!d)return;
 document.querySelectorAll('#days a').forEach(a=>a.toggleAttribute('aria-current',a.dataset.d===d));
 const r=await fetch(`data/${d}.md`,{cache:'no-cache'});const el=document.getElementById('day');
 el.innerHTML=r.ok?`<p class="date">${d.slice(5).replace('-','.')}<span style="font-size:.35em;color:var(--muted)"> ${d.slice(0,4)}</span></p>`+md(await r.text()):'<p>未找到该日期。</p>';document.title=`${d} · 漏洞日报`}
fetch('data/index.json',{cache:'no-cache'}).then(r=>r.json()).then(j=>{days=j;
 document.getElementById('days').innerHTML=j.map(x=>`<li><a href="#${x.date}" data-d="${x.date}">${x.date.slice(5).replace('-','.')}<small>${x.date.slice(0,4)} · ${x.links} 条链接</small></a></li>`).join('');show()});
addEventListener('hashchange',show);
