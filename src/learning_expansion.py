"""Curated assessment material, independent answers, stories and pen practice."""


def extend(catalog, vocab, choice, gap, build, number, time_words):
    modules = catalog['modules']
    lookup = {m['id']: m for m in modules}
    words = {w['en']: w for w in vocab}
    banks = {}
    def bank(mid, rows):
        banks[mid] = rows
    def pick(prompt, text, answer, wrong, **extra):
        return choice(prompt, text, [answer, *wrong], 0, **extra)
    def typed(prompt, text, answers, **extra):
        if isinstance(answers, str): answers = [answers]
        return dict(kind='input', prompt=prompt, stimulus=text, acceptedText=answers,
                    explanation='Ответ: '+answers[0]+'.', **extra)
    def module(mid, section, title, description, rules, examples, tasks, **extra):
        m = dict(id=mid, section=section, title=title, description=description, rules=rules,
                 examples=[dict(en=en, ru=ru) for en, ru in examples], tasks=tasks,
                 prerequisites=[], **extra)
        modules.append(m); lookup[mid] = m
        return m
    def noun_article(word):
        return 'an' if word[0] in 'aeiou' else 'a'

    # These prompts are kept out of all lesson/practice banks.
    sound_words = [('boat','b'),('desk','d'),('kite','k'),('pencil','p'),('sock','s'),('milk','m'),('goat','g'),('fox','f'),('hat','h'),('leg','l'),('nose','n'),('table','t')]
    bank('letters', [pick('Найди слово с указанным первым звуком.', '/'+sound+'/', w,
        [sound_words[(i+3)%12][0],sound_words[(i+7)%12][0]], speech=w,
        explanation=f'{w} начинается со звука /{sound}/.') for i,(w,sound) in enumerate(sound_words)])
    short = [('cap','/æ/'),('map','/æ/'),('jam','/æ/'),('hen','/e/'),('leg','/e/'),('ten','/e/'),('sit','/ɪ/'),('six','/ɪ/'),('hill','/ɪ/'),('hot','/ɒ/'),('bus','/ʌ/'),('nut','/ʌ/')]
    bank('short-vowels', [pick('Какой гласный звук слышен?', '', sound,
        [s for s in ['/æ/','/e/','/ɪ/','/ɒ/','/ʌ/'] if s!=sound][:2], speech=w, audioOnly=True,
        explanation=f'{w}: гласный {sound}.') for w,sound in short])
    groups = [('brush','sh'),('wish','sh'),('dish','sh'),('shop','sh'),('beach','ch'),('peach','ch'),('lunch','ch'),('watch','ch'),('bath','th'),('path','th'),('thumb','th'),('thank','th')]
    bank('letter-groups', [pick('Какое сочетание букв в услышанном слове?', '', group,
        [s for s in ['sh','ch','th'] if s!=group], speech=w,audioOnly=True,
        explanation=f'{w}: сочетание {group}.') for w,group in groups])
    long = [('deep',True),('street',True),('keep',True),('week',True),('sleep',True),('sweet',True),('team',True),('dream',True),('clean',True),('peach',True),('bread',False),('heavy',False)]
    bank('long-vowels', [choice('Прочитай слово. Какой в нём гласный звук?', w,
        ['Долгий /iː/','Короткий /e/','Короткий /ʌ/'],0 if long_sound else 1,
        explanation=f'{w}: '+('/iː/.' if long_sound else '/e/: исключение.')) for w,long_sound in long])
    read = ['pencil','ruler','rabbit','bird','fish','horse','table','bed','hat','sun','rain','nurse']
    bank('read-words', [pick('Прочитай слово и выбери картинку.',w,{'scene':{'word':w}},
        [{'scene':{'word':read[(i+3)%12]}},{'scene':{'word':read[(i+7)%12]}}],
        explanation=w+' — '+words[w]['ru']+'.') for i,w in enumerate(read)])
    pairs = [('cap','cup'),('sit','seat'),('hill','heel'),('met','mat'),('cot','coat'),('full','fool')]
    bank('similar-sounds', [pick('Какое из двух слов прозвучало?', '', w,[b if w==a else a],
        speech=w,audioOnly=True,explanation=f'Сравни {a} и {b}.') for a,b in pairs for w in (a,b)])
    nouns = [('pencil','карандаш'),('ruler','линейка'),('rabbit','кролик'),('bird','птица'),('table','стол'),('nurse','медсестра'),('eye','глаз'),('ear','ухо'),('umbrella','зонт'),('owl','сова'),('ant','муравей'),('actor','актёр')]
    bank('articles-a-an',[gap('I have ___ '+w+'.','У меня есть предмет: '+ru+'.',noun_article(w),
        ['an' if noun_article(w)=='a' else 'a','—'],'Артикль выбираем по первому звуку существительного.') for w,ru in nouns])
    bank('articles-the',[gap(f'Here is {noun_article(w)} {w}. ___ {w} is small.','Говорим о том же предмете второй раз.',
        'The',['A','An'],'Уже названный предмет: the.') for w,ru in nouns])
    zero = ['birds','horses','rabbits','flowers','books','eggs','oranges','carrots','juice','tea','cheese','fish']
    rows=[gap('I like ___ '+w+' very much.','Говорим вообще, без указания на конкретные предметы.','—',['a','an'],
              'Перед множественным числом и неисчисляемым названием в таком высказывании артикля нет.') for w in zero]
    for q in rows:q['complete']=q['complete'].replace(' — ',' ')
    bank('articles-zero',rows)
    plural = [('rabbit','rabbits'),('bird','birds'),('ruler','rulers'),('egg','eggs'),('orange','oranges'),('pencil','pencils'),('dish','dishes'),('watch','watches'),('city','cities'),('man','men'),('woman','women'),('person','people')]
    bank('plurals',[pick('Выбери форму для нескольких.',f'one {a} → three ___',b,[a,a+'ing'],explanation=f'{a} → {b}.') for a,b in plural])
    pronouns = [('Ben','he'),('Kate','she'),('Ben and Kate','they'),('My sister and I','we'),('The pencils','they'),('The table','it'),('The bird','it'),('My grandmother','she'),('My grandfather','he'),('My friends','they'),('The girls','they'),('My brother and I','we')]
    bank('pronouns',[pick('Замени выделенную группу местоимением.',text,answer,
        [s for s in ['he','she','it','we','they'] if s!=answer][:2],explanation=f'{text} → {answer}.') for text,answer in pronouns])
    subjects = [('I','am','have'),('You','are','have'),('He','is','has'),('She','is','has'),('We','are','have'),('They','are','have'),('The rabbit','is','has'),('The birds','are','have'),('My father','is','has'),('My friends','are','have'),('Kate','is','has'),('Ben and Kate','are','have')]
    endings = ['at school','at home','happy','kind','ready','tired']
    bank('be',[gap(f'{s} ___ {endings[(i+2)%6]} today.','Выбери форму по подлежащему.',be,[v for v in ['am','is','are'] if v!=be],
        'I am; he/she/it is; you/we/they are.') for i,(s,be,hv) in enumerate(subjects)])
    bank('have',[gap(f'{s} ___ {noun_article(nouns[i][0])} {nouns[i][0]}.','Кто-то имеет этот предмет.',hv,
        ['has' if hv=='have' else 'have','is'],'I/you/we/they have; he/she/it has.') for i,(s,be,hv) in enumerate(subjects)])
    verbs = [('draw','рисовать'),('sing','петь'),('dance','танцевать'),('read','читать'),('write','писать'),('jump','прыгать')]
    bank('can',[gap(f'{s} can ___ well.','Выбери неизменённый глагол.',verbs[i%6][0],
        [verbs[i%6][0]+'s',verbs[i%6][0]+'ing'],'После can глагол без -s и -ing.') for i,(s,be,hv) in enumerate(subjects)])
    simple = [('I','draw','a cat'),('She','draws','a flower'),('He','sings','songs'),('We','sing','at school'),('They','play','basketball'),('My father','reads','at home'),('You','drink','juice'),('My sister','likes','birds'),('The nurse','works','at night'),('We','help','our friends'),('Kate','eats','an apple'),('Ben and Kate','walk','in the park')]
    bank('present-simple',[gap(f'{s} ___ {end}.','Речь об обычном действии.',v,
        [v[:-1] if v.endswith('s') else v+'s',(v[:-1] if v.endswith('s') else v)+'ing'],
        'С he/she/it в этих глаголах добавляем -s; с I/you/we/they — нет.') for s,v,end in simple])
    ing = ['drawing','singing','playing','jumping','reading','writing']
    bank('present-continuous',[gap(f'{s} ___ {ing[(i+3)%6]} at the moment.','Действие происходит сейчас.',be,
        [v for v in ['am','is','are'] if v!=be],'Действие сейчас: am/is/are + глагол на -ing.') for i,(s,be,hv) in enumerate(subjects)])
    bank('there-is-are',[gap('There ___ '+(noun_article(w)+' '+w if i%2==0 else 'three '+w+'s')+' in the room.',
        'Посмотри на количество предметов.','is' if i%2==0 else 'are',['are' if i%2==0 else 'is','am'],
        'There is — один, there are — несколько.') for i,(w,ru) in enumerate(nouns)])
    bank('prepositions',[pick('Выбери предлог по картинке.',f'The {w} is ___ the table.',pos,[s for s in ['on','under','beside'] if s!=pos],
        figure={'type':'scene','scene':{'word':w,'position':pos}},explanation={'on':'on — на.','under':'under — под.','beside':'beside — рядом.'}[pos])
        for w in ['hat','apple','ball','ruler'] for pos in ['on','under','beside']])
    bank('name-object',[build(f'Here is {noun_article(w)} {w}.','Вот предмет: '+ru+'.') for w,ru in nouns])
    descriptions=[('The horse is brown.','Лошадь коричневая.'),('The bird is yellow.','Птица жёлтая.'),('It is a green pencil.','Это зелёный карандаш.'),('It is a pink flower.','Это розовый цветок.'),('The ruler is long.','Линейка длинная.'),('The bag is old.','Рюкзак старый.'),('The shoes are new.','Туфли новые.'),('The stars are yellow.','Звёзды жёлтые.'),('The cat has a long tail.','У кошки длинный хвост.'),('The rabbit is big and white.','Кролик большой и белый.'),('This is a small house.','Это маленький дом.'),('The dog has brown eyes.','У собаки карие глаза.')]
    bank('describe-object',[build(en,ru) for en,ru in descriptions])
    actions=[('I read at home.','Я читаю дома.'),('She drinks juice.','Она пьёт сок.'),('We play basketball.','Мы играем в баскетбол.'),('He is drawing now.','Он сейчас рисует.'),('They are singing songs.','Они сейчас поют песни.'),('I can dance.','Я умею танцевать.'),('My father cooks breakfast.','Мой папа готовит завтрак.'),('The cat is playing.','Кошка сейчас играет.'),('We run in the park.','Мы бегаем в парке.'),('The children read books.','Дети читают книги.'),('My mother rides a bike.','Моя мама катается на велосипеде.'),('I draw a red flower.','Я рисую красный цветок.')]
    bank('action-phrases',[build(en,ru) for en,ru in actions])
    questions=[('Are you tired?','Ты устала?'),('Is he a teacher?','Он учитель?'),('Is the bird yellow?','Птица жёлтая?'),('Are they at school?','Они в школе?'),('Can you dance?','Ты умеешь танцевать?'),('Can she draw?','Она умеет рисовать?'),('Can he jump?','Он умеет прыгать?'),('Do you like oranges?','Тебе нравятся апельсины?'),('Does she read books?','Она читает книги?'),('Do they play basketball?','Они играют в баскетбол?'),('Does he have a rabbit?','У него есть кролик?'),('Do you walk to school?','Ты идёшь в школу пешком?')]
    bank('questions',[build(en,ru) for en,ru in questions])
    bank('short-answers',[pick('Ответь по указанному смыслу.',q,answer,
        ['Yes, I is.','No, they am not.'],ru=ru,complete=answer,explanation='Повторяем вспомогательное слово вопроса.')
        for q,answer,ru in [('Are you tired?','Yes, I am.','Да, я устала.'),('Are you at school?','No, I am not.','Нет, я не в школе.'),('Is she a nurse?','Yes, she is.','Да, она медсестра.'),('Is he happy?','No, he is not.','Нет, он не рад.'),('Are they ready?','Yes, they are.','Да, они готовы.'),('Are the birds green?','No, they are not.','Нет, они не зелёные.'),('Can you dance?','Yes, I can.','Да, я умею танцевать.'),('Can she draw?','No, she cannot.','Нет, она не умеет рисовать.'),('Do you like juice?','Yes, I do.','Да, мне нравится сок.'),('Does he read books?','No, he does not.','Нет, он не читает книги.'),('Do they play basketball?','Yes, they do.','Да, они играют в баскетбол.'),('Does she have a bird?','Yes, she does.','Да, у неё есть птица.')]])
    negatives=[('I am not tired.','Я не устала.'),('The bird is not yellow.','Птица не жёлтая.'),('They are not at school.','Они не в школе.'),('We are not sad.','Мы не грустим.'),('I cannot dance.','Я не умею танцевать.'),('She cannot draw.','Она не умеет рисовать.'),('He cannot jump.','Он не умеет прыгать.'),('I do not like juice.','Мне не нравится сок.'),('She does not read books.','Она не читает книги.'),('He does not have a rabbit.','У него нет кролика.'),('We do not eat eggs.','Мы не едим яйца.'),('They do not play tennis today.','Они сегодня не играют в теннис.')]
    bank('negatives',[build(en,ru) for en,ru in negatives])
    about=[('My name is Kate.','Меня зовут Кейт.'),('I am nine years old.','Мне девять лет.'),('I am a good friend.','Я хорошая подруга.'),('I have a sister.','У меня есть сестра.'),('I have a white rabbit.','У меня есть белый кролик.'),('I like oranges.','Мне нравятся апельсины.'),('I can dance.','Я умею танцевать.'),('I play basketball.','Я играю в баскетбол.'),('My favourite colour is green.','Мой любимый цвет зелёный.'),('I live in a small house.','Я живу в маленьком доме.'),('I read books every day.','Я читаю книги каждый день.'),('My father is a doctor.','Мой папа врач.')]
    bank('about-me',[build(en,ru) for en,ru in about])
    understood=[]; instructions=[]
    for i in range(12):
        w=['star','ball'][i%2];n=3+i%3;color=['pink','green','red'][i%3]
        c={'word':w,'count':n,'color':color}
        c['paint']=w
        others=[{**c,'count':n+1},{**c,'color':'blue'}]
        sentence=f'Find {number(n)} {color} {w}s.'
        understood.append(pick('Прочитай фразу и выбери картинку.',f'There are {number(n)} {color} {w}s.',{'scene':c},[{'scene':a} for a in others],explanation='Проверь количество и цвет.'))
        instructions.append(pick('Выполни услышанную инструкцию.','',{'scene':c},[{'scene':a} for a in others],speech=sentence,audioOnly=True,explanation=sentence))
    bank('understand-sentence',understood);bank('instructions',instructions)
    dialogues=[('What is your name? My name is Ben.','Как зовут ребёнка?','Ben',['Tom','Anna']),('How old are you? I am nine.','Сколько лет ребёнку?','nine',['eight','ten']),('Do you have a pet? Yes, I have a bird.','Какое животное есть у ребёнка?','a bird',['a dog','a cat']),('Can you sing? No, but I can dance.','Что умеет ребёнок?','dance',['sing','swim']),('What colour is your pencil? It is green.','Какого цвета карандаш?','green',['blue','red']),('Where is the hat? It is on the table.','Где шляпа?','on the table',['under the table','beside the table']),('Do you like tea? No, I like juice.','Что нравится ребёнку?','juice',['tea','milk']),('What does your father do? He is a teacher.','Кем работает папа?','a teacher',['a doctor','a farmer']),('How many books do you have? I have four.','Сколько книг?','four',['three','six']),('What time is it? It is seven o’clock.','Который час?','seven o’clock',['five o’clock','eight o’clock']),('Do you read every day? No, I read on Saturday.','Когда ребёнок читает?','on Saturday',['every day','on Monday']),('Where are your pens? They are in my bag.','Где ручки?','in the bag',['in the room','at school'])]
    bank('dialogues',[pick(prompt,'' if i%2==0 else text,answer,wrong,speech=text,audioOnly=i%2==0,stimulusType='dialogue',explanation='Найди ответ в разговоре.') for i,(text,prompt,answer,wrong) in enumerate(dialogues)])
    stories=[]
    for i,(name,animal,color,place) in enumerate([('Kate','rabbit','white','room'),('Ben','bird','yellow','garden'),('Tom','cat','black','house'),('Emma','dog','brown','park')]):
        text=f'{name} has a {animal}. It is {color}. It likes to play in the {place}.'
        for j,(prompt,answer,wrong) in enumerate([('Какое животное есть у ребёнка?',animal,[a for a in ['dog','cat','bird','rabbit'] if a!=animal][:2]),('Какого цвета животное?',color,[a for a in ['white','yellow','black','brown'] if a!=color][:2]),('Где животное любит играть?',place,[a for a in ['room','garden','house','park'] if a!=place][:2])]):
            audio=(i+j)%2==1
            stories.append(pick(prompt,'' if audio else text,answer,wrong,speech=text,audioOnly=audio,stimulusType='story',explanation='Ответ указан в истории.'))
    bank('stories',stories)
    for mid,lo,hi in [('numbers-10',0,10),('numbers-20',11,20),('numbers-100',21,100)]:
        rows=[]
        for i,n in enumerate(range(lo,min(lo+16,hi+1))):
            # Context is different even when this finite set of numbers was seen before.
            text=f'I have {number(n)} pencils.' if mid!='numbers-100' else f'There are {number(n)} stars.'
            rows.append(pick('Какое число названо во фразе?', '' if i%2 else text, str(n),
                [str(lo+(n-lo+1)%(hi-lo+1)),str(lo+(n-lo+3)%(hi-lo+1))],speech=text,audioOnly=i%2==1,explanation=f'{number(n)} — {n}.'))
        bank(mid,rows)
    bank('quantities',[pick('Посчитай предметы.', '',number(n),[number(n-1),number(n+1)],
        figure={'type':'scene','scene':{'word':['pencil','banana','bird'][i%3],'count':n}},explanation=f'{n}: {number(n)}.') for i,n in enumerate(range(2,14))])
    bank('arithmetic',[pick('Реши пример и выбери английское число.',f'{a} + {b} = ?',number(a+b),[number(a+b+1),number(a+b-1)],explanation=f'{a+b}: {number(a+b)}.') for a,b in [(1,2),(2,4),(3,4),(4,5),(5,5),(6,5),(7,5),(8,5),(9,5),(10,5),(8,8),(9,10)]])
    for mid,mins in [('clock-hours',[0]),('clock-half',[30]),('clock-quarter',[15,45])]:
        rows=[]
        for i in range(12):
            h=i+1;minute=mins[i%len(mins)];answer=time_words(h,minute)
            if i%2:rows.append(pick('Во сколько начинается занятие?', '',answer,[time_words(h%12+1,minute),time_words((h+2)%12+1,minute)],speech=f'The lesson starts at {answer}.',audioOnly=True,explanation=f'{answer}: {h}:{minute:02d}.'))
            else:rows.append(dict(kind='clock-set',prompt='Поставь на часах время начала занятия.',stimulus=f'The lesson starts at {answer}.',speech=f'The lesson starts at {answer}.',hour=h,minute=minute,explanation=f'{answer}: {h}:{minute:02d}.'))
        bank(mid,rows)
    days=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    bank('weekdays',[pick('Какой день был вчера?',f'Today is {day}. Yesterday was ___ .',days[(i-1)%7],[day,days[(i+1)%7]],explanation='Yesterday — вчера. Идём на один день назад.') for i,day in enumerate(days)]+[pick('В какой день встреча?', '',days[i],[days[(i+1)%7],days[(i+3)%7]],speech=f'We meet on {days[i]}.',audioOnly=True,explanation='Ищи день после on.') for i in range(5)])
    schedule=[('Drawing',10),('Music',11),('Swimming',3),('Football',5),('Reading',7),('Breakfast',9)]
    bank('schedule',[pick('Во сколько занятие по расписанию?',activity,time_words(h,0),[time_words(h%12+1,0),time_words((h+3)%12+1,0)],figure={'type':'schedule','rows':[dict(label=a,time=f'{b}:00') for a,b in schedule]},explanation=f'{activity}: {h}:00.') for activity,h in schedule]+
        [pick('В какой день будет занятие?', '',days[i],[days[(i+2)%7],days[(i+4)%7]],speech=f'We have music on {days[i]} at ten.',audioOnly=True,explanation='День недели стоит после on.') for i in range(6)])

    catalog['sections'] += [dict(id='independent',title='Отвечаем сами',icon='✍️',description='Пишем слово и отвечаем без вариантов.'),dict(id='adventures',title='Приключения капибары',icon='🦫',description='Несколько связанных заданий в одной истории.'),dict(id='pen',title='Занимаемся со стилусом',icon='🖊️',description='Обводим, соединяем, пишем и рисуем.')]
    dictation_words=['cat','dog','sun','pen','bag','bed','hat','red','fish','book','tree','milk']
    dictation_check=['bird','egg','eye','ear','shoe','rain','hand','nose','star','blue','green','ruler']
    module('dictation','independent','Слово под диктовку','Послушай и напиши короткое слово.',[
        'Послушай слово и введи его английскими буквами. Можно использовать клавиатуру планшета.',
        'В тренировке можно открыть подсказку. В проверке текст слова появится только в разборе.'],[('cat','кошка'),('sun','солнце')],
        [typed('Послушай и напиши слово.','',w,speech=w,audioOnly=True,inputLabel='Слово по-английски') for w in dictation_words])
    bank('dictation',[typed('Послушай и напиши слово.','',w,speech=w,audioOnly=True,inputLabel='Слово по-английски') for w in dictation_check])
    gaps=[('I ___ happy.','am'),('She ___ a book.','has'),('We ___ at home.','are'),('He can ___ .','swim'),('This is ___ apple.','an'),('This is ___ cat.','a'),('She ___ tennis.','plays'),('They ___ books.','read'),('The dog ___ small.','is'),('I ___ a bag.','have'),('There ___ two pens.','are'),('She is ___ now.','running')]
    module('write-gap','independent','Допиши слово','Заполняем пропуск без готовых вариантов.',[
        'Прочитай всё предложение. Напиши одно подходящее слово в пропуске.',
        'Если подходит несколько слов, задание даёт русскую подсказку или конкретную форму глагола.'],[('She has a book.','У неё есть книга.')],
        [typed('Впиши пропущенное слово.'+(' Используй глагол swim.' if i==3 else ' Используй глагол run: действие сейчас.' if i==11 else ''),text,answer) for i,(text,answer) in enumerate(gaps)])
    new_gaps=[('I ___ at school.','am'),('He ___ a ruler.','has'),('You ___ ready.','are'),('She can ___ well.','dance'),('Here is ___ orange.','an'),('Here is ___ rabbit.','a'),('He ___ every day.','reads'),('We ___ water.','drink'),('The bird ___ yellow.','is'),('They ___ two books.','have'),('There ___ three eggs.','are'),('He is ___ now.','singing')]
    bank('write-gap',[typed('Впиши слово.'+(' Используй dance.' if i==3 else ' Используй read.' if i==6 else ' Используй drink.' if i==7 else ' Используй sing: действие сейчас.' if i==11 else ''),text,answer) for i,(text,answer) in enumerate(new_gaps)])
    hints=['Я рада.','У неё есть книга.','Мы дома.','Он умеет плавать.','Это яблоко.','Это кошка.','Она играет в теннис.','Они читают книги.','Собака маленькая.','У меня есть рюкзак.','Здесь две ручки.','Она сейчас бежит.']
    check_hints=['Я в школе.','У него есть линейка.','Ты готова.','Она умеет хорошо танцевать.','Вот апельсин.','Вот кролик.','Он читает каждый день.','Мы пьём воду.','Птица жёлтая.','У них есть две книги.','Здесь три яйца.','Он сейчас поёт.']
    for q,hint in zip(lookup['write-gap']['tasks'],hints):q['prompt']+=' '+hint
    for q,hint in zip(banks['write-gap'],check_hints):q['prompt']+=' '+hint
    facts=[('The cat is black. What colour is the cat?',['black','It is black','The cat is black']),('There are three books. How many books are there?',['three','3','There are three books']),('Anna is eight. How old is Anna?',['eight','8','She is eight']),('The bag is on the table. Where is the bag?',['on the table','It is on the table','The bag is on the table']),('Ben can swim. Can Ben swim?',['Yes, he can']),('Kate has a dog. Does Kate have a dog?',['Yes, she does']),('The cats are small. Are the cats big?',['No, they are not',"No, they aren’t"]),('My name is Tom. What is my name?',['Tom','Your name is Tom']),('The ball is green. What colour is the ball?',['green','It is green']),('It is six o’clock. What time is it?',['six o’clock',"six o'clock",'It is six o’clock']),('I have two pens. How many pens do I have?',['two','2','You have two pens']),('Emma likes milk. Does Emma like juice?',['No, she does not',"No, she doesn’t"])]
    facts[-1]=('Emma likes milk. She does not like juice. Does Emma like juice?',facts[-1][1])
    module('write-answer','independent','Ответь капибаре','Прочитай факт и напиши короткий ответ.',[
        'Ответ ищем в первой фразе. Цвет и количество можно назвать одним словом.',
        'На вопрос с Can или Does отвечай короткой фразой: Yes, he can. No, she does not. Можно использовать обычные сокращения.'],[('The dog is brown. What colour is it? — Brown.','Собака коричневая. Ответ: коричневый.')],
        [typed('Напиши ответ по прочитанному.',text,answers,inputLabel='Короткий ответ') for text,answers in facts])
    check_facts=[('The rabbit is white. What colour is it?',['white','It is white']),('There are five pencils. How many pencils are there?',['five','5','There are five pencils']),('Kate is nine. How old is Kate?',['nine','9','She is nine']),('The hat is under the table. Where is the hat?',['under the table','It is under the table']),('Tom can dance. Can Tom dance?',['Yes, he can']),('Emma has a bird. Does Emma have a bird?',['Yes, she does']),('The birds are yellow. Are the birds red?',['No, they are not',"No, they aren’t"]),('My name is Ben. What is my name?',['Ben','Your name is Ben']),('The pencil is blue. What colour is it?',['blue','It is blue']),('It is ten o’clock. What time is it?',['ten o’clock',"ten o'clock",'It is ten o’clock']),('I have four eggs. How many eggs do I have?',['four','4','You have four eggs']),('Anna likes water. Does Anna like tea?',['No, she does not',"No, she doesn’t"])]
    check_facts[-1]=('Anna likes water. She does not like tea. Does Anna like tea?',check_facts[-1][1])
    bank('write-answer',[typed('Напиши ответ по прочитанному.',text,answers,inputLabel='Короткий ответ') for text,answers in check_facts])

    # Every adventure is a fixed sequence: later steps refer to the same facts.
    school=[pick('Выбери рюкзак капибары.','My bag is blue.','blue',['red','green']),pick('Что положить в рюкзак?','Put three books in the bag.',{'scene':{'word':'book','count':3}},[{'scene':{'word':'book','count':2}},{'scene':{'word':'book','count':4}}]),typed('Допиши артикль для школьного перекуса.','This is ___ apple.','an'),build('I have three books.','У меня три книги.'),pick('Где лежит карандаш?','The pencil is under the table.','under the table',['on the table','beside the table']),dict(kind='clock-set',prompt='Поставь время выхода из дома.',stimulus='We go to school at eight o’clock.',hour=8,minute=0,explanation='Выходим в 8:00.'),typed('Напиши короткий ответ.','I have a pencil. Do you have a pencil?','Yes, I do'),build('We are ready for school.','Мы готовы к школе.')]
    shopping=[pick('Что покупает капибара?','I need four apples.',{'scene':{'word':'apple','count':4}},[{'scene':{'word':'apple','count':3}},{'scene':{'word':'banana','count':4}}]),typed('Допиши слово в списке покупок.','I have ___ apples. Напиши «четыре».','four'),pick('Какого цвета яблоки?','The apples are green.','green',['red','yellow']),typed('Один апельсин. Какой артикль нужен?','I want ___ orange.','an'),build('I would like some milk.','Я хотела бы немного молока.'),pick('Сколько фруктов в пакете?','Four apples and two bananas.', 'six',['five','seven']),typed('Ответь по словам покупателя.','I like apples. Do you like apples?','Yes, I do'),build('Thank you for the apples.','Спасибо за яблоки.')]
    day=[pick('Какой сегодня день?','Today is Saturday.','Saturday',['Monday','Friday']),dict(kind='clock-set',prompt='Поставь время завтрака.',stimulus='Breakfast is at nine o’clock.',hour=9,minute=0,explanation='Завтрак в 9:00.'),typed('Допиши день недели.','Today is Saturday. Tomorrow is ___ .','Sunday'),pick('Что капибара делает утром?','I read a book in the morning.','read',['swim','dance']),dict(kind='clock-set',prompt='Поставь время игры в теннис.',stimulus='I play tennis at half past three.',hour=3,minute=30,explanation='Теннис в 3:30.'),typed('Допиши глагол «уметь».','I ___ play tennis.','can'),build('I help my mother at home.','Я помогаю маме дома.'),pick('Где капибара вечером?','In the evening I am at home.','at home',['at school','in the park'])]
    story_steps=[['Сначала выберем рюкзак.','Теперь положим в рюкзак книги.','Добавим яблоко для перекуса.','Расскажем, сколько книг взяли.','Карандаш потерялся. Где он?','Рюкзак готов. Проверим время выхода.','Перед выходом проверим, взяли ли карандаш.','Всё собрано. Можно отправляться в школу!'],['Начнём со списка: какие продукты нужны капибаре?','Запишем количество яблок в список.','Выберем яблоки нужного цвета.','Добавим в корзину один апельсин.','Теперь вежливо попросим молоко.','В пакете уже яблоки и бананы. Посчитаем их.','Продавец спрашивает, нравятся ли нам яблоки.','Покупки готовы. Поблагодарим продавца!'],['У капибары выходной. Какой сегодня день?','Начнём день с завтрака.','Запомним, какой день будет завтра.','После завтрака выберем утреннее занятие.','Днём капибара пойдёт на теннис. Проверим время.','Расскажем об умении играть в теннис.','После спорта поможем маме.','Наступил вечер. Где отдыхает капибара?']]
    for story_index,(mid,title,description,intro,tasks) in enumerate([('adventure-school','Собираемся в школу','Помоги капибаре собрать рюкзак и выйти вовремя.','У капибары первый учебный день. Соберём вещи, перекус и проверим время.',school),('adventure-shop','Покупаем продукты','Список покупок, просьбы и счёт.','Капибара идёт в магазин. Помоги выбрать продукты и вежливо поговорить с продавцом.',shopping),('adventure-day','Планируем день','Завтрак, чтение, спорт и помощь дома.','Сегодня суббота. Составим день капибары и успеем на теннис.',day)]):
        for q,lead in zip(tasks,story_steps[story_index]):q['storyLead']=lead
        module(mid,'adventures',title,description,[intro,'Проходи шаги по порядку: сведения из истории пригодятся дальше. Можно прерваться и продолжить позже.'],[],tasks,adventure=True,practiceOnly=True)

    module('trace-letters','pen','Обводим буквы','Пишем английские буквы по крупному образцу.',[
        'Веди стилусом по светлому контуру. Можно рисовать пальцем или мышью.',
        'Обводка помогает потренировать движения руки. Красоту и форму буквы проверяем вместе со взрослым.'],[('A B C','Образцы первых букв')],
        [dict(kind='trace',prompt='Обведи букву по контуру.',stimulus='',guide=c,manual=True,expectedText=c,explanation='Проверь вместе со взрослым: все части буквы на месте.') for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'],practiceOnly=True)
    match_words=['cat','dog','sun','pen','book','tree','milk','fish','hat','bag','bird','apple']
    def matching(rows):
        return dict(kind='matching',prompt='Соедини английские слова с переводами.',stimulus='',pairs=[dict(left=w,right=words[w]['ru']) for w in rows],explanation='Пары соединяют слово и его перевод.')
    module('match-pairs','pen','Соединяем пары','Проведи линии между словом и переводом.',[
        'Проведи стилусом от английского слова слева к переводу справа.',
        'Можно также нажать слово, затем перевод. Чтобы исправить пару, соедини слово заново.'],[('cat — кошка','Пример пары')],
        [matching([match_words[i%12],match_words[(i+4)%12],match_words[(i+8)%12]]) for i in range(12)])
    new_match=['ruler','rabbit','horse','egg','rain','shoe','hand','nose','star','flower','chair','doctor']
    bank('match-pairs',[matching([new_match[i%12],new_match[(i+4)%12],new_match[(i+8)%12]]) for i in range(12)])
    module('handwriting','pen','Пишем короткие слова','Послушай слово и напиши его стилусом.',[
        'Пиши на поле от руки. Озвучку можно повторить. Рукописный текст автоматически не распознаётся.',
        'Открой «Проверить вместе со взрослым», сравни с образцом и реши, нужно ли ещё потренироваться.'],[('cat','Короткое слово для записи')],
        [dict(kind='handwriting',prompt='Послушай и напиши слово от руки.',stimulus='',speech=w,audioOnly=True,manual=True,expectedText=w,explanation='Образец: '+w+'.') for w in dictation_words],practiceOnly=True)
    draw_tasks=[]
    for i in range(12):
        shape='ball' if i%2==0 else 'star';color=['blue','red','green','yellow'][i%4];n=1+i%3;size='small' if i%2==0 else 'big'
        en=f'Draw {number(n)} {size} {color} {shape if n==1 else shape+"s"}.'
        ru=f'Нарисуй: {n}; '+('маленький размер' if size=='small' else 'большой размер')+'; '+dict(blue='синий',red='красный',green='зелёный',yellow='жёлтый')[color]+' цвет; '+('мяч' if shape=='ball' else 'звезда')+'.'
        draw_tasks.append(dict(kind='drawing',prompt='Нарисуй по английской инструкции.',stimulus=en,speech=en,manual=True,expectedText=ru,sampleScene=dict(word=shape,paint=shape,color=color,count=n,size=size),explanation=ru))
    module('draw-instruction','pen','Рисуем по инструкции','Цвет, форма, размер и количество на рисунке.',[
        'Прочитай или послушай просьбу капибары. Выбери цвет и нарисуй на поле.',
        'Рисунок проверяем вместе со взрослым: форма, цвет, количество и размер. Здесь нет автоматической оценки рисунка.'],[('Draw two red stars.','Нарисуй две красные звезды.')],draw_tasks,practiceOnly=True)

    # Stable separate ids make new assessment examples resumable and reviewable.
    for m in modules:
        for i,q in enumerate(m['tasks']):
            if 'id' not in q:
                q.update(id=f'{m["id"]}-{i+1:02d}',moduleId=m['id'],skills=[m['id']],themes=[],difficulty=2)
            q.setdefault('stimulus','');q.setdefault('explanation',m['rules'][0])
            if q['kind']=='build':q.setdefault('acceptedAnswers',[q['answer']])
        m['assessmentTasks']=banks.get(m['id'],[])
        for i,q in enumerate(m['assessmentTasks']):
            q.update(id=f'{m["id"]}-check-{i+1:02d}',moduleId=m['id'],skills=[m['id']],themes=[],difficulty=2,checkOnly=True)
            q.setdefault('stimulus','');q.setdefault('explanation',m['rules'][0])
            if q['kind']=='build':q.setdefault('acceptedAnswers',[q['answer']])
        if not m.get('practiceOnly'):
            assert len(m['assessmentTasks'])>=10, m['id']
        for q in m['tasks']+m['assessmentTasks']:
            if q['kind']=='input':assert q['acceptedText'] and all(isinstance(a,str) and a for a in q['acceptedText'])
            if q['kind']=='choice':assert len({str(c) for c in q['choices']})==len(q['choices']),q['id']
    ids=[q['id'] for m in modules for q in m['tasks']+m['assessmentTasks']]
    assert len(ids)==len(set(ids))
    return catalog
