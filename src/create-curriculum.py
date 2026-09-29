"""Content catalog. Runtime and storage refer to stable module/task identifiers."""
from pathlib import Path
import json,random,re

base=Path(__file__).resolve().parent
rng=random.Random(42)
vocab=json.loads((base/'curriculum-vocab.json').read_text(encoding='utf-8'))['words']
sections=[
 {'id':'sounds','title':'Звуки и чтение слов','icon':'🔤','description':'От букв и звуков к самостоятельному чтению.'},
 {'id':'grammar','title':'Грамматика','icon':'🧠','description':'Небольшие правила, из которых складывается язык.'},
 {'id':'phrases','title':'Строим фразы','icon':'🧩','description':'Описываем, спрашиваем и рассказываем о себе.'},
 {'id':'understanding','title':'Читаем и слушаем','icon':'🎧','description':'Понимаем предложения, инструкции, диалоги и истории.'},
 {'id':'numbers','title':'Числа и время','icon':'🕒','description':'Считаем, называем время и понимаем расписание.'}]
modules=[]
def add(mid,section,title,description,rules,examples,tasks,prerequisites=()):
 for i,q in enumerate(tasks):
  q['id']=f'{mid}-{i+1:02d}';q['moduleId']=mid;q['skills']=[mid]
  corpus=' '.join([q.get('stimulus',''),q.get('speech',''),q.get('complete','')]).lower()
  q['themes']=sorted({w['topic'] for w in vocab if re.search(r'\b'+re.escape(w['en'])+r'\b',corpus)})
  q.setdefault('explanation',rules[0]);q.setdefault('difficulty',1 if not prerequisites else 2)
 modules.append(dict(id=mid,section=section,title=title,description=description,rules=rules,examples=[{'en':en,'ru':ru} for en,ru in examples],tasks=tasks,prerequisites=list(prerequisites)))
def choice(prompt,stimulus,choices,correct,ru='',**extra):
 options=[dict(text=c,lang='ru' if re.search(r'[А-Яа-яЁё]',c) else 'en') if isinstance(c,str) else c for c in choices]
 order=list(range(len(options)));rng.shuffle(order)
 return dict(kind='choice',prompt=prompt,stimulus=stimulus,ru=ru,choices=[options[i] for i in order],correct=order.index(correct),**extra)
def gap(text,ru,correct,wrong,explanation=''):
 return choice('Вставь слово вместо пропуска.',text,[correct,*wrong],0,ru,complete=text.replace('___',correct),explanation=explanation)
def build(en,ru,**extra):
 answer=re.sub(r'[.,!?]','',en).split();tokens=answer.copy();rng.shuffle(tokens)
 return dict(kind='build',prompt='Собери фразу по-английски.',stimulus='',speech=en,ru=ru,answer=answer,tokens=tokens,complete=en,**extra)
