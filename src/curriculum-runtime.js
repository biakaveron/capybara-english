const STORE='capybara-english-curriculum-v1';
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
// Only mixed prose receives emphasis; English stories and speech stay plain.
function mixed(text){
 const value=String(text??'');if(!/[А-Яа-яЁё]/.test(value)||!/[A-Za-z]/.test(value))return esc(value);
 const word="-?[A-Za-z]+(?:[’'][A-Za-z]+)?(?:[-/][A-Za-z]+)*";
 const pattern=new RegExp(word+"(?:[ \t]+"+word+")*",'g');let result='',end=0;
 for(const match of value.matchAll(pattern)){result+=esc(value.slice(end,match.index))+`<span class="english-inline" lang="en">${esc(match[0])}</span>`;end=match.index+match[0].length;}
 return result+esc(value.slice(end));
}
const LETTER_NAMES={A:'ay',B:'bee',C:'see',D:'dee',E:'ee',F:'eff',G:'gee',H:'aitch',I:'eye',J:'jay',K:'kay',L:'el',M:'em',N:'en',O:'oh',P:'pee',Q:'cue',R:'ar',S:'ess',T:'tee',U:'you',V:'vee',W:'double you',X:'ex',Y:'why',Z:'zed'};
function speechText(text){const letter=/^(?:The letter )?([A-Z])\.?$/.exec(String(text).trim());return letter?LETTER_NAMES[letter[1]]:text;}
const icon=name=>`<img src="assets/${name}.svg" alt="" aria-hidden="true">`;
const MODULES=new Map(CURRICULUM.modules.map(m=>[m.id,m]));
const TASKS=new Map(CURRICULUM.modules.flatMap(m=>[...m.tasks,...(m.assessmentTasks||[])].map(q=>[q.id,q])));
const WORDS=new Map(VOCAB.map(w=>[w.en,w]));
const TOPIC_ICONS={backpack:'🎒',school:'🏫',animals:'🐱',family:'👨‍👩‍👧‍👦',home:'🏠',food:'🍎',body:'✋',nature:'🌳',qualities:'🎨',actions:'🏃',professions:'🧑‍⚕️',sport:'🏅'};
const now=()=>Date.now();
function freshState(){return {version:1,voice:'',rate:.85,focusModule:null,words:[],training:{},tests:{},review:{},practice:null,daily:null};}
let state=freshState(),storageAvailable=true,tab='today',view='home',activeModule=null,activeSection=null,wordTopic=null,activeWord=null,resultTarget=null,resultIndex=0;
let solved=false,selected=[],clockHour=12,clockMinute=0,voices=[],toastTimer=null,speechTimer=null,speechGeneration=0;
function validScene(c){return c&&WORDS.has(c.word)&&(c.count===undefined||Number.isInteger(c.count)&&c.count>=1&&c.count<=20)&&(c.size===undefined||['small','big'].includes(c.size))&&(c.position===undefined||['on','under','beside'].includes(c.position));}
function validSnapshot(q){
 if(!q||!TASKS.has(q.id)||q.moduleId!==TASKS.get(q.id).moduleId||q.kind!==TASKS.get(q.id).kind||typeof q.prompt!=='string'||typeof q.stimulus!=='string')return false;
 if(q.kind==='choice')return Array.isArray(q.choices)&&q.choices.length>=2&&q.choices.length<=6&&q.choices.every(c=>c&&(typeof c.text==='string'||validScene(c.scene)))&&Number.isInteger(q.correct)&&q.correct>=0&&q.correct<q.choices.length;
 if(q.kind==='build')return Array.isArray(q.tokens)&&q.tokens.length>0&&q.tokens.every(w=>typeof w==='string')&&Array.isArray(q.answer)&&q.answer.length===q.tokens.length&&q.answer.every(w=>typeof w==='string')&&typeof q.complete==='string';
 if(q.kind==='input')return Array.isArray(q.acceptedText)&&q.acceptedText.length>0&&q.acceptedText.every(w=>typeof w==='string'&&w.length>0);
 if(q.kind==='matching')return Array.isArray(q.pairs)&&q.pairs.length>=2&&q.pairs.length<=6&&q.pairs.every(p=>p&&typeof p.left==='string'&&typeof p.right==='string')&&validOrder(q.rightOrder,q.pairs.length);
 if(['trace','handwriting','drawing'].includes(q.kind))return q.manual===true&&typeof q.expectedText==='string';
 return Number.isInteger(q.hour)&&q.hour>=1&&q.hour<=12&&[0,15,30,45].includes(q.minute);
}
function validAnswer(a){return a&&TASKS.has(a.taskId)&&a.moduleId===TASKS.get(a.taskId).moduleId&&typeof a.correct==='boolean'&&typeof a.response==='string'&&typeof a.expected==='string';}
function validHistory(h){return h&&Array.isArray(h.answers)&&h.answers.length>0&&h.answers.length===h.total&&h.total<=100&&h.answers.every(validAnswer)&&h.score===h.answers.filter(a=>a.correct).length&&Number.isFinite(h.finishedAt)&&(!h.items||Array.isArray(h.items)&&h.items.length===h.total&&h.items.every(validSnapshot));}
function cleanRun(raw){
 if(!raw||!['test','module','daily','review'].includes(raw.mode)||(raw.mode==='test'?!validTarget(raw.owner):raw.mode==='review'?raw.owner!=='review':!MODULES.has(raw.owner))||!Array.isArray(raw.items)||!raw.items.length||raw.items.length>100||!raw.items.every(validSnapshot)||!Number.isInteger(raw.position)||raw.position<0||raw.position>=raw.items.length||!Array.isArray(raw.answers))return null;
 if(raw.answers.length!==raw.position&&raw.answers.length!==raw.position+1)return null;
 if(!raw.answers.every((a,i)=>validAnswer(a)&&a.taskId===raw.items[i].id))return null;
 raw.attempts=Number.isInteger(raw.attempts)&&raw.attempts>=0?raw.attempts:0;raw.hinted=!!raw.hinted;
 const q=raw.items[raw.position],d=raw.draft;
 if(d&&q.kind==='build'&&(!Array.isArray(d.tokens)||!d.tokens.every(i=>Number.isInteger(i)&&i>=0&&i<q.tokens.length)||new Set(d.tokens).size!==d.tokens.length))raw.draft=null;
 if(d&&q.kind==='clock-set'&&(!Number.isInteger(d.hour)||d.hour<1||d.hour>12||![0,15,30,45].includes(d.minute)))raw.draft=null;
 if(d&&q.kind==='input'&&(typeof d.text!=='string'||d.text.length>200))raw.draft=null;
 if(d&&q.kind==='matching'&&!validLinks(d.links,q.pairs.length))raw.draft=null;
 if(d&&['trace','handwriting','drawing'].includes(q.kind)&&!validStrokes(d.strokes))raw.draft=null;
 return raw;
}
try{
 const raw=JSON.parse(localStorage.getItem(STORE));
 if(raw?.version===1){
  state.voice=typeof raw.voice==='string'?raw.voice:'';state.rate=Number.isFinite(raw.rate)?Math.max(.65,Math.min(1,raw.rate)):.85;
  state.focusModule=MODULES.has(raw.focusModule)?raw.focusModule:null;
  state.words=Array.isArray(raw.words)?[...new Set(raw.words.filter(en=>WORDS.has(en)))]:[];
  for(const [id,p] of Object.entries(raw.training||{})){if(!MODULES.has(id)||!p||typeof p!=='object')continue;state.training[id]={cursor:TASKS.get(p.cursor)?.moduleId===id?p.cursor:MODULES.get(id).tasks[0].id,done:Object.fromEntries(Object.entries(p.done||{}).filter(([qid,a])=>TASKS.get(qid)?.moduleId===id&&a&&Number.isFinite(a.at)))};}
  for(const [id,t] of Object.entries(raw.tests||{})){if(!validTarget(id)||!t)continue;const active=cleanRun(t.active);state.tests[id]={active:active?.mode==='test'&&active.owner===id?active:null,history:Array.isArray(t.history)?t.history.filter(validHistory).slice(0,10):[]};}
  state.review=Object.fromEntries(Object.entries(raw.review||{}).filter(([id,r])=>TASKS.has(id)&&r&&Number.isFinite(r.due)&&Number.isInteger(r.streak)&&r.streak>=0));
  state.practice=cleanRun(raw.practice);
  state.daily=raw.daily&&typeof raw.daily.date==='string'?raw.daily:null;
 }
}catch{storageAvailable=false;}
function save(){try{localStorage.setItem(STORE,JSON.stringify(state));storageAvailable=true;}catch{storageAvailable=false;}$('saved').textContent=storageAvailable?'Сохраняем на устройстве':'Без сохранения';$('storage-note').textContent=storageAvailable?'Прогресс остаётся в этом браузере на этом устройстве.':'Браузер не разрешил сохранение. После закрытия результаты потеряются.';}
function toast(s){$('toast').textContent=s;$('toast').hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').hidden=true,5000);}
function stopSpeech(){speechGeneration++;clearTimeout(speechTimer);window.speechSynthesis?.cancel();}
function voiceList(){
 if(!window.speechSynthesis)return;
 voices=speechSynthesis.getVoices().filter(v=>/^en[-_]/i.test(v.lang));
 $('voice').innerHTML=voices.length?voices.map(v=>`<option value="${esc(v.voiceURI)}">${esc(v.name)} · ${esc(v.lang)}${v.localService?' · на устройстве':' · через сеть'}</option>`).join(''):'<option value="">Английский голос не найден</option>';
 if(!voices.some(v=>v.voiceURI===state.voice)&&voices.length)state.voice=(voices.find(v=>/^en-GB/i.test(v.lang)&&v.localService)||voices.find(v=>/^en-GB/i.test(v.lang))||voices[0]).voiceURI;
 $('voice').value=state.voice;const v=voices.find(v=>v.voiceURI===state.voice);$('voice-status').textContent=v?(v.localService?'Голос работает на устройстве. Проверьте озвучку без сети на планшете.':'Этот голос может требовать интернет.'):'Установите английский голос в настройках синтеза речи планшета.';
}
function speak(text,slow=false){
 stopSpeech();if(!window.speechSynthesis||typeof SpeechSynthesisUtterance==='undefined'){toast('Озвучка недоступна. Попробуйте Chrome на планшете.');return;}
 voiceList();const voice=voices.find(v=>v.voiceURI===state.voice);if(!voice){toast('Откройте настройки и проверьте английский голос.');return;}
 const u=new SpeechSynthesisUtterance(speechText(text)),generation=speechGeneration;u.lang=voice.lang;u.voice=voice;u.rate=slow?Math.max(.65,state.rate-.15):state.rate;
 u.onstart=u.onend=()=>clearTimeout(speechTimer);u.onerror=e=>{clearTimeout(speechTimer);if(!['canceled','interrupted'].includes(e.error))toast('Проверьте громкость, голос и подключение к интернету.');};speechSynthesis.speak(u);speechTimer=setTimeout(()=>{if(generation===speechGeneration)toast('Если звука нет, проверьте настройки английского голоса.');},6000);
}
function shuffled(a){const c=a.slice();for(let i=c.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[c[i],c[j]]=[c[j],c[i]];}return c;}
function validTarget(id){return typeof id==='string'&&(id.startsWith('module:')&&MODULES.has(id.slice(7))&&!MODULES.get(id.slice(7)).practiceOnly||id.startsWith('section:')&&CURRICULUM.sections.some(s=>s.id===id.slice(8))&&CURRICULUM.modules.some(m=>m.section===id.slice(8)&&!m.practiceOnly));}
function training(id){return state.training[id]||= {cursor:MODULES.get(id).tasks[0].id,done:{}};}
function testing(target){return state.tests[target]||= {active:null,history:[]};}
function moduleCount(id){return Object.keys(state.training[id]?.done||{}).length;}
function latest(id){return state.tests['module:'+id]?.history[0];}
function percent(id){return Math.round(moduleCount(id)/MODULES.get(id).tasks.length*100);}
function dueTasks(){return Object.entries(state.review).filter(([id,r])=>r.due<=now()).sort((a,b)=>a[1].due-b[1].due).map(([id])=>TASKS.get(id));}
function localDate(){const d=new Date();return `${d.getFullYear()}-${d.getMonth()+1}-${d.getDate()}`;}
function recommend(){const focus=MODULES.get(state.focusModule);return focus&&moduleCount(focus.id)<focus.tasks.length?focus:CURRICULUM.modules.find(m=>moduleCount(m.id)<m.tasks.length&&m.prerequisites.every(id=>moduleCount(id)>0))||CURRICULUM.modules.find(m=>moduleCount(m.id)<m.tasks.length)||CURRICULUM.modules[0];}
function navigate(next){stopSpeech();resultTarget=null;tab=next;view='home';activeModule=null;activeSection=null;solved=false;render();}
function heading(title,sub='',counter=''){return `<div class="activity-header"><div><h1 id="activity-title">${mixed(title)}</h1><p>${mixed(sub)}</p></div>${counter?`<span class="task-counter">${esc(counter)}</span>`:''}</div>`;}
function backbar(){return `<div class="breadcrumbs"><button class="text-button" data-home="learn">Все разделы</button>${activeSection?`<button class="text-button" data-section="${activeSection}">${esc(CURRICULUM.sections.find(s=>s.id===activeSection)?.title)}</button>`:''}</div>`;}
function render(){
 $('main-nav').innerHTML=[['today','☀️','Сегодня'],['learn','📚','Учимся'],['dictionary','🎒','Словарь'],['review','🔁','Повторяем']].map(([id,e,t])=>`<button data-nav="${id}" class="nav-button ${tab===id?'active':''}" ${tab===id?'aria-current="page"':''}><span aria-hidden="true">${e}</span>${t}</button>`).join('');
 $('main-nav').querySelectorAll('button').forEach(b=>b.onclick=()=>navigate(b.dataset.nav));
 $('side-panel').hidden=false;
 if(view==='session')renderSession();else if(view==='result')renderResult();else if(view==='practice-finish')renderPracticeFinish();else if(view==='module')renderModule();else if(view==='section')renderSection();else if(tab==='today')renderToday();else if(tab==='learn')renderLearn();else if(tab==='dictionary')renderDictionary();else renderReview();
 bindNavigation();save();
}
function bindNavigation(){
 $('activity').querySelectorAll('[data-module]').forEach(b=>b.onclick=()=>openModule(b.dataset.module));
 $('activity').querySelectorAll('[data-section]').forEach(b=>b.onclick=()=>openSection(b.dataset.section));
 $('activity').querySelectorAll('[data-home]').forEach(b=>b.onclick=()=>navigate(b.dataset.home));
 $('activity').querySelectorAll('[data-speech]').forEach(b=>b.onclick=()=>speak(b.dataset.speech));
 $('activity').querySelectorAll('[data-test]').forEach(b=>b.onclick=()=>startTest(b.dataset.test));
 $('activity').querySelectorAll('[data-result]').forEach(b=>b.onclick=()=>openResult(b.dataset.result,0));
}
function progressSide(){
 const learned=CURRICULUM.modules.filter(m=>moduleCount(m.id)>0).length,checked=CURRICULUM.modules.filter(m=>latest(m.id)).length;
 $('side-panel').innerHTML=`<div class="side-card blue-card"><span class="eyebrow">ТВОЙ ПУТЬ</span><h3>Шаг за шагом</h3><p>${learned} из ${CURRICULUM.modules.length} блоков начато</p><p>${checked} блоков проверено самостоятельно</p><p>${state.words.length} из ${VOCAB.length} слов повторено</p></div><div class="side-card"><h3>Капибара подсказывает</h3><p>Можно выбирать разделы в любом порядке. Начни с объяснения, потом потренируйся и проверь себя.</p></div>`;
}
function moduleCard(m){const last=latest(m.id);return `<button class="module-card" data-module="${m.id}"><span class="module-title">${mixed(m.title)}</span><span>${mixed(m.description)}</span><span class="mini-progress"><span style="width:${percent(m.id)}%"></span></span><span class="module-status">Тренировка: ${moduleCount(m.id)}/${m.tasks.length}${last?` · Проверка: ${last.score}/${last.total}`:''}</span></button>`;}
function renderToday(){
 const m=recommend(),due=dueTasks().length,active=state.practice,dayDone=state.daily?.date===localDate()&&state.daily.complete;
 $('activity').innerHTML=heading('Пора учиться с капибарой','Короткое занятие: новое и повторение.')+`<div class="welcome"><img src="assets/capybara.svg" alt="Капибара"><div><span class="eyebrow">СЕГОДНЯ</span><h2>${dayDone?'Сегодня уже позанимались!':mixed(m.title)}</h2><p>${dayDone?'Можно выбрать ещё один блок или повторить трудное.':mixed(m.description)}</p><div class="button-row"><button class="primary" id="daily-start">${active&&active.mode==='daily'?`Продолжить · ${active.answers.length}/${active.items.length}`:'Короткое занятие'}</button><button class="secondary" data-module="${m.id}">Сначала объяснение</button></div></div></div>${active&&active.mode!=='daily'?`<div class="resume-card"><p>Осталась незавершённая тренировка.</p><button class="secondary" id="resume-practice">Продолжить</button></div>`:''}<div class="summary-grid"><div><strong>${due}</strong><span>заданий пора повторить</span></div><div><strong>${CURRICULUM.modules.length}</strong><span>учебных блоков</span></div><div><strong>${VOCAB.length}</strong><span>слов в словаре</span></div></div><h2 class="subheading">Выбрать направление</h2><div class="section-grid">${CURRICULUM.sections.map(s=>`<button class="section-card" data-section="${s.id}"><span aria-hidden="true">${s.icon}</span><strong>${s.title}</strong></button>`).join('')}</div>`;
 $('daily-start').onclick=startDaily;if($('resume-practice'))$('resume-practice').onclick=resumePractice;progressSide();
}
function renderLearn(){
 $('activity').innerHTML=heading('Чему будем учиться?','Словарные темы можно использовать в разных учебных блоках.')+`<div class="section-grid">${CURRICULUM.sections.map(s=>{const mods=CURRICULUM.modules.filter(m=>m.section===s.id);return `<button class="section-card" data-section="${s.id}"><span aria-hidden="true">${s.icon}</span><strong>${s.title}</strong><p>${s.description}</p><small>${mods.length} блоков · ${mods.filter(m=>latest(m.id)).length} проверено</small></button>`;}).join('')}</div>`;progressSide();
}
function openSection(id){stopSpeech();resultTarget=null;activeSection=id;activeModule=null;tab='learn';view='section';render();}
function renderSection(){
 const section=CURRICULUM.sections.find(s=>s.id===activeSection),mods=CURRICULUM.modules.filter(m=>m.section===activeSection),target='section:'+activeSection,t=testing(target);
 $('activity').innerHTML=backbar()+heading(section.title,section.description)+`<div class="module-grid">${mods.map(moduleCard).join('')}</div>${mods.some(m=>!m.practiceOnly)?`<div class="test-card"><span class="eyebrow">ПРОВЕРКА РАЗДЕЛА</span><h3>Соединим навыки</h3><p>Новые примеры из блоков с самостоятельной проверкой, затем дополнительные задания. Одна попытка на ответ; оценка и разбор появятся в конце.</p><div class="button-row"><button class="primary" data-test="${target}">${t.active?'Продолжить проверку':'Проверить раздел'}</button>${t.history.length?`<button class="secondary" data-result="${target}">Результаты · ${t.history[0].score}/${t.history[0].total}</button>`:''}</div></div>`:''}`;progressSide();
}
function openModule(id){if(!MODULES.has(id))return;stopSpeech();resultTarget=null;state.focusModule=id;activeModule=id;activeSection=MODULES.get(id).section;tab='learn';view='module';render();}
function renderModule(){
 const m=MODULES.get(activeModule),p=training(m.id),target='module:'+m.id,t=testing(target),active=state.practice?.owner===m.id&&state.practice.mode==='module';
 $('activity').innerHTML=backbar()+heading(m.title,m.description)+`<div class="lesson-rules"><h2>Разберёмся</h2>${m.rules.map(r=>`<p>${mixed(r)}</p>`).join('')}</div>${m.id==='letters'?`<div class="alphabet-grid">${'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('').map(c=>`<button class="secondary" data-speech="${c}" aria-label="Послушать название буквы ${c}">${c}</button>`).join('')}</div>`:''}<div class="examples">${m.examples.map(e=>`<div class="example"><div><p lang="en">${esc(e.en)}</p><p class="muted">${mixed(e.ru)}</p></div><button class="icon-button" data-speech="${esc(e.en)}" aria-label="Послушать пример">${icon('volume-2')}</button></div>`).join('')}</div><div class="training-card"><span class="eyebrow">ПОТРЕНИРУЕМСЯ</span><p>${Object.keys(p.done).length} из ${m.tasks.length} заданий выполнено. В тренировке можно исправлять ошибки.</p><div class="button-row"><button class="primary" id="practice-start">${active?`Продолжить · ${state.practice.answers.length}/${state.practice.items.length}`:'Тренироваться'}</button>${Object.keys(p.done).length?'<button class="secondary" id="practice-again">Повторить все задания</button>':''}</div></div>${m.practiceOnly?`<p class="guided-note">${m.adventure?'Приключение проходит шаг за шагом. Здесь можно пользоваться объяснениями.':'Письмо и рисунки проверяем вместе со взрослым. Результат не считается самостоятельной проверкой.'}</p>`:`<div class="test-card"><span class="eyebrow">ПРОВЕРИМ СЕБЯ</span><p>10 новых примеров из отдельного набора. Считается первая попытка. Подсказки отключены.</p><div class="button-row"><button class="primary" data-test="${target}">${t.active?`Продолжить · ${t.active.answers.length}/${t.active.items.length}`:'Начать проверку'}</button>${t.history.length?`<button class="secondary" data-result="${target}">Результаты · ${t.history[0].score}/${t.history[0].total}</button>`:''}</div></div>`}${m.prerequisites.length?`<div class="prerequisites"><h3>Перед этим полезно потренировать</h3><div class="button-row">${m.prerequisites.map(id=>`<button class="text-button" data-module="${id}">${mixed(MODULES.get(id).title)}</button>`).join('')}</div></div>`:''}`;
 $('practice-start').onclick=()=>startPractice(m.id);if($('practice-again'))$('practice-again').onclick=()=>startPractice(m.id,true);
 $('side-panel').innerHTML=`<div class="side-card blue-card"><h3>Этот блок</h3><p>Тренировка: ${moduleCount(m.id)}/${m.tasks.length}</p><p>Последняя проверка: ${t.history[0]?`${t.history[0].score}/${t.history[0].total}`:'пока нет'}</p><p>Это разные показатели: выполненное с подсказкой упражнение не считается самостоятельной проверкой.</p></div><div class="side-card"><h3>Не спеши</h3><p>Послушай примеры и повтори вслух. Можно возвращаться к объяснению во время тренировки.</p></div>`;
}
function snapshot(q,test=false){const c=JSON.parse(JSON.stringify(q));if(test&&c.kind==='choice'){const order=shuffled(c.choices.map((_,i)=>i));c.choices=order.map(i=>c.choices[i]);c.correct=order.indexOf(q.correct);}if(c.kind==='build')c.tokens=shuffled(c.tokens);if(c.kind==='matching')c.rightOrder=shuffled(c.pairs.map((_,i)=>i));return c;}
function makeRun(items,mode,owner){return {id:now().toString(36)+'-'+Math.random().toString(36).slice(2),mode,owner,startedAt:now(),position:0,answers:[],items:items.map(q=>snapshot(q,mode==='test')),attempts:0,hinted:false};}
function replacePractice(run){if(state.practice&&!confirm('Начать другую тренировку? Текущая незавершённая тренировка будет заменена. Выполненные задания сохранятся.'))return false;state.practice=run;resultTarget=null;save();return true;}
function resumePractice(){stopSpeech();resultTarget=null;tab=state.practice.mode==='review'?'review':'today';view='session';solved=false;render();}
function startPractice(id,again=false){
 if(!again&&state.practice?.mode==='module'&&state.practice.owner===id){resultTarget=null;tab='learn';view='session';render();return;}
 const m=MODULES.get(id),done=training(id).done,items=again?m.tasks:m.tasks.filter(q=>!done[q.id]);
 if(!replacePractice(makeRun(items.length?items:m.tasks,'module',id)))return;activeModule=id;activeSection=m.section;tab='learn';view='session';render();
}
function startDaily(){
 if(state.practice?.mode==='daily'){resumePractice();return;}
 const m=recommend();if(m.adventure){startPractice(m.id);return;}const due=dueTasks(),fresh=m.tasks.filter(q=>!training(m.id).done[q.id]);
 const items=[...due.slice(0,4),...fresh].filter((q,i,a)=>a.findIndex(x=>x.id===q.id)===i).slice(0,8);
 for(const q of shuffled([...m.tasks,...m.prerequisites.flatMap(id=>MODULES.get(id).tasks)]))if(items.length<8&&!items.some(x=>x.id===q.id))items.push(q);
 if(!replacePractice(makeRun(items,'daily',m.id)))return;state.daily={date:localDate(),complete:false};tab='today';view='session';render();
}
function startReview(all=false){
 if(state.practice?.mode==='review'){resumePractice();return;}
 const items=(all?Object.keys(state.review).map(id=>TASKS.get(id)):dueTasks()).slice(0,12);if(!items.length){toast('Пока нет заданий для повторения.');return;}
 if(!replacePractice(makeRun(items,'review','review')))return;tab='review';view='session';render();
}
function startTest(target){
 if(!validTarget(target))return;stopSpeech();const t=testing(target);
 if(!t.active){
  let items;
  if(target.startsWith('module:')){const bank=MODULES.get(target.slice(7)).assessmentTasks,groups=new Map();for(const q of bank){const key=q.kind+':'+(q.audioOnly?'audio':'visual');if(!groups.has(key))groups.set(key,[]);groups.get(key).push(q);}const core=[...groups.values()].map(rows=>shuffled(rows)[0]);items=shuffled([...core,...shuffled(bank).filter(q=>!core.some(c=>c.id===q.id)).slice(0,10-core.length)]);}
  else{const mods=CURRICULUM.modules.filter(m=>m.section===target.slice(8)&&!m.practiceOnly);items=mods.map(m=>shuffled(m.assessmentTasks)[0]);const remaining=shuffled(mods.flatMap(m=>m.assessmentTasks)).filter(q=>!items.some(x=>x.id===q.id));items=shuffled([...items,...remaining.slice(0,Math.max(0,10-items.length))]);}
  t.active=makeRun(items,'test',target);
 }
 resultTarget=target;activeModule=target.startsWith('module:')?target.slice(7):null;activeSection=activeModule?MODULES.get(activeModule).section:target.slice(8);tab='learn';view='session';save();render();
}
function currentRun(){if(view!=='session')return null;return resultTarget&&view==='session'&&state.tests[resultTarget]?.active?.mode==='test'?state.tests[resultTarget].active:state.practice;}
function currentTask(){const r=currentRun();return r.items[r.position];}
function figure(q){if(!q.figure)return '';if(q.figure.type==='clock')return clockFace(q.figure.hour,q.figure.minute);if(q.figure.type==='scene')return scene(q.figure.scene);if(q.figure.type==='schedule')return `<table class="schedule"><caption>Расписание · время по 12-часовым часам</caption><tbody>${q.figure.rows.map(r=>`<tr><th scope="row" lang="en">${esc(r.label)}</th><td>${esc(r.time)}</td></tr>`).join('')}</tbody></table>`;return '';}
function paint(shape,color){const palette={red:'#e5484d',blue:'#3478db',green:'#29955b',yellow:'#f3c742',pink:'#e977ab'};const art=shape==='star'?'<path d="M32 4l8 18 20 3-15 14 4 20-17-10-17 10 4-20L4 25l20-3z"/>':'<circle cx="32" cy="32" r="27"/><path d="M11 16Q42 22 52 49M12 48Q21 22 50 15" fill="none"/>';return `<svg class="painted-object" viewBox="0 0 64 64" aria-hidden="true" fill="${palette[color]||palette.blue}" stroke="#253b59" stroke-width="3">${art}</svg>`;}
function sceneLabel(c){const w=WORDS.get(c.word),colors={red:'красный',blue:'синий',green:'зелёный',yellow:'жёлтый',pink:'розовый'},sizes={small:'маленький',big:'большой'},positions={on:'на столе',under:'под столом',beside:'рядом со столом'};return `${c.count||1} × ${c.paint==='ball'?'мяч':c.paint==='star'?'звезда':w?.ru||c.word}; ${[colors[c.color],sizes[c.size],positions[c.position]].filter(Boolean).join(', ')}`;}
function scene(c){
 const w=WORDS.get(c.word)||{},color=c.color||w.color||'',size=c.size||w.size||'',art=c.emoji||w.emoji;
 const image=c.paint?paint(c.paint,color):w.kind&&ICONS[w.kind]?icon(ICONS[w.kind]):w.icon?icon(w.icon):`<span class="scene-emoji" aria-hidden="true">${esc(art||'⭐')}</span>`;
 const objects=Array.from({length:Math.max(1,Math.min(20,c.count||1))},()=>`<span class="object ${esc(color)} ${esc(size)}">${image}</span>`).join('');
 return `<div class="scene ${c.count>1?'objects':''}" role="img" aria-label="${esc(sceneLabel(c))}">${c.position?`<div class="relation-scene ${esc(c.position)}"><span class="relation-subject">${objects}</span><span class="relation-table" aria-hidden="true"></span></div>`:objects}</div>`;
}
function clockFace(h,m){
 const cx=100,cy=100;const end=(angle,len)=>[cx+Math.sin(angle*Math.PI/180)*len,cy-Math.cos(angle*Math.PI/180)*len];const [hx,hy]=end((h%12)*30+m*.5,46),[mx,my]=end(m*6,67);
 return `<svg class="clock-face" role="img" aria-label="Часы: короткая стрелка — часы, длинная — минуты" viewBox="0 0 200 200"><circle cx="100" cy="100" r="94" fill="#fff" stroke="#c7d8f3" stroke-width="5"/>${Array.from({length:60},(_,i)=>{const [x,y]=end(i*6,87),[a,b]=end(i*6,i%5?84:80);return `<path d="M${x} ${y}L${a} ${b}" stroke="#6682a5" stroke-width="${i%5?1:2}"/>`;}).join('')}${Array.from({length:12},(_,i)=>{const n=i+1,[x,y]=end(n*30,70);return `<text x="${x}" y="${y}" text-anchor="middle" dominant-baseline="central" font-size="14" font-weight="700" fill="#253b59">${n}</text>`;}).join('')}<path d="M100 100L${hx} ${hy}" stroke="#253b59" stroke-width="7" stroke-linecap="round"/><path d="M100 100L${mx} ${my}" stroke="#1653e8" stroke-width="4" stroke-linecap="round"/><circle cx="100" cy="100" r="5" fill="#1653e8"/></svg>`;
}
function renderSession(){
 const r=currentRun();if(!r){navigate(tab);return;}const q=r.items[r.position],test=r.mode==='test',a=r.answers[r.position],m=MODULES.get(q.moduleId);solved=!!a;selected=a?.tokenIndexes||r.draft?.tokens||[];clockHour=a?.hour??r.draft?.hour??12;clockMinute=a?.minute??r.draft?.minute??0;
 const comprehension=q.stimulusType==='story'||q.stimulusType==='dialogue';
 let body='';
 if(q.audioOnly)body=`<div class="listening-call"><div class="button-row"><button class="primary" id="listen-task">${icon('volume-2')}Послушать</button><button class="secondary" id="slow-task">${icon('volume-2')}Медленнее</button></div>${test?'':`<button class="text-button" id="hint-task">Показать фразу-подсказку</button><p class="hint-sentence" id="hint-sentence" lang="en" ${r.hinted?'':'hidden'}>${r.hinted?esc(q.speech):''}</p>`}</div>`;
 else if(q.stimulus)body=`<div class="stimulus ${q.stimulusType==='story'||q.stimulusType==='dialogue'?'story':''}"><p lang="${q.moduleId==='pronouns'||q.moduleId==='weekdays'?'ru':'en'}">${mixed(q.stimulus)}</p>${q.speech&&(!test||!['letters','read-words','understand-sentence','stories','dialogues'].includes(q.moduleId))?`<button class="icon-button" id="listen-task" aria-label="Послушать">${icon('volume-2')}</button>`:''}</div>`;
 body+=figure(q);
 if(m.adventure)body=`<div class="adventure-step"><img src="assets/capybara.svg" alt=""><p>${mixed(q.storyLead||m.description)}</p></div>`+body;
 if(comprehension)body+=`<p class="comprehension-question" id="comprehension-question">${mixed(q.prompt)}</p>`;
 if(q.kind==='choice')body+=`<div class="choices ${q.choices.some(c=>c.scene)?'picture-choices':''}">${q.choices.map((c,i)=>`<button class="choice" data-choice="${i}" ${c.scene?`aria-label="${esc(sceneLabel(c.scene))}"`:''}>${c.scene?`<span class="choice-letter" aria-hidden="true">${i+1}</span>`+scene(c.scene):`<span lang="${c.lang||'en'}">${mixed(c.text)}</span>`}</button>`).join('')}</div>${q.ru&&!q.audioOnly&&(q.complete||q.moduleId==='short-answers')?`<p class="translation">${mixed(q.ru)}</p>`:''}`;
 else if(q.kind==='build')body+=`<p class="translation builder-translation">${mixed(q.ru)}</p><div class="dropzone" id="dropzone"></div><p class="bank-label">Слова для фразы</p><div class="word-bank" id="word-bank"></div><div class="button-row"><button class="primary" id="submit-answer" disabled>${test?'Ответить':'Проверить'}</button><button class="text-button" id="clear-tokens">Убрать слова</button></div>`;
 else if(q.kind==='input')body+=inputBody(q,r,a,test);
 else if(q.kind==='matching')body+=matchingBody(q,r,a,test);
 else if(q.manual)body+=penBody(q);
 else body+=`<div id="clock-picture">${clockFace(clockHour,clockMinute)}</div><div class="clock-controls"><label>Час<select id="clock-hour" aria-label="Установить час">${Array.from({length:12},(_,i)=>`<option value="${i+1}" ${i+1===clockHour?'selected':''}>${i+1}</option>`).join('')}</select></label><label>Минуты<select id="clock-minute" aria-label="Установить минуты">${[0,15,30,45].map(n=>`<option value="${n}" ${n===clockMinute?'selected':''}>${String(n).padStart(2,'0')}</option>`).join('')}</select></label><button class="primary" id="submit-answer">${test?'Ответить':'Проверить'}</button></div>`;
 $('activity').innerHTML=`<div class="session-top"><button class="text-button" id="session-back">${test?'К разделу':'Вернуться'}</button><div class="session-title-group"><h1 class="session-title" id="activity-title">${mixed(m.title)}</h1><span class="task-counter">${r.position+1} / ${r.items.length}</span></div>${test?'':`<button class="text-button" id="lesson-help">Объяснение</button>`}</div>`+(comprehension?'':`<p class="session-prompt">${mixed(q.prompt)}</p>`)+body+`<div id="feedback" class="feedback" aria-live="polite"></div><div class="activity-footer"><span>${test?'Одна попытка · итог в конце':'Можно попробовать ещё раз'}</span><button class="primary" id="next-question" ${a?'':'disabled'}>${r.position===r.items.length-1?(test?'Завершить проверку':'Закончить'):'Дальше'}${icon('arrow-right')}</button></div>`;
 if($('listen-task'))$('listen-task').onclick=()=>{if(!test&&!q.audioOnly&&['letters','read-words','understand-sentence','stories','dialogues'].includes(q.moduleId)){r.hinted=true;save();}speak(q.speech);};if($('slow-task'))$('slow-task').onclick=()=>speak(q.speech,true);
 if($('hint-task'))$('hint-task').onclick=()=>{r.hinted=true;$('hint-sentence').hidden=false;$('hint-sentence').textContent=q.speech;save();};
 if($('lesson-help'))$('lesson-help').onclick=()=>{r.hinted=true;save();$('help-title').innerHTML=mixed(m.title);$('help-content').innerHTML=m.rules.map(s=>`<p>${mixed(s)}</p>`).join('')+m.examples.map(e=>`<p lang="en">${esc(e.en)}</p><p class="muted">${mixed(e.ru)}</p>`).join('');$('help-dialog').showModal();};
 $('session-back').onclick=()=>{stopSpeech();if(test){if(r.owner.startsWith('module:'))openModule(r.owner.slice(7));else openSection(r.owner.slice(8));}else if(r.mode==='module')openModule(r.owner);else navigate(r.mode==='review'?'review':'today');};
 if(q.kind==='choice')$('activity').querySelectorAll('[data-choice]').forEach(b=>b.onclick=()=>submitAnswer(Number(b.dataset.choice)===q.correct,optionLabel(q.choices[Number(b.dataset.choice)]),{chosen:Number(b.dataset.choice)}));
 else if(q.kind==='build'){renderTokens();$('clear-tokens').onclick=()=>{if(solved)return;selected=[];renderTokens();};$('submit-answer').onclick=()=>{const words=selected.map(i=>q.tokens[i]);submitAnswer((q.acceptedAnswers||[q.answer]).some(a=>a.join(' ').toLowerCase()===words.join(' ').toLowerCase()),words.join(' '),{tokenIndexes:selected.slice()});};}
 else if(q.kind==='input')bindInputAnswer(q,r);
 else if(q.kind==='matching')bindMatching(q,r,a);
 else if(q.manual)bindPen(q,r,a);
 else{function update(){if(solved)return;clockHour=Number($('clock-hour').value);clockMinute=Number($('clock-minute').value);$('clock-picture').innerHTML=clockFace(clockHour,clockMinute);r.draft={hour:clockHour,minute:clockMinute};save();}$('clock-hour').onchange=update;$('clock-minute').onchange=update;$('submit-answer').onclick=()=>submitAnswer(clockHour===q.hour&&clockMinute===q.minute,`${clockHour}:${String(clockMinute).padStart(2,'0')}`,{hour:clockHour,minute:clockMinute});}
 $('next-question').onclick=nextQuestion;if(a)restoreAnswer(a,test,q);renderSessionSide(r,test);
}
function optionLabel(c){return c.scene?sceneLabel(c.scene):c.text;}
function expected(q){if(q.kind==='input')return q.acceptedText[0];if(q.kind==='matching')return q.pairs.map(p=>p.left+' — '+p.right).join('; ');if(q.manual)return q.expectedText;return q.kind==='choice'?optionLabel(q.choices[q.correct]):q.kind==='build'?q.complete:`${q.hour}:${String(q.minute).padStart(2,'0')}`;}
function renderTokens(){
 const q=currentTask();if(!solved){currentRun().draft={tokens:selected.slice()};save();}const make=(i,inBank)=>`<button class="token" data-token="${i}" ${solved?'disabled':''} aria-label="${inBank?'Добавить':'Убрать'} слово ${esc(q.tokens[i])}" lang="en">${esc(q.tokens[i])}</button>`;
 $('word-bank').innerHTML=q.tokens.map((w,i)=>selected.includes(i)?'':make(i,true)).join('');$('dropzone').innerHTML=selected.length?selected.map(i=>make(i,false)).join(''):'<span class="placeholder">Нажимай на слова или перетаскивай их сюда</span>';
 $('submit-answer').disabled=solved||selected.length!==q.tokens.length;
 $('activity').querySelectorAll('[data-token]').forEach(b=>{b.onclick=()=>{if(solved||b.dataset.dragged==='yes')return;const i=Number(b.dataset.token);selected=selected.includes(i)?selected.filter(x=>x!==i):[...selected,i];renderTokens();};bindDrag(b);});
}
function bindDrag(button){let start=null,ghost=null,moved=false;const clean=()=>{ghost?.remove();ghost=null;$('dropzone')?.classList.remove('over');};button.onpointerdown=e=>{if(solved||e.button!==0)return;start={x:e.clientX,y:e.clientY,id:e.pointerId};moved=false;button.setPointerCapture(e.pointerId);};button.onpointermove=e=>{if(!start||start.id!==e.pointerId)return;if(Math.hypot(e.clientX-start.x,e.clientY-start.y)>10){moved=true;if(!ghost){ghost=button.cloneNode(true);ghost.classList.add('token-ghost');document.body.appendChild(ghost);}ghost.style.left=e.clientX+'px';ghost.style.top=e.clientY+'px';const r=$('dropzone').getBoundingClientRect();$('dropzone').classList.toggle('over',e.clientX>=r.left&&e.clientX<=r.right&&e.clientY>=r.top&&e.clientY<=r.bottom);}};button.onpointerup=e=>{if(!start)return;start=null;if(moved){const r=$('dropzone').getBoundingClientRect(),inside=e.clientX>=r.left&&e.clientX<=r.right&&e.clientY>=r.top&&e.clientY<=r.bottom,i=Number(button.dataset.token);button.dataset.dragged='yes';if(inside&&!selected.includes(i))selected.push(i);else if(!inside)selected=selected.filter(x=>x!==i);clean();renderTokens();}else clean();};button.onpointercancel=()=>{start=null;clean();};}
function feedback(message,kind='neutral'){$('feedback').className='feedback '+kind;$('feedback').innerHTML=mixed(message);}
function scheduleReview(id,correct){const old=state.review[id]||{streak:0},streak=correct?old.streak+1:0;state.review[id]={streak,due:now()+(correct?[1,3,7,14][Math.min(streak-1,3)]*86400000:0),lastCorrect:correct};}
function submitAnswer(correct,response,extra={}){
 const r=currentRun();if(!r||r.answers[r.position]||solved)return;const q=currentTask(),test=r.mode==='test';r.attempts=(r.attempts||0)+1;
 if(!correct&&!test){scheduleReview(q.id,false);feedback('Попробуй ещё раз. '+q.explanation,'try');if(Number.isInteger(extra.chosen))$('activity').querySelector(`[data-choice="${extra.chosen}"]`)?.classList.add('incorrect');save();return;}
 const a={taskId:q.id,moduleId:q.moduleId,correct:!!correct,firstTry:r.attempts===1&&!r.hinted&&!q.manual,response:String(response),expected:expected(q),at:now(),...extra};r.answers.push(a);solved=true;
 if(!test)scheduleReview(q.id,q.manual?correct:a.firstTry);
 if(!test&&!q.checkOnly){const p=training(q.moduleId);p.done[q.id]={at:now(),firstTry:a.firstTry};p.cursor=q.id;}
 save();restoreAnswer(a,test,q);renderSessionSide(r,test);
}
function restoreAnswer(a,test,q){
 solved=true;$('activity').querySelectorAll('[data-choice],[data-token],#submit-answer,#clear-tokens,#clock-hour,#clock-minute,#hint-task,#written-answer,[data-match-left],[data-match-right],#clear-matches,[data-ink],#undo-stroke,#clear-drawing,#manual-good,#manual-retry').forEach(b=>{b.disabled=true;if(b.hasAttribute('data-choice')&&Number(b.dataset.choice)===a.chosen)b.classList.add(test?'selected-answer':'correct');});
 feedback(test?'Ответ сохранён. Итог появится в конце.':(q.manual?'Проверили вместе. ':'Получилось! ')+q.explanation,test?'neutral':'good');$('next-question').disabled=false;
 if(!test&&q.audioOnly){const h=$('hint-sentence');h.hidden=false;h.textContent=q.speech;}
}
function renderSessionSide(r,test){const manual=r.items.every(q=>q.manual);$('side-panel').innerHTML=`<div class="side-card blue-card"><h3>${test?'Самостоятельная проверка':'Шаг за шагом'}</h3><div class="progress-rail"><span style="width:${r.answers.length/r.items.length*100}%"></span></div><p>${r.answers.length} из ${r.items.length} ответов сохранено</p></div><div class="side-card"><h3>${test?'Попробуй сама':manual?'Проверяем вместе':'Можно учиться на ошибках'}</h3><p>${manual?'Обводку, почерк и рисунок обсуждаем вместе со взрослым. Сохранённое выполнение не означает самостоятельную оценку.':test?'Один ответ на задание. Можно слушать несколько раз. Подсказки и исправления появятся после завершения.':'Слушай, читай объяснение и пробуй снова. Повторный ответ помогает учиться, но не считается самостоятельной проверкой.'}</p><p>Можно выйти и продолжить позже.</p></div>`;}
function nextQuestion(){
 const r=currentRun();if(!r||!r.answers[r.position])return;stopSpeech();solved=false;selected=[];
 if(r.position<r.items.length-1){r.position++;r.attempts=0;r.hinted=false;r.draft=null;save();render();return;}
 if(r.mode==='test'){const t=testing(r.owner),result={id:r.id,finishedAt:now(),total:r.items.length,score:r.answers.filter(a=>a.correct).length,answers:r.answers,items:r.items};if(!t.history.some(h=>h.id===r.id)){t.history.unshift(result);r.answers.forEach(a=>scheduleReview(a.taskId,a.correct));}t.history=t.history.slice(0,10);t.active=null;save();openResult(r.owner,0);}
 else{state.lastPractice={mode:r.mode,owner:r.owner,total:r.items.length,firstTry:r.answers.filter(a=>a.firstTry).length,manualCount:r.answers.filter(a=>a.manual).length};if(r.mode==='daily')state.daily={date:localDate(),complete:true};state.practice=null;resultTarget=null;view='practice-finish';save();render();}
}
function renderPracticeFinish(){
 const r=state.lastPractice||{total:0,firstTry:0},m=MODULES.get(r.owner);$('activity').innerHTML=heading(m?.adventure?'Приключение завершено!':'Хорошо позанимались!',m?.adventure?({'adventure-school':'Рюкзак собран: капибара готова к школе!','adventure-shop':'Покупки сделаны: капибара благодарит за помощь!','adventure-day':'План готов: у капибары хватит времени на отдых и занятия.'}[m.id]):'Теперь можно отдохнуть или выбрать следующий блок.')+`<div class="finish-illustration"><img src="assets/capybara.svg" alt="Капибара"></div><p class="finish-copy">Выполнено ${r.total} заданий.${r.manualCount===r.total?' Проверили работу вместе со взрослым.':` Без подсказки с первой попытки получилось ${r.firstTry}.`}</p><p class="muted">${m?.practiceOnly?'Можно пройти занятие ещё раз или выбрать следующий блок.':'Это результат тренировки. Для самостоятельной оценки есть отдельная проверка.'}</p><div class="button-row"><button class="primary" data-home="today">На главную</button><button class="secondary" data-home="learn">Выбрать блок</button>${MODULES.has(r.owner)&&!MODULES.get(r.owner).practiceOnly?`<button class="secondary" data-test="module:${r.owner}">Проверить себя</button>`:''}</div>`;progressSide();
}
function openResult(target,index=0){stopSpeech();resultTarget=target;resultIndex=index;view='result';tab='learn';activeModule=target.startsWith('module:')?target.slice(7):null;activeSection=activeModule?MODULES.get(activeModule).section:target.slice(8);render();}
function renderResult(){
 const history=testing(resultTarget).history,r=history[resultIndex];if(!r){navigate('learn');return;}const wrong=r.answers.map((a,i)=>({...a,index:i})).filter(a=>!a.correct),label=resultTarget.startsWith('module:')?MODULES.get(resultTarget.slice(7)).title:CURRICULUM.sections.find(s=>s.id===resultTarget.slice(8)).title;
 const groups=Object.fromEntries([...new Set(r.answers.map(a=>a.moduleId))].map(id=>{const rows=r.answers.filter(a=>a.moduleId===id);return [id,{correct:rows.filter(a=>a.correct).length,total:rows.length}];}));
 $('activity').innerHTML=backbar()+heading('Проверка завершена',label)+`<div class="test-score">${r.score}<span> / ${r.total}</span></div><p class="score-note">${wrong.length?'Посмотрим, что стоит потренировать.':'Все ответы получились с первой попытки!'}</p>${resultTarget.startsWith('section:')?`<div class="skill-results">${Object.entries(groups).map(([id,s])=>`<div><span>${mixed(MODULES.get(id).title)}</span><strong>${s.correct}/${s.total}</strong></div>`).join('')}</div>`:''}${wrong.length?`<div class="test-review"><h2>Разберём ошибки</h2>${wrong.map(a=>{const q=r.items?.[a.index]||TASKS.get(a.taskId);return `<article class="test-error"><span class="eyebrow">${mixed(MODULES.get(a.moduleId).title)}</span><p class="test-question" lang="en">${mixed(q.stimulus||q.speech||q.ru||q.prompt)}</p>${figure(q)}${q.ru?`<p>${mixed(q.ru)}</p>`:''}<p>Твой ответ: <strong>${mixed(a.response)}</strong></p><p>Правильный ответ: <strong>${mixed(a.expected)}</strong></p>${q.complete?`<p lang="en">${esc(q.complete)}</p>`:''}${q.kind==='choice'&&q.choices[q.correct].scene?scene(q.choices[q.correct].scene):q.kind==='clock-set'?clockFace(q.hour,q.minute):''}<p class="muted">${mixed(q.explanation)}</p><button class="secondary" data-practice-task="${a.taskId}">Потренировать</button></article>`;}).join('')}</div>`:''}<div class="button-row result-actions"><button class="primary" data-test="${resultTarget}">${testing(resultTarget).active?'Продолжить проверку':'Новая проверка'}</button><button class="secondary" ${activeModule?`data-module="${activeModule}"`:`data-section="${activeSection}"`}>${activeModule?'К учебному блоку':'К разделу'}</button></div>${history.length>1?`<div class="test-history"><h3>Последние проверки</h3>${history.map((h,i)=>`<button class="text-button" data-history="${i}">${new Date(h.finishedAt).toLocaleDateString('ru-RU')} · ${h.score}/${h.total}</button>`).join('')}</div>`:''}`;
 $('activity').querySelectorAll('[data-history]').forEach(b=>b.onclick=()=>openResult(resultTarget,Number(b.dataset.history)));
 $('activity').querySelectorAll('[data-practice-task]').forEach(b=>b.onclick=()=>{const q=TASKS.get(b.dataset.practiceTask);if(!replacePractice(makeRun([q],'module',q.moduleId)))return;resultTarget=null;view='session';activeModule=q.moduleId;tab='learn';render();});
 $('side-panel').innerHTML=`<div class="side-card blue-card"><h3>Первая попытка</h3><p>${r.score} из ${r.total} самостоятельно</p><p>${new Date(r.finishedAt).toLocaleString('ru-RU')}</p></div><div class="side-card"><h3>Дальше</h3><p>Повтори трудные задания. Новая проверка выбирает задания заново и перемешивает ответы.</p></div>`;
}
function renderReview(){
 const due=dueTasks(),later=Object.keys(state.review).length-due.length,active=state.practice?.mode==='review';
 $('activity').innerHTML=heading('Повторяем','Трудные задания возвращаются сразу; успешные — через 1, 3, 7 и 14 дней.')+`<div class="training-card"><h2>${due.length?'Есть что повторить':'На сейчас всё повторено'}</h2><p>${due.length} заданий сейчас · ${later} назначено на следующие дни.</p><div class="button-row">${due.length||active?`<button class="primary" id="review-start">${active?'Продолжить повторение':'Повторить сейчас'}</button>`:''}${Object.keys(state.review).length?'<button class="secondary" id="review-all">Повторить заранее</button>':''}<button class="text-button" data-home="learn">Выбрать новый блок</button></div></div><div class="review-list">${due.slice(0,12).map(q=>`<div><strong>${mixed(MODULES.get(q.moduleId).title)}</strong><span>${mixed(q.audioOnly?'Задание на слух':q.stimulus||q.ru||q.prompt)}</span></div>`).join('')}</div>`;
 if($('review-start'))$('review-start').onclick=()=>startReview();if($('review-all'))$('review-all').onclick=()=>startReview(true);progressSide();
}
function renderDictionary(){
 if(!wordTopic){$('activity').innerHTML=heading('Наш словарь','240 слов: картинки, транскрипция и примеры.')+`<div class="section-grid dictionary-topics">${TOPICS.map(t=>{const words=VOCAB.filter(w=>w.topic===t.id);return `<button class="section-card" data-word-topic="${t.id}"><span aria-hidden="true">${TOPIC_ICONS[t.id]}</span><strong>${t.title}</strong><small>${words.filter(w=>state.words.includes(w.en)).length}/${words.length} повторено</small></button>`;}).join('')}</div>`;$('activity').querySelectorAll('[data-word-topic]').forEach(b=>b.onclick=()=>{wordTopic=b.dataset.wordTopic;activeWord=null;render();});}
 else{const words=VOCAB.filter(w=>w.topic===wordTopic),w=WORDS.get(activeWord);$('activity').innerHTML=`<button class="text-button" id="dictionary-back">Все словарные темы</button>`+heading(TOPICS.find(t=>t.id===wordTopic).title,'Выбери слово, послушай и повтори.')+(w?`<div class="word-stage">${scene({word:w.en})}<div><div class="word-en" lang="en">${esc(w.en)}</div><div class="word-ipa" lang="en">[${esc(w.ipa)}]</div><div class="word-ru">${esc(w.ru)}</div><p class="word-example" lang="en">${esc(w.example)}</p><div class="button-row"><button class="secondary" data-speech="${esc(w.en)}">${icon('volume-2')}Слово</button><button class="secondary" data-speech="${esc(w.example)}">${icon('volume-2')}Фраза</button></div></div></div><button class="primary" id="mark-word">${state.words.includes(w.en)?'Слово уже повторено':'Я повторила слово'}</button>`:'<div class="word-empty">📖<h2>Выбери слово ниже</h2><p>Открытие темы и карточки не засчитывается как повторение.</p></div>')+`<div class="word-grid">${words.map(w=>`<button class="word-button ${state.words.includes(w.en)?'viewed':''} ${w.en===activeWord?'current':''}" data-word="${esc(w.en)}" lang="en">${esc(w.en)}${state.words.includes(w.en)?'<span aria-label="Повторено"> ✓</span>':''}</button>`).join('')}</div>`;
 $('dictionary-back').onclick=()=>{wordTopic=null;activeWord=null;render();};$('activity').querySelectorAll('[data-word]').forEach(b=>b.onclick=()=>{stopSpeech();activeWord=b.dataset.word;render();});if($('mark-word'))$('mark-word').onclick=()=>{if(!state.words.includes(w.en))state.words.push(w.en);save();render();};}
 progressSide();
}
function renderParent(){
 const rows=CURRICULUM.modules.map(m=>{const h=state.tests['module:'+m.id]?.history||[],last=h[0],active=state.tests['module:'+m.id]?.active;return `<tr><th scope="row">${mixed(m.title)}</th><td>${moduleCount(m.id)}/${m.tasks.length}</td><td>${last?`<button class="text-button" data-parent-result="module:${m.id}">${last.score}/${last.total}</button>`:active?'В процессе':m.practiceOnly?'Совместная работа':'—'}</td></tr>`;}).join('');
 const sections=CURRICULUM.sections.filter(s=>state.tests['section:'+s.id]?.history.length);
 $('parent-content').innerHTML=`<p>Тренировки допускают подсказки и повторные попытки. Проверки учитывают первый ответ и показывают самостоятельный результат. Произношение ребёнка оценивайте вместе: голос не записывается.</p><div class="table-scroll"><table class="parent-table"><caption>Учебные блоки</caption><thead><tr><th>Блок</th><th>Тренировка</th><th>Проверка</th></tr></thead><tbody>${rows}</tbody></table></div>${sections.length?`<h3>Проверки разделов</h3>${sections.map(s=>{const h=state.tests['section:'+s.id].history[0];return `<button class="parent-result" data-parent-result="section:${s.id}">${s.title}: ${h.score}/${h.total}</button>`;}).join('')}`:''}<p>Хранятся последние 10 проверок каждого блока и раздела. Результаты остаются в этом браузере; очистка его данных удалит прогресс.</p><button class="text-button" id="reset-all">Начать всё заново</button>`;
 $('parent-content').querySelectorAll('[data-parent-result]').forEach(b=>b.onclick=()=>{$('settings-dialog').close();openResult(b.dataset.parentResult,0);});
 $('reset-all').onclick=()=>{if(!confirm('Удалить прогресс слов, тренировок и проверок?'))return;const prefs={voice:state.voice,rate:state.rate};state={...freshState(),...prefs};resultTarget=null;$('settings-dialog').close();wordTopic=null;activeWord=null;navigate('today');};
}
$('settings').onclick=()=>{voiceList();$('speed').value=state.rate;$('speed-value').textContent=state.rate.toFixed(2);renderParent();$('settings-dialog').showModal();};
$('voice').onchange=()=>{state.voice=$('voice').value;save();};$('speed').oninput=()=>{state.rate=Number($('speed').value);$('speed-value').textContent=state.rate.toFixed(2);save();};$('test-voice').onclick=()=>speak('Hello! Let us learn English together.');
document.querySelector('.brand').onclick=e=>{e.preventDefault();navigate('today');};
document.addEventListener('visibilitychange',()=>{if(document.hidden)stopSpeech();});
if(window.speechSynthesis){speechSynthesis.addEventListener('voiceschanged',voiceList);voiceList();}
save();render();
if('serviceWorker' in navigator&&location.protocol!=='file:')navigator.serviceWorker.register('./sw.js').catch(()=>{});
