const PEN_COLORS={blue:'#3478db',red:'#e5484d',green:'#29955b',yellow:'#e1b41f',black:'#253b59'};
const PEN_LABELS={blue:'Синий',red:'Красный',green:'Зелёный',yellow:'Жёлтый',black:'Чёрный'};
function validOrder(a,n){return Array.isArray(a)&&a.length===n&&new Set(a).size===n&&a.every(i=>Number.isInteger(i)&&i>=0&&i<n);}
function validLinks(a,n){return Array.isArray(a)&&a.length<=n&&a.every(p=>p&&Number.isInteger(p.left)&&Number.isInteger(p.right)&&p.left>=0&&p.left<n&&p.right>=0&&p.right<n)&&new Set(a.map(p=>p.left)).size===a.length&&new Set(a.map(p=>p.right)).size===a.length;}
function validStrokes(a){return Array.isArray(a)&&a.length<=150&&a.every(s=>s&&Object.hasOwn(PEN_COLORS,s.color)&&Array.isArray(s.points)&&s.points.length<=1000&&s.points.every(p=>Array.isArray(p)&&p.length===3&&p.every(Number.isFinite)&&p[0]>=0&&p[0]<=600&&p[1]>=0&&p[1]<=260&&p[2]>=1&&p[2]<=10));}
function normalAnswer(text){return String(text).normalize('NFKC').toLowerCase().replace(/[’‘]/g,"'").replace(/[.!?,]/g,'').replace(/-/g,' ').trim().replace(/\s+/g,' ');}
function inputBody(q,r,a,test){return `<form id="text-answer-form" class="written-answer"><label for="written-answer">${esc(q.inputLabel||(q.stimulus.includes('___')?'Пропущенное слово':'Ответ по-английски'))}</label><input id="written-answer" type="text" lang="en" maxlength="200" autocapitalize="none" autocomplete="off" autocorrect="off" spellcheck="false" value="${esc(a?.response??r.draft?.text??'')}" placeholder="Напиши по-английски"><button class="primary" id="submit-answer" type="submit" disabled>${test?'Ответить':'Проверить'}</button></form>`;}
function bindInputAnswer(q,r){const field=$('written-answer');field.oninput=()=>{if(solved)return;r.draft={text:field.value};$('submit-answer').disabled=!field.value.trim();save();};$('submit-answer').disabled=solved||!field.value.trim();$('text-answer-form').onsubmit=e=>{e.preventDefault();if(solved||!field.value.trim())return;submitAnswer(q.acceptedText.some(a=>normalAnswer(a)===normalAnswer(field.value)),field.value);};}
function matchingBody(q,r,a,test){const links=a?.links||r.draft?.links||[];return `<p class="matching-tip">Проведи линию или нажми слово и перевод.</p><div class="matching-board" id="matching-board"><svg id="match-lines" aria-hidden="true"></svg><div class="match-column">${q.pairs.map((pair,i)=>`<button class="match-word" data-match-left="${i}" lang="en">${esc(pair.left)}</button>`).join('')}</div><div class="match-column">${q.rightOrder.map(i=>`<button class="match-word" data-match-right="${i}">${esc(q.pairs[i].right)}</button>`).join('')}</div></div><div class="button-row"><button class="primary" id="submit-answer" ${links.length===q.pairs.length?'':'disabled'}>${test?'Ответить':'Проверить пары'}</button><button class="text-button" id="clear-matches">Убрать линии</button></div>`;}
function bindMatching(q,r,a){
 let links=JSON.parse(JSON.stringify(a?.links||r.draft?.links||[])),from=null,drag=null;
 const board=$('matching-board'),svg=$('match-lines');
 function point(el,side){const rect=el.getBoundingClientRect(),bounds=board.getBoundingClientRect();return {x:(side==='left'?rect.right:rect.left)-bounds.left,y:rect.top+rect.height/2-bounds.top};}
 function line(start,end){return `<path d="M${start.x} ${start.y}L${end.x} ${end.y}"/>`;}
 function redraw(to){const bounds=board.getBoundingClientRect();svg.setAttribute('viewBox',`0 0 ${bounds.width} ${bounds.height}`);svg.innerHTML=links.map(p=>line(point(board.querySelector(`[data-match-left="${p.left}"]`),'left'),point(board.querySelector(`[data-match-right="${p.right}"]`),'right'))).join('')+(from!==null&&to?line(point(board.querySelector(`[data-match-left="${from}"]`),'left'),to):'');board.querySelectorAll('[data-match-left]').forEach(b=>b.classList.toggle('match-selected',Number(b.dataset.matchLeft)===from));$('submit-answer').disabled=solved||links.length!==q.pairs.length;}
 function persist(){r.draft={links};save();redraw();}
 function connect(left,right){if(solved)return;links=links.filter(p=>p.left!==left&&p.right!==right);links.push({left,right});from=null;persist();}
 board.querySelectorAll('[data-match-left]').forEach(button=>{button.onclick=()=>{if(solved||button.dataset.suppress==='yes'){button.dataset.suppress='';return;}from=Number(button.dataset.matchLeft);redraw();};
  button.onpointerdown=e=>{if(solved||e.button!==0)return;drag={x:e.clientX,y:e.clientY,moved:false,id:e.pointerId};from=Number(button.dataset.matchLeft);button.setPointerCapture(e.pointerId);redraw();};
  button.onpointermove=e=>{if(!drag||drag.id!==e.pointerId)return;if(Math.hypot(e.clientX-drag.x,e.clientY-drag.y)>8){drag.moved=true;const bounds=board.getBoundingClientRect();redraw({x:e.clientX-bounds.left,y:e.clientY-bounds.top});}};
  button.onpointerup=e=>{if(!drag||drag.id!==e.pointerId)return;if(drag.moved){button.dataset.suppress='yes';const right=[...board.querySelectorAll('[data-match-right]')].find(b=>{const p=b.getBoundingClientRect();return e.clientX>=p.left&&e.clientX<=p.right&&e.clientY>=p.top&&e.clientY<=p.bottom;});if(right)connect(Number(button.dataset.matchLeft),Number(right.dataset.matchRight));}drag=null;redraw();};
  button.onpointercancel=()=>{drag=null;from=null;redraw();};
 });
 board.querySelectorAll('[data-match-right]').forEach(b=>b.onclick=()=>{if(from!==null)connect(from,Number(b.dataset.matchRight));});
 $('clear-matches').onclick=()=>{if(solved)return;links=[];from=null;persist();};
 $('submit-answer').onclick=()=>submitAnswer(links.length===q.pairs.length&&links.every(p=>p.left===p.right),links.map(p=>q.pairs[p.left].left+' — '+q.pairs[p.right].right).join('; '),{links:JSON.parse(JSON.stringify(links))});
 redraw();requestAnimationFrame(()=>{if(svg.isConnected)redraw();});
 const observer=new ResizeObserver(()=>{if(svg.isConnected)redraw();else observer.disconnect();});observer.observe(board);
}
function penBody(q){return `<div class="pen-tools" aria-label="Инструменты рисования">${Object.entries(PEN_COLORS).map(([color,hex])=>`<button class="ink-button" data-ink="${color}" style="--ink:${hex}" aria-label="${PEN_LABELS[color]}" aria-pressed="false"><span aria-hidden="true"></span></button>`).join('')}<button class="text-button" id="undo-stroke">Отменить штрих</button><button class="text-button" id="clear-drawing">Очистить</button></div><canvas id="pen-canvas" width="1200" height="520" role="img" aria-label="Поле для письма и рисования стилусом"></canvas><p class="muted pen-note">Можно писать стилусом, пальцем или мышью. Рисунок сохраняется до завершения задания.</p><details class="manual-check" id="manual-check"><summary>Проверить вместе со взрослым</summary><p>${mixed(q.expectedText)}</p>${q.sampleScene?scene(q.sampleScene):''}<div class="button-row"><button class="primary" id="manual-good" disabled>Получилось</button><button class="secondary" id="manual-retry" disabled>Повторим вместе</button></div><p class="muted">Совместная проверка. Приложение не распознаёт почерк и не оценивает рисунок автоматически.</p></details>`;}
function bindPen(q,r,a){
 const canvas=$('pen-canvas'),ctx=canvas.getContext('2d');ctx.setTransform(2,0,0,2,0,0);
 let strokes=JSON.parse(JSON.stringify(a?.strokes||r.draft?.strokes||[])),ink=r.draft?.ink||'blue',stroke=null,pointer=null;
 if(!Object.hasOwn(PEN_COLORS,ink))ink='blue';
 function repaint(){ctx.clearRect(0,0,600,260);ctx.fillStyle='#fff';ctx.fillRect(0,0,600,260);ctx.strokeStyle='#dce6f4';ctx.lineWidth=1;for(const y of [90,180,235]){ctx.beginPath();ctx.moveTo(15,y);ctx.lineTo(585,y);ctx.stroke();}
  if(q.guide){ctx.font='bold 210px Arial, sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.strokeStyle='#cbd8eb';ctx.lineWidth=2;ctx.strokeText(q.guide,300,137);}
  for(const s of [...strokes,...(stroke?[stroke]:[])]){ctx.strokeStyle=ctx.fillStyle=PEN_COLORS[s.color];ctx.lineCap=ctx.lineJoin='round';const points=s.points;if(points.length===1){ctx.beginPath();ctx.arc(points[0][0],points[0][1],points[0][2]/2,0,Math.PI*2);ctx.fill();}for(let i=1;i<points.length;i++){ctx.lineWidth=points[i][2];ctx.beginPath();ctx.moveTo(points[i-1][0],points[i-1][1]);ctx.lineTo(points[i][0],points[i][1]);ctx.stroke();}}
  const empty=!strokes.length&&!stroke;$('manual-good').disabled=$('manual-retry').disabled=solved||empty;document.querySelectorAll('[data-ink]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.ink===ink)));
 }
 function persist(){r.draft={strokes,ink};save();}
 function point(e){const bounds=canvas.getBoundingClientRect();return [Math.max(0,Math.min(600,(e.clientX-bounds.left)/bounds.width*600)),Math.max(0,Math.min(260,(e.clientY-bounds.top)/bounds.height*260)),Math.min(10,Math.max(1,3+(e.pressure||.5)*4))];}
 canvas.onpointerdown=e=>{if(solved||e.button!==0||pointer!==null)return;if(strokes.length>=150){toast('Поле заполнено. Можно отменить штрих или очистить рисунок.');return;}e.preventDefault();pointer=e.pointerId;canvas.setPointerCapture(pointer);stroke={color:ink,points:[point(e)]};repaint();};
 canvas.onpointermove=e=>{if(pointer!==e.pointerId||!stroke)return;e.preventDefault();if(stroke.points.length<1000)stroke.points.push(point(e));repaint();};
 function finish(e){if(pointer!==e.pointerId||!stroke)return;strokes.push(stroke);stroke=null;pointer=null;persist();repaint();}
 canvas.onpointerup=canvas.onpointercancel=finish;
 document.querySelectorAll('[data-ink]').forEach(b=>b.onclick=()=>{if(solved)return;ink=b.dataset.ink;persist();repaint();});
 $('undo-stroke').onclick=()=>{if(solved)return;strokes.pop();persist();repaint();};$('clear-drawing').onclick=()=>{if(solved)return;strokes=[];persist();repaint();};
 $('manual-check').ontoggle=()=>{if($('manual-check')?.open&&!solved){r.hinted=true;save();}};
 $('manual-good').onclick=()=>{if(!strokes.length)return;submitAnswer(true,'Проверили вместе со взрослым',{manual:true,strokes:JSON.parse(JSON.stringify(strokes))});};
 $('manual-retry').onclick=()=>{if(!strokes.length)return;submitAnswer(false,'Нужно потренироваться',{manual:true});};
 repaint();
}