def numbered(n):
 small=['zero','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen']
 if n<20:return small[n]
 if n==100:return 'one hundred'
 tens=['','','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']
 return tens[n//10]+('-'+small[n%10] if n%10 else '')
def num_options(n,lo,hi):return [n,*rng.sample([x for x in range(lo,hi+1) if x!=n],3)]

# SOUNDS: browser speech always pronounces whole words or letter names.
alphabet=list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
tasks=[choice('Послушай название буквы и найди её.','',[c,alphabet[(i+7)%26],alphabet[(i+15)%26]],0,speech=c,audioOnly=True,explanation=f'Это буква {c}. Название буквы и звук в слове могут различаться.') for i,c in enumerate(alphabet)]
for sound,w,other in [('b','bag',['dog','cat']),('d','dog',['bag','pen']),('k','cat',['sun','bed']),('p','pen',['dog','cat']),('s','sun',['pig','dog']),('m','mother',['father','sun'])]:
 tasks.append(choice('Найди слово с указанным первым звуком.',f'/{sound}/',[w,*other],0,speech=w,explanation=f'В начале слова {w} слышится /{sound}/.'))
add('letters','sounds','Буквы и первые звуки','Узнаём 26 букв и слышим начало слова.',[
 'В английском алфавите 26 букв. У буквы есть название, а в слове она передаёт звук. Например, B называется «би», но bag начинается со звука /b/.',
 'Слушай целое слово, затем обращай внимание на первый звук. Кнопки букв ниже озвучивают именно названия букв.'],[('B — bag','Буква B, слово «рюкзак»'),('C — cat','Буква C, слово «кошка»')],tasks)
short=[('cat','/æ/'),('bag','/æ/'),('hat','/æ/'),('pen','/e/'),('bed','/e/'),('red','/e/'),('pig','/ɪ/'),('fish','/ɪ/'),('big','/ɪ/'),('dog','/ɒ/'),('cup','/ʌ/'),('sun','/ʌ/')]
tasks=[choice('Послушай слово. Какой гласный звук слышен?','',[s,*[x for x in ['/æ/','/e/','/ɪ/','/ɒ/','/ʌ/'] if x!=s][:2]],0,speech=w,audioOnly=True,explanation=f'{w}: гласный звук {s}. Сравни с примерами в объяснении.') for w,s in short]
add('short-vowels','sounds','Короткие гласные','Сравниваем гласные в коротких словах.',[
 'Слушай примеры: cat /æ/, pen /e/, pig /ɪ/, dog /ɒ/, cup /ʌ/. Здесь используется британское произношение; для занятий удобно выбрать британский голос.',
 'Знаки в косых чертах обозначают звуки. Читай короткое слово целиком и сравнивай его звучание с образцом.'],[(w,s) for w,s in short[:1]+short[3:4]+short[6:7]+short[9:]],tasks,('letters',))
groups=[('fish','sh'),('shirt','sh'),('shoe','sh'),('sheep','sh'),('chair','ch'),('cheese','ch'),('child','ch'),('teacher','ch'),('three','th'),('mother','th'),('brother','th'),('tooth','th')]
tasks=[choice('Послушай слово. Какое сочетание букв в нём слышится?','',['sh','ch','th'],['sh','ch','th'].index(g),speech=w,audioOnly=True,explanation=f'{w}: сочетание {g}.') for w,g in groups]
add('letter-groups','sounds','Сочетания sh, ch и th','Две буквы могут передавать один звук.',[
 'sh часто передаёт /ʃ/: fish, sheep. ch часто передаёт /tʃ/: chair, cheese.',
 'th может передавать /θ/ в three или /ð/ в mother. Для этих звуков кончик языка находится у зубов. Послушай примеры и повтори вместе со взрослым.'],[('fish — sheep','В обоих словах есть sh'),('chair — cheese','В обоих словах есть ch'),('three — mother','В обоих словах есть th, но звук различается')],tasks,('letters',))
long=[('see','ee'),('green','ee'),('sheep','ee'),('tree','ee'),('feet','ee'),('bee','ee'),('eat','ea'),('meat','ea'),('sea','ea'),('leaf','ea'),('teacher','ea'),('head','exception')]
tasks=[choice('Послушай и прочитай слово. Что обозначает его гласный звук?',w,['Долгий /iː/','Короткий /e/','Короткий /ʌ/'],1 if w=='head' else 0,speech=w,explanation=f'{w}: '+('ea звучит /e/. Это исключение.' if w=='head' else 'здесь слышится долгий /iː/.')) for w,g in long]
add('long-vowels','sounds','Долгий звук: ee и ea','Читаем сочетания и замечаем исключения.',[
 'В see, green, sheep сочетание ee передаёт долгий /iː/. В eat, meat, leaf такой же звук передаёт ea.',
 'У ea есть исключения: head и bread произносятся с /e/. Слушай слово целиком, а не угадывай по буквам.'],[('green — leaf','Один долгий звук, разные сочетания букв'),('head — bread','Здесь ea передаёт /e/')],tasks,('short-vowels',))
read_words=['bag','book','cat','dog','apple','banana','shirt','shoe','tree','flower','doctor','football']
tasks=[]
for i,w in enumerate(read_words):
 alternatives=[w,read_words[(i+3)%12],read_words[(i+7)%12]]
 tasks.append(choice('Прочитай слово и выбери картинку.',w,[{'scene':{'word':a}} for a in alternatives],0,speech=w))
add('read-words','sounds','Читаем слова','Соединяем написание, звучание и значение.',[
 'Сначала попробуй прочитать слово сама. Найди его картинку, затем проверь чтение кнопкой озвучки.',
 'Транскрипцию и пример предложения можно посмотреть в словаре.'],[('cat','кошка'),('tree','дерево'),('doctor','врач')],tasks,('letters',))
pairs=[('cat','cut'),('ship','sheep'),('bed','bad'),('pin','pen'),('thin','tin'),('three','tree')]
tasks=[]
for a,b in pairs:
 for w in [a,b]:tasks.append(choice('Послушай внимательно. Какое слово прозвучало?','',[a,b],0 if w==a else 1,speech=w,audioOnly=True,explanation=f'Сравни звучание пары: {a} — {b}.'))
add('similar-sounds','sounds','Похожие звуки','Слышать разницу в похожих словах.',[
 'Некоторые слова отличаются одним звуком: cat — cut, ship — sheep, bed — bad.',
 'Сначала слушай медленно. После ответа сравни два слова по кнопкам в объяснении. В тесте выбирай то слово, которое услышала.'],[('cat — cut','кошка — резать'),('ship — sheep','корабль — овца'),('thin — tin','тонкий — жестяная банка')],tasks,('short-vowels','letter-groups'))

# GRAMMAR: focused tasks with unambiguous context.
nouns=[('bag','рюкзак'),('book','книга'),('cat','кошка'),('dog','собака'),('pen','ручка'),('teacher','учитель'),('apple','яблоко'),('egg','яйцо'),('orange','апельсин'),('elephant','слон'),('artist','художник'),('astronaut','космонавт')]
tasks=[gap('This is ___ '+w+'.','Это '+ru+'.','an' if w[0] in 'aeiou' else 'a',['a' if w[0] in 'aeiou' else 'an','—'],'Перед единственным исчисляемым предметом используем a/an: выбираем по первому звуку следующего слова.') for w,ru in nouns]
add('articles-a-an','grammar','Артикли a и an','Один предмет, о котором говорим впервые.',[
 'Перед названием одного исчисляемого предмета обычно ставим a или an: a cat, an apple.',
 'a — перед согласным звуком, an — перед гласным. Смотрим на звук следующего слова: a big apple, an old book. Здесь знак «—» означает, что слова в пропуске нет.'],[('a cat','кошка'),('an apple','яблоко'),('an old book','старая книга')],tasks)
tasks=[]
for w,ru in nouns:
 article='an' if w[0] in 'aeiou' else 'a'
 tasks.append(gap(f'I can see {article} {w}. ___ {w} is here.',f'Я вижу предмет: {ru}. Затем говорю о нём ещё раз.','The',['A','An'],'Предмет уже назван. Во второй фразе используем the.'))
add('articles-the','grammar','Артикль the','Говорим о том самом, уже известном предмете.',[
 'Сначала называем новый предмет: I see a dog. Затем говорим о той же собаке: The dog is big.',
 'the помогает показать, что собеседник понимает, о каком предмете речь. В этих заданиях он уже назван в первом предложении.'],[('I have a book. The book is new.','У меня есть книга. Эта книга новая.')],tasks,('articles-a-an',))
generic=[('cats','кошки'),('dogs','собаки'),('apples','яблоки'),('bananas','бананы'),('birds','птицы'),('flowers','цветы'),('books','книги'),('rabbits','кролики'),('milk','молоко'),('water','вода'),('rice','рис'),('bread','хлеб')]
tasks=[gap('I like ___ '+w+'.',('Мне нравятся ' if w.endswith('s') else 'Мне нравится ')+ru+' вообще, без указания на конкретные предметы.','—',['a','an'],'Перед множественным числом и неисчисляемыми названиями в таком общем высказывании a/an не ставим.') for w,ru in generic]
for q in tasks:q['complete']=q['complete'].replace(' — ',' ')
add('articles-zero','grammar','Когда артикль не нужен','Общие высказывания о предметах, еде и напитках.',[
 'Когда говорим о кошках вообще: I like cats. Перед cats здесь нет артикля.',
 'В общих высказываниях milk, water, bread тоже могут идти без артикля: I drink water. «—» в ответе означает отсутствие слова. Это начальный блок, не все случаи употребления артиклей.'],[('I like apples.','Мне нравятся яблоки вообще.'),('I drink water.','Я пью воду.')],tasks,('articles-a-an',))
plurals=[('cat','cats','кошки'),('dog','dogs','собаки'),('book','books','книги'),('pen','pens','ручки'),('apple','apples','яблоки'),('box','boxes','коробки'),('bus','buses','автобусы'),('baby','babies','малыши'),('child','children','дети'),('mouse','mice','мыши'),('foot','feet','ступни'),('tooth','teeth','зубы')]
tasks=[choice('Выбери форму для нескольких предметов.',f'one {a} → two ___',[b,a,a+'ing'],0,ru=ru,explanation=f'Один: {a}. Несколько: {b}.') for a,b,ru in plurals]
add('plurals','grammar','Один и несколько','Множественное число и первые исключения.',[
 'Часто добавляем -s: cat — cats. Иногда -es: box — boxes. В baby окончание меняется: babies.',
 'Есть особые формы: child — children, mouse — mice, foot — feet, tooth — teeth.'],[('one cat — two cats','одна кошка — две кошки'),('one child — two children','один ребёнок — двое детей')],tasks)
pronouns=[('Я','I'),('Ты','you'),('Он','he'),('Она','she'),('Оно / это','it'),('Мы','we'),('Вы','you'),('Они','they'),('Мама','she'),('Папа','he'),('Мама и папа','they'),('Я и моя подруга','we')]
tasks=[choice('Выбери подходящее местоимение.',ru,[en,*[x for x in ['I','you','he','she','it','we','they'] if x!=en][:2]],0,explanation=f'{ru} → {en}.') for ru,en in pronouns]
add('pronouns','grammar','Я, ты, он, она, мы, они','Заменяем имена и названия местоимениями.',[
 'I — я; you — ты или вы; he — он; she — она; it — предмет или животное, когда его пол не уточняется; we — мы; they — они.',
 'I всегда пишется с большой буквы. Мама и папа вместе — they, а я и подруга — we.'],[('She is my mother.','Она моя мама.'),('We are friends.','Мы друзья.')],tasks)
be_rows=[('I','am','happy','Я рада.'),('You','are','kind','Ты добрый.'),('He','is','a boy','Он мальчик.'),('She','is','a girl','Она девочка.'),('It','is','a cat','Это кошка.'),('We','are','friends','Мы друзья.'),('They','are','at school','Они в школе.'),('The book','is','new','Книга новая.'),('The cats','are','small','Кошки маленькие.'),('My mother','is','a doctor','Моя мама врач.'),('I','am','at home','Я дома.'),('You','are','ready','Ты готова.')]
tasks=[gap(f'{subject} ___ {ending}.',ru,verb,[x for x in ['am','is','are'] if x!=verb],'I am; he/she/it is; you/we/they are. С одним предметом — is, с несколькими — are.') for subject,verb,ending,ru in be_rows]
add('be','grammar','Am, is и are','Кто это, какой он и где находится.',[
 'I am; he/she/it is; you/we/they are. В английском эти слова нужны там, где в русском их часто нет: The cat is small — Кошка маленькая.',
 'С одним названным предметом используем is, с несколькими — are.'],[('I am happy.','Я рада.'),('The book is new.','Книга новая.'),('We are at home.','Мы дома.')],tasks,('pronouns',))
have_rows=[('I','have','a bag','У меня есть рюкзак.'),('You','have','a book','У тебя есть книга.'),('He','has','a dog','У него есть собака.'),('She','has','a cat','У неё есть кошка.'),('We','have','two pens','У нас две ручки.'),('They','have','a ball','У них есть мяч.'),('My sister','has','a toy','У моей сестры есть игрушка.'),('The boy','has','a bike','У мальчика есть велосипед.'),('The girls','have','books','У девочек есть книги.'),('I','have','two hands','У меня две руки.'),('The cat','has','green eyes','У кошки зелёные глаза.'),('You','have','a new hat','У тебя новая шляпа.')]
tasks=[gap(f'{s} ___ {end}.',ru,v,['has' if v=='have' else 'have','am'],'I/you/we/they have; he/she/it has.') for s,v,end,ru in have_rows]
add('have','grammar','Have и has','Говорим, что у кого-то есть.',[
 'I/you/we/they have. He/she/it has. Имя или один человек тоже требуют has: My sister has a toy.'],[('I have a bag.','У меня есть рюкзак.'),('She has a cat.','У неё есть кошка.')],tasks,('pronouns',))
canverbs=[('swim','плавать'),('run','бегать'),('jump','прыгать'),('read','читать'),('write','писать'),('sing','петь'),('dance','танцевать'),('draw','рисовать'),('play','играть'),('walk','ходить'),('open','открывать'),('count','считать')]
tasks=[gap(f'{["I","She","He","We"][i%4]} can ___.' ,'Умеет / умеем '+ru+'.',v,[v+'s',v+'ing'],'После can используем глагол без -s и -ing.') for i,(v,ru) in enumerate(canverbs)]
for i,q in enumerate(tasks):q['ru']=['Я умею ','Она умеет ','Он умеет ','Мы умеем '][i%4]+canverbs[i][1]+'.'
add('can','grammar','Can: умею и могу','Глагол после can не меняется.',[
 'I can swim. She can swim. После can не добавляем к глаголу -s или -ing.',
 'Вопрос начинается с Can: Can you swim? Отрицание: cannot или короткое can’t.'],[('She can swim.','Она умеет плавать.'),('Can you sing?','Ты умеешь петь?')],tasks,('pronouns',))
simple=[('I','play','football','Я играю в футбол.'),('She','plays','tennis','Она играет в теннис.'),('He','reads','books','Он читает книги.'),('We','read','at school','Мы читаем в школе.'),('They','drink','water','Они пьют воду.'),('My brother','runs','every day','Мой брат бегает каждый день.'),('You','like','apples','Тебе нравятся яблоки.'),('My sister','likes','cats','Моей сестре нравятся кошки.'),('The teacher','works','at school','Учитель работает в школе.'),('We','walk','to school','Мы идём в школу пешком.'),('She','eats','breakfast at home','Она завтракает дома.'),('I','help','my mother','Я помогаю маме.')]
tasks=[]
for s,v,end,ru in simple:
 baseverb=v[:-1] if v.endswith('s') else v
 tasks.append(gap(f'{s} ___ {end}.',ru,v,[baseverb if v!=baseverb else v+'s',baseverb+'ing'],'В обычном действии с he/she/it к этим глаголам добавляем -s. С I/you/we/they — без -s.'))
add('present-simple','grammar','Обычные действия','Что делаем обычно или каждый день.',[
 'I play, you play, we play, they play. Но he plays, she plays. В этом блоке тренируем обычные глаголы с простым окончанием -s.',
 'Вопросы с do/does и отрицания don’t/doesn’t разбираются отдельно в разделе построения фраз.'],[('I play football.','Я играю в футбол.'),('She reads every day.','Она читает каждый день.')],tasks,('pronouns',))
continuous=[('I','am','reading','Я сейчас читаю.'),('She','is','swimming','Она сейчас плавает.'),('He','is','running','Он сейчас бежит.'),('We','are','playing','Мы сейчас играем.'),('They','are','singing','Они сейчас поют.'),('You','are','drawing','Ты сейчас рисуешь.'),('The cat','is','sleeping','Кошка сейчас спит.'),('The children','are','dancing','Дети сейчас танцуют.'),('My mother','is','cooking','Моя мама сейчас готовит.'),('I','am','writing','Я сейчас пишу.'),('My brother','is','eating','Мой брат сейчас ест.'),('We','are','walking','Мы сейчас идём пешком.')]
tasks=[gap(f'{s} ___ {v} now.',ru,b,[x for x in ['am','is','are'] if x!=b],'Действие сейчас: am/is/are + глагол с -ing.') for s,b,v,ru in continuous]
add('present-continuous','grammar','Что происходит сейчас','Am/is/are вместе с глаголом на -ing.',[
 'Чтобы описать действие сейчас, используем am/is/are + глагол с -ing: I am reading. She is swimming.',
 'Правописание иногда меняется: run → running, swim → swimming, write → writing. В этих упражнениях форма на -ing уже дана.'],[('I am reading now.','Я сейчас читаю.'),('They are playing.','Они сейчас играют.')],tasks,('be','present-simple'))
tasks=[]
for i,(w,ru) in enumerate(nouns):
 n=1 if i%2==0 else 2;article='an' if w[0] in 'aeiou' else 'a';end=f'{article} {w}' if n==1 else f'two {w}s'
 plural_ru={'bag':'два рюкзака','book':'две книги','cat':'две кошки','dog':'две собаки','pen':'две ручки','teacher':'два учителя','apple':'два яблока','egg':'два яйца','orange':'два апельсина','elephant':'два слона','artist':'два художника','astronaut':'два космонавта'}
 tasks.append(gap(f'There ___ {end}.','Здесь '+(ru if n==1 else plural_ru[w])+'.','is' if n==1 else 'are',['are' if n==1 else 'is','am'],'There is — один предмет. There are — несколько.'))
add('there-is-are','grammar','There is и there are','Говорим, что где-то есть предметы.',[
 'There is a cat — Здесь есть кошка. There are two cats — Здесь две кошки.',
 'Выбираем is или are по количеству предметов.'],[('There is a book on the table.','На столе есть книга.'),('There are two books.','Здесь две книги.')],tasks,('be','plurals'))
tasks=[]
for i,w in enumerate(['bag','book','pencil','toy']):
 for pos,ru in [('on','на'),('under','под'),('beside','рядом с')]:
  tasks.append(choice('Где находится предмет?',f'The {w} is ___ the table.',['on','under','beside'],['on','under','beside'].index(pos),figure={'type':'scene','scene':{'word':w,'position':pos}},explanation={'on':'on: предмет на столе.','under':'under: предмет под столом.','beside':'beside: предмет рядом со столом.'}[pos]))
add('prepositions','grammar','На, под и рядом','Положение предмета: on, under, beside.',[
 'on — на; under — под; beside — рядом с. Смотри, где находится предмет относительно стола.'],[('The book is on the table.','Книга на столе.'),('The bag is under the table.','Рюкзак под столом.')],tasks,('be',))

# PHRASES: sentence building, transformations, questions and short answers.
tasks=[build(f'This is {"an" if w[0] in "aeiou" else "a"} {w}.','Это '+ru+'.') for w,ru in nouns]
add('name-object','phrases','Называем предмет','Собираем первое полное предложение.',[
 'This is + a/an + название предмета: This is a cat. Не забывай is и артикль.'],[('This is an apple.','Это яблоко.'),('This is a book.','Это книга.')],tasks,('articles-a-an','be'))
descriptions=[('The cat is small.','Кошка маленькая.'),('The dog is big.','Собака большая.'),('It is a red ball.','Это красный мяч.'),('It is a blue bag.','Это синий рюкзак.'),('The book is new.','Книга новая.'),('The chair is old.','Стул старый.'),('The flower is yellow.','Цветок жёлтый.'),('The apples are green.','Яблоки зелёные.'),('The rabbit has long ears.','У кролика длинные уши.'),('The bird is small and blue.','Птица маленькая и синяя.'),('This is a beautiful picture.','Это красивая картина.'),('The elephant has a long nose.','У слона длинный нос.')]
add('describe-object','phrases','Описываем предмет и животное','Цвет, размер, качество и части тела.',[
 'После is можно назвать качество: The cat is small. Перед названием предмета прилагательное ставим раньше существительного: a red ball.',
 'Чтобы рассказать о частях тела, используем has: The rabbit has long ears.'],descriptions[:3],[build(en,ru) for en,ru in descriptions],('be','have','articles-a-an'))
actions=[('I play football.','Я играю в футбол.'),('She reads a book.','Она читает книгу.'),('We drink water.','Мы пьём воду.'),('He is running now.','Он сейчас бежит.'),('They are playing tennis.','Они сейчас играют в теннис.'),('I can swim.','Я умею плавать.'),('My mother cooks dinner.','Моя мама готовит ужин.'),('The dog is sleeping.','Собака сейчас спит.'),('We walk to school.','Мы идём в школу пешком.'),('The children sing songs.','Дети поют песни.'),('My father drives a car.','Мой папа водит машину.'),('I draw a green tree.','Я рисую зелёное дерево.')]
add('action-phrases','phrases','Говорим о действиях','Кто делает, что делает и с чем.',[
 'Сначала называем того, кто действует, затем действие: She reads a book.',
 'Если действие происходит сейчас, добавляем am/is/are и форму на -ing. С can используем глагол без окончаний.'],actions[:3],[build(en,ru) for en,ru in actions],('present-simple','present-continuous','can'))
questions=[('Are you happy?','Ты рада?'),('Is he a doctor?','Он врач?'),('Is the cat small?','Кошка маленькая?'),('Are they at home?','Они дома?'),('Can you swim?','Ты умеешь плавать?'),('Can she sing?','Она умеет петь?'),('Can he ride a bike?','Он умеет кататься на велосипеде?'),('Do you like apples?','Тебе нравятся яблоки?'),('Does she play tennis?','Она играет в теннис?'),('Do they read books?','Они читают книги?'),('Does he have a dog?','У него есть собака?'),('Do you go to school?','Ты ходишь в школу?')]
add('questions','phrases','Задаём вопросы','Is/are, can, do и does в начале вопроса.',[
 'С am/is/are и can переносим это слово в начало: You can swim → Can you swim?',
 'Для обычного действия используем Do с I/you/we/they, Does с he/she/it. После does глагол без -s: Does she play tennis?'],questions[:2]+questions[8:9],[build(en,ru) for en,ru in questions],('be','can','present-simple'))
answers=[('Are you happy?','Yes, I am.',['Yes, I is.','Yes, I are.'],'Да, я рада.'),('Are you at home?','No, I am not.',['No, I is not.','No, I are not.'],'Нет, я не дома.'),('Is she a doctor?','Yes, she is.',['Yes, she are.','Yes, she am.'],'Да, она врач.'),('Is he sad?','No, he is not.',['No, he am not.','No, he are not.'],'Нет, он не грустит.'),('Are they friends?','Yes, they are.',['Yes, they is.','Yes, they am.'],'Да, они друзья.'),('Are the cats big?','No, they are not.',['No, they is not.','No, they am not.'],'Нет, они не большие.'),('Can you swim?','Yes, I can.',['Yes, I am.','Yes, I do.'],'Да, я умею плавать.'),('Can she sing?','No, she cannot.',['No, she is not.','No, she does not.'],'Нет, она не умеет петь.'),('Do you like milk?','Yes, I do.',['Yes, I am.','Yes, I can.'],'Да, мне нравится молоко.'),('Does he play tennis?','No, he does not.',['No, he do not.','No, he is not.'],'Нет, он не играет в теннис.'),('Do they read books?','Yes, they do.',['Yes, they does.','Yes, they are.'],'Да, они читают книги.'),('Does she have a cat?','Yes, she does.',['Yes, she do.','Yes, she is.'],'Да, у неё есть кошка.')]
tasks=[choice('Ответь на вопрос по смыслу русского ответа.',question,[correct,*wrong],0,ru,explanation='В коротком ответе повторяем вспомогательное слово вопроса: is/are, can или do/does. Для вопроса к you отвечаем от себя: I.') for question,correct,wrong,ru in answers]
add('short-answers','phrases','Коротко отвечаем','Yes и No вместе с нужным словом.',[
 'Can you swim? — Yes, I can. Is she happy? — Yes, she is. Do you like milk? — Yes, I do.',
 'Отрицательный ответ: No, I cannot. No, she is not. No, I do not. Полные формы здесь помогают увидеть правило.'],[(q,a) for q,a,w,r in answers[:1]+answers[6:7]+answers[8:9]],tasks,('questions',))
negatives=[('I am not sad.','Я не грущу.'),('The cat is not big.','Кошка не большая.'),('They are not at home.','Они не дома.'),('We are not tired.','Мы не устали.'),('I cannot swim.','Я не умею плавать.'),('She cannot sing.','Она не умеет петь.'),('He cannot ride a bike.','Он не умеет кататься на велосипеде.'),('I do not like milk.','Мне не нравится молоко.'),('She does not play football.','Она не играет в футбол.'),('He does not have a dog.','У него нет собаки.'),('We do not eat meat.','Мы не едим мясо.'),('They do not go to school today.','Они сегодня не идут в школу.')]
add('negatives','phrases','Говорим «не»','Строим отрицательные предложения.',[
 'После am/is/are ставим not. Для can используем cannot, короткая форма — can’t.',
 'В обычных действиях: do not или does not + глагол без -s. I don’t like milk. She doesn’t play football. В заданиях даны полные формы.'],negatives[:1]+negatives[4:5]+negatives[8:9],[build(en,ru) for en,ru in negatives],('be','can','present-simple'))
about=[('My name is Anna.','Меня зовут Анна.'),('I am eight years old.','Мне восемь лет.'),('I am a pupil.','Я ученица.'),('I have a brother.','У меня есть брат.'),('I have a small dog.','У меня есть маленькая собака.'),('I like apples.','Мне нравятся яблоки.'),('I can swim.','Я умею плавать.'),('I play tennis.','Я играю в теннис.'),('My favourite colour is blue.','Мой любимый цвет синий.'),('I live in a big house.','Я живу в большом доме.'),('I go to school every day.','Я хожу в школу каждый день.'),('My mother is a teacher.','Моя мама учительница.')]
add('about-me','phrases','Рассказываем о себе','Соединяем знакомые конструкции в маленький рассказ.',[
 'Начни с имени и возраста, затем расскажи о семье, любимых вещах и своих умениях.',
 'В упражнениях собираем рассказ девочки Анны. После тренировки попробуй заменить сведения своими и рассказать вслух взрослому.'],about[:3],[build(en,ru) for en,ru in about],('name-object','action-phrases','have'))

# COMPREHENSION: distinct evidence, instructions, complete dialogues and stories.
extra=json.loads((base/'extra-lessons.json').read_text(encoding='utf-8'))['topics']
tasks=[]
for tid in ['backpack','animals','qualities','sport']:
 for q in extra[tid]['understanding'][:3]:
  tasks.append(choice('Прочитай всю фразу и выбери картинку.',q['text'],[{'scene':c} for c in q['choices']],q['correct'],q['ru'],speech=q['text'],explanation='Сравни количество, размер, цвет и расположение на картинках.'))
add('understand-sentence','understanding','Понимаем предложение','Учитываем все слова, а не только название предмета.',[
 'Важны не только названия: two — два, small — маленький, green — зелёный, on — на.',
 'Сначала прочитай всю фразу, затем проверь все её признаки на картинке.'],[('There are two green balls.','Здесь два зелёных мяча.'),('The pencil is on the table.','Карандаш на столе.')],tasks,('read-words','be'))
tasks=[]
for w,ru in [('nose','нос'),('ear','ухо'),('hand','кисть руки'),('eye','глаз'),('head','голова'),('foot','ступня')]:
 opts=[w,*[a for a in ['nose','ear','hand','eye','head','foot'] if a!=w][:2]]
 tasks.append(choice('Послушай инструкцию и выбери нужную часть тела.','',[{'scene':{'word':a}} for a in opts],0,speech=f'Touch your {w}.',audioOnly=True,ru=f'Коснись: {ru}.',explanation=f'Touch your {w}: покажи эту часть тела.'))
for color in ['red','blue','green']:
 for n in [1,2]:
  scenes=[{'word':'ball','paint':'ball','color':color,'count':n},{'word':'ball','paint':'ball','color':color,'count':3},{'word':'ball','paint':'ball','color':'yellow','count':n}]
  tasks.append(choice('Послушай и выбери картинку по инструкции.','',[{'scene':c} for c in scenes],0,speech=f'Find {"one" if n==1 else "two"} {color} {"ball" if n==1 else "balls"}.',audioOnly=True,explanation='Find — найди. Обрати внимание на цвет и количество.'))
add('instructions','understanding','Выполняем инструкции','Слушаем просьбу и выбираем нужный предмет.',[
 'Touch — коснись; find — найди; show — покажи. Сначала пойми действие, затем предмет и его признаки.',
 'В тренировке можно открыть текст-подсказку; в самостоятельной проверке слушай без неё.'],[('Touch your nose.','Коснись носа.'),('Find two red balls.','Найди два красных мяча.')],tasks,('read-words','understand-sentence'))
dialogs=[
 ('What is your name? My name is Anna.','Как зовут девочку?','Anna',['Kate','Emma']),
 ('How old are you? I am eight.','Сколько лет ребёнку?','eight',['seven','nine']),
 ('Do you have a pet? Yes, I have a cat.','Какое животное есть у ребёнка?','a cat',['a dog','a rabbit']),
 ('Can you swim? No, but I can run.','Что умеет ребёнок?','run',['swim','fly']),
 ('What colour is your bag? It is blue.','Какого цвета рюкзак?','blue',['green','red']),
 ('Where is the book? It is under the table.','Где книга?','under the table',['on the table','beside the table']),
 ('Do you like milk? No, I like water.','Что нравится ребёнку?','water',['milk','juice']),
 ('What does your mother do? She is a doctor.','Кем работает мама?','a doctor',['a teacher','a farmer']),
 ('How many pens do you have? I have three.','Сколько ручек?','three',['two','five']),
 ('What time is it? It is five o\'clock.','Который час?','five o\'clock',['four o\'clock','six o\'clock']),
 ('Do you play tennis? Yes, every day.','Как часто ребёнок играет в теннис?','every day',['on Sunday only','never']),
 ('Where are your shoes? They are in my room.','Где туфли?','in the room',['in the garden','at school'])]
tasks=[choice(prompt,'',[answer,*wrong],0,speech=text,audioOnly=i%2==0,stimulusType='dialogue',explanation='Найди ответ в реплике собеседника.') for i,(text,prompt,answer,wrong) in enumerate(dialogs)]
for i,q in enumerate(tasks):q['stimulus']=dialogs[i][0] if not q['audioOnly'] else ''
add('dialogues','understanding','Короткие диалоги','Находим ответ в разговоре двух людей.',[
 'Вопрос подсказывает, что слушать: имя, возраст, место, цвет, количество или время.',
 'Часть диалогов читаем, часть слушаем. Не нужно переводить каждое слово: найди нужную информацию.'],[('What colour is your bag? — It is blue.','Какого цвета рюкзак? — Синий.')],tasks,('questions','short-answers'))
stories=[
 ('Anna has a small dog. The dog is brown. It likes to run in the garden.','Какого цвета собака?','brown',['black','white']),
 ('Ben is seven. He has a sister. His sister is nine. They go to school together.','Сколько лет сестре?','nine',['seven','eight']),
 ('There are three apples on the table. Two bananas are in the bag. Anna eats one banana.','Сколько яблок на столе?','three',['two','one']),
 ('Kate likes reading. She has a new book. The book is on her bed.','Где книга?','on the bed',['under the table','in the bag']),
 ('Tom can swim. His brother cannot swim. They both can ride a bike.','Что умеют оба брата?','ride a bike',['swim','fly']),
 ('It is Sunday. The children are in the park. They are playing football.','Во что играют дети?','football',['tennis','chess']),
 ('My mother is a doctor. My father is a teacher. They work every day.','Кем работает папа?','a teacher',['a doctor','a farmer']),
 ('The cat is sleeping under the chair. The dog is running in the garden.','Кто спит?','the cat',['the dog','the bird']),
 ('Emma has a red shirt and blue shoes. Her hat is yellow.','Какого цвета шляпа?','yellow',['red','blue']),
 ('It is eight o\'clock. Anna has breakfast. She goes to school at nine.','Во сколько Анна идёт в школу?','nine o\'clock',['eight o\'clock','ten o\'clock']),
 ('Leo likes milk. His sister likes water. Their mother drinks tea.','Что нравится сестре?','water',['milk','tea']),
 ('There are two birds in the tree. One bird is small. The other bird is big.','Сколько птиц на дереве?','two',['one','three'])]
tasks=[choice(prompt,text if i%2==0 else '',[answer,*wrong],0,speech=text,audioOnly=i%2==1,stimulusType='story',explanation='Ответ находится в истории. Перечитай или послушай её ещё раз.') for i,(text,prompt,answer,wrong) in enumerate(stories)]
add('stories','understanding','Маленькие истории','Понимаем короткий текст и отвечаем по его содержанию.',[
 'В истории несколько предложений. Вопрос помогает выбрать нужное: кто, где, сколько, какой или когда.',
 'Для тренировки чередуем чтение и слушание. После задания попробуй пересказать историю взрослому.'],[(stories[0][0],'У Анны маленькая коричневая собака. Она любит бегать в саду.')],tasks,('understand-sentence','dialogues'))

# NUMBERS AND TIME.
for mid,title,values,lo,hi,pre in [
 ('numbers-10','Числа от 0 до 10',list(range(11))+[7],0,10,()),
 ('numbers-20','Числа от 11 до 20',list(range(11,21))+[13,18],11,20,('numbers-10',)),
 ('numbers-100','Числа от 21 до 100',[21,22,25,30,34,40,46,50,60,70,90,100],21,100,('numbers-20',))]:
 tasks=[]
 for i,n in enumerate(values):
  opts=num_options(n,lo,hi)
  if i%2:tasks.append(choice('Послушай число и выбери цифры.','',[dict(text=str(x),lang='en') for x in opts],0,speech=numbered(n),audioOnly=True,explanation=f'{n} — {numbered(n)}.'))
  else:tasks.append(choice('Как это число называется по-английски?',str(n),[numbered(x) for x in opts],0,explanation=f'{n} — {numbered(n)}.'))
 rules=['Слушай число и сравнивай его название с цифрами.']
 if mid=='numbers-20':rules+=['Обрати внимание: eleven, twelve, thirteen, fifteen, eighteen. Их написание нужно запомнить.']
 if mid=='numbers-100':rules+=['Десятки: twenty, thirty, forty, fifty, sixty, seventy, eighty, ninety. Составное число: twenty-one. 100 — one hundred.']
 add(mid,'numbers',title,'Читаем и узнаём на слух названия чисел.',rules,[(numbered(n),str(n)) for n in values[:4]],tasks,pre)
tasks=[]
for i in range(12):
 n=i+1;word=['apple','book','cat','star'][i%4];opts=num_options(n,1,15)
 tasks.append(choice('Посчитай предметы и выбери число.','',[numbered(x) for x in opts],0,figure={'type':'scene','scene':{'word':word,'count':n}},explanation=f'Здесь {n} предметов: {numbered(n)}.'))
add('quantities','numbers','Считаем предметы','Соединяем количество с английским числительным.',[
 'Считай предметы по одному, не пропуская и не повторяя. Затем выбери английское название получившегося числа.'],[('three apples','три яблока'),('five books','пять книг')],tasks,('numbers-10','numbers-20'))
tasks=[]
for i,(a,b,op) in enumerate([(2,3,'+'),(7,2,'−'),(4,4,'+'),(9,3,'−'),(5,6,'+'),(12,4,'−'),(8,5,'+'),(15,5,'−'),(6,7,'+'),(14,8,'−'),(9,9,'+'),(20,1,'−')]):
 result=a+b if op=='+' else a-b;opts=num_options(result,0,20)
 tasks.append(choice('Реши пример и назови ответ по-английски.',f'{a} {op} {b} = ?',[numbered(n) for n in opts],0,explanation=f'{a} {op} {b} = {result}: {numbered(result)}.'))
add('arithmetic','numbers','Простые вычисления','Складываем и вычитаем, называем ответ по-английски.',[
 'plus — плюс; minus — минус; equals — равно. Two plus three equals five.',
 'В этом блоке нужно и решить пример, и выбрать английское название ответа.'],[('Two plus three equals five.','Два плюс три равно пяти.'),('Seven minus two equals five.','Семь минус два равно пяти.')],tasks,('numbers-20',))
def time_words(h,m):
 if m==0:return numbered(h)+" o'clock"
 if m==30:return 'half past '+numbered(h)
 if m==15:return 'quarter past '+numbered(h)
 return 'quarter to '+numbered(h%12+1)
for mid,title,mins,rule,pre in [
 ('clock-hours','Часы: целый час',[0],'Когда минутная стрелка на 12: three o’clock — три часа.',('numbers-10','numbers-20')),
 ('clock-half','Часы: половина часа',[30],'Half past three — три часа тридцать минут: половина часа после трёх.',('clock-hours',)),
 ('clock-quarter','Часы: четверть часа',[15,45],'Quarter past three — 3:15. Quarter to four — 3:45: до четырёх остаётся четверть часа.',('clock-half',))]:
 tasks=[]
 for i in range(12):
  h=i+1;m=mins[(i//2)%len(mins)];answer=time_words(h,m)
  if i%2:
   tasks.append(dict(kind='clock-set',prompt='Поставь указанное время на часах.',stimulus='It is '+answer+'.',speech='It is '+answer+'.',hour=h,minute=m,allowedMinutes=mins,explanation=f'{answer} — {h}:{m:02d}.'))
  else:
   others=[time_words(h%12+1,m),time_words((h+2)%12+1,m)]
   tasks.append(choice('Который час? Выбери английскую фразу.','',[answer,*others],0,figure={'type':'clock','hour':h,'minute':m},explanation=f'{answer} — {h}:{m:02d}.'))
 add(mid,'numbers',title,'Читаем циферблат и сами устанавливаем время.',[
  'Короткая стрелка показывает часы, длинная — минуты. За час короткая стрелка постепенно движется к следующему числу.',rule],[(time_words(3,mins[0]),f'3:{mins[0]:02d}'),(time_words(12,mins[-1]),f'12:{mins[-1]:02d}')],tasks,pre)
days=[('Monday','понедельник'),('Tuesday','вторник'),('Wednesday','среда'),('Thursday','четверг'),('Friday','пятница'),('Saturday','суббота'),('Sunday','воскресенье')]
tasks=[]
for i,(en,ru) in enumerate(days):tasks.append(choice('Выбери день недели.',ru,[en,days[(i+2)%7][0],days[(i+4)%7][0]],0,explanation=f'{ru} — {en}.'))
for i in range(5):
 day,nextday=days[i][0],days[(i+1)%7][0]
 tasks.append(choice('Какой день идёт следующим?',f'Today is {day}. Tomorrow is ___ .',[nextday,day,days[(i+3)%7][0]],0,explanation='Порядок: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday.'))
add('weekdays','numbers','Дни недели','Названия дней и их порядок.',[
 'Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday. Названия дней пишутся с большой буквы.',
 'today — сегодня; tomorrow — завтра. В английском перед днём недели обычно on: on Monday.'],[('on Monday','в понедельник'),('Today is Friday.','Сегодня пятница.')],tasks)
schedule=[('Breakfast',8),('School',9),('Lunch',12),('Reading',2),('Tennis',4),('Dinner',6)]
tasks=[]
for i in range(12):
 activity,h=schedule[i%6]
 if i<6:
  tasks.append(choice('Посмотри расписание. Во сколько это занятие?',activity,[time_words(h,0),time_words(h%12+1,0),time_words((h+2)%12+1,0)],0,figure={'type':'schedule','rows':[{'label':a,'time':f'{b}:00'} for a,b in schedule]},explanation=f'{activity}: {h}:00 — {time_words(h,0)}.'))
 else:
  day=days[(i-6)%7][0];sentence=f'I play tennis on {day} at {numbered(h)}.'
  tasks.append(choice('Послушай. В какой день играют в теннис?','',[day,days[(i-4)%7][0],days[(i-2)%7][0]],0,speech=sentence,audioOnly=True,explanation=f'on {day} — в этот день недели.'))
add('schedule','numbers','Понимаем расписание','Соединяем занятие, день недели и время.',[
 'Для дня недели: on Monday. Для времени: at eight o’clock.',
 'В расписании сначала найди занятие, затем прочитай время. В заданиях на слух ищи день недели после on.'],[('I play tennis on Monday at four.','Я играю в теннис в понедельник в четыре.')],tasks,('clock-hours','weekdays','read-words'))

# Common alternative word orders are accepted in sentence building.
alternatives={
 'describe-object-10':['The bird is blue and small.'],
 'action-phrases-04':['He is now running.','Now he is running.'],
 'negatives-12':['Today they do not go to school.','They do not today go to school.'],
 'about-me-01':['Anna is my name.'],
 'about-me-09':['Blue is my favourite colour.'],
 'about-me-11':['Every day I go to school.','I go every day to school.']}
for m in modules:
 for q in m['tasks']:
  if q['kind']=='build':
   q['acceptedAnswers']=[q['answer'],*[re.sub(r'[.,!?]','',s).split() for s in alternatives.get(q['id'],[])]]
   assert all(sorted(w.lower() for w in answer)==sorted(w.lower() for w in q['tokens']) for answer in q['acceptedAnswers']),q['id']

# Validation catches authoring mistakes before a catalog reaches the browser.
ids=set();mids={m['id'] for m in modules}
for m in modules:
 assert len(m['tasks'])>=12,m['id'];assert all(p in mids for p in m['prerequisites'])
 for q in m['tasks']:
  assert q['id'] not in ids;ids.add(q['id'])
  if not q['explanation']:q['explanation']=m['rules'][0]
  if q['kind']=='choice':
   assert 0<=q['correct']<len(q['choices']);assert len({json.dumps(c,sort_keys=True) for c in q['choices']})==len(q['choices']),q['id']
  if q['kind']=='build':assert sorted(q['answer'])==sorted(q['tokens']) and all(not re.search(r'[.,!?]',w) for w in q['tokens'])
catalog=dict(version=1,sections=sections,modules=modules)
from learning_expansion import extend
catalog=extend(catalog,vocab,choice,gap,build,numbered,time_words)
(base/'curriculum.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{len(modules)} modules, {sum(len(m["tasks"]) for m in modules)} practice tasks, {sum(len(m["assessmentTasks"]) for m in modules)} assessment tasks, {len(sections)} sections.')
