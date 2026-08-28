from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import json, re, html
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/pdf/japan-trip-overview-2027.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
QA=ROOT/'tmp/pdfs';QA.mkdir(parents=True,exist_ok=True)
B=json.loads((ROOT/'budget/assumptions.json').read_text(encoding='utf-8'))
R=Decimal(str(B['fx_rub_per_jpy']))
for name,fn in [('A','arial.ttf'),('AB','arialbd.ttf'),('AI','ariali.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/fn)))
pdfmetrics.registerFontFamily('A',normal='A',bold='AB',italic='AI',boldItalic='AB')
W,H=A4; M=42; CW=W-2*M
INK=HexColor('#263C36'); RED=HexColor('#AD483F'); MUTED=HexColor('#68756F')
BG=HexColor('#FAF7F0'); LINE=HexColor('#DCDDD3'); PALE=HexColor('#EEF1E9')
C=canvas.Canvas(str(OUT),pagesize=A4,pageCompression=1)
C.setTitle('Япония 2027 | Обзор поездки на двоих')
C.setAuthor('План поездки')
C.setSubject('Рабочий план: 10 дней, места и альтернативы, транспорт и бюджет. Версия 26.08.2026.')
PAGE=0; BOXES=[]; TEXT=[]; MIN_Y=54
def norm(s):
    s=str(s).replace('\u2011','-').replace('\u2013','-').replace('\u2014','-').replace('\u2212','-')
    s=re.sub(r'(?<=\d) (?=\d{3}(?:\D|$))','\u00a0',s)
    return re.sub(r'(?<=\d) (?=(?:YEN|RUB)\b)','\u00a0',s)
def fm(v):return f"{Decimal(str(v)).quantize(Decimal('1'),rounding=ROUND_HALF_UP):,}".replace(',',' ')
def money(v,currency='JPY'):
    v=Decimal(str(v));y=v if currency in ('JPY','YEN') else v/R;ru=v if currency=='RUB' else v*R
    return fm(y)+' YEN / '+fm(ru)+' RUB'
def rng(a,b,cur='JPY'):
    a=Decimal(str(a));b=Decimal(str(b))
    y1,y2=(a,b) if cur!='RUB' else (a/R,b/R)
    r1,r2=(a,b) if cur=='RUB' else (a*R,b*R)
    return fm(y1)+'-'+fm(y2)+' YEN / '+fm(r1)+'-'+fm(r2)+' RUB'
def ps(size=11,leading=None,color=INK,bold=False):
    return ParagraphStyle('p',fontName='AB' if bold else 'A',fontSize=size,leading=leading or size*1.36,textColor=color,spaceAfter=0,allowWidows=0,allowOrphans=0)
def para(s,x,y,w,size=11,color=INK,bold=False,leading=None):
    s=norm(s);p=Paragraph(s,ps(size,leading,color,bold));_,hh=p.wrap(w,H)
    assert y-hh>=MIN_Y-0.1, f'PAGE {PAGE}: overflow {y-hh}: {s[:100]}'
    p.drawOn(C,x,y-hh);BOXES.append((PAGE,x,y-hh,w,hh,s[:70]));TEXT.append(s)
    return y-hh
def section_label(s,y=H-38):
    C.setFillColor(RED);C.setFont('AB',9);C.drawString(M,y,norm(s).upper())
def newpage(chapter,title,sub=None):
    global PAGE
    if PAGE:C.showPage()
    PAGE+=1
    C.setFillColor(BG);C.rect(0,0,W,H,fill=1,stroke=0)
    C.setStrokeColor(LINE);C.line(M,43,W-M,43)
    C.setFillColor(MUTED);C.setFont('A',8)
    C.drawString(M,28,'Япония 2027 | Рабочая версия 26.08.2026')
    C.drawRightString(W-M,28,f'{PAGE} / 9')
    section_label(chapter)
    y=H-67
    y=para(title,M,y,CW,25,bold=True,leading=29)
    if sub:y=para(sub,M,y-9,CW,10.2,color=MUTED)
    return y-21
def note(s,y,color=PALE):
    p=Paragraph(norm(s),ps(10.2,14))
    _,hh=p.wrap(CW-24,H)
    C.setFillColor(color);C.roundRect(M,y-hh-22,CW,hh+22,8,fill=1,stroke=0)
    para(s,M+12,y-11,CW-24,10.2,leading=14)
    return y-hh-35
def heading(s,y,size=14):return para(s,M,y,CW,size,bold=True)-10
def table(headers,rows,widths,y,size=10,rowpad=8):
    style=ps(size,size*1.3)
    def cell(v,header=False):
        return Paragraph(norm(v),ps(size if not header else size-0.3,(size if not header else size-0.3)*1.3,white if header else INK,header))
    data=[[cell(h,True) for h in headers]]+[[cell(v) for v in row] for row in rows]
    t=Table(data,colWidths=widths,hAlign='LEFT')
    cmds=[('BACKGROUND',(0,0),(-1,0),INK),('VALIGN',(0,0),(-1,-1),'TOP'),
          ('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),
          ('TOPPADDING',(0,0),(-1,-1),rowpad),('BOTTOMPADDING',(0,0),(-1,-1),rowpad),
          ('LINEBELOW',(0,0),(-1,0),0.5,INK)]
    for i in range(1,len(data)):
        cmds += [('BACKGROUND',(0,i),(-1,i),white if i%2 else PALE),('LINEBELOW',(0,i),(-1,i),.4,LINE)]
    t.setStyle(TableStyle(cmds));tw,th=t.wrap(CW,H)
    assert y-th>=MIN_Y, f'PAGE {PAGE} table overflow: {y-th}'
    t.drawOn(C,M,y-th);BOXES.append((PAGE,M,y-th,tw,th,'TABLE'))
    TEXT.extend(str(v) for row in rows for v in row)
    return y-th-16
def splitmoney(s):
    return s.replace(' YEN / ',' YEN<br/>/ ')
def day(n,date,title,night,main,alt,pace,y):
    pparts=[('main','<b>Предпочтительно.</b> '+main),('alt','<b>Одна альтернатива.</b> '+alt),('pace','<b>Темп и детали.</b> '+pace)]
    width=CW-28; total=50
    for key,txt in pparts:
        pp=Paragraph(norm(txt),ps(10.4,14));_,hh=pp.wrap(width,H);total+=hh+8
    total+=4
    assert y-total>=MIN_Y, f'Day {n} exceeds page {PAGE}: {y-total}'
    C.setFillColor(white);C.setStrokeColor(LINE);C.roundRect(M,y-total,CW,total,9,fill=1,stroke=1)
    C.setFillColor(RED);C.circle(M+20,y-22,11,fill=1,stroke=0)
    C.setFont('AB',9);C.setFillColor(white);C.drawCentredString(M+20,y-25,str(n).zfill(2))
    yy=para(title,M+39,y-11,CW-54,13.3,bold=True,leading=16)
    yy=para(date+' | Ночь: '+night,M+39,yy-2,CW-54,9.1,color=MUTED,leading=12)-12
    for key,txt in pparts:yy=para(txt,M+14,yy,width,10.4,leading=14)-8
    return y-total-13

# 1 / overview
y=newpage('01 / Поездка','Япония. Наша первая поездка','Токио, Фудзи, Киото и Осака - без гонки, с JoJo, аниме и временем просто побыть вместе.')
C.setFillColor(RED);C.circle(W-M-40,y-41,29,fill=1,stroke=0)
y=para('10 дней в Японии<br/><font color="#AD483F">Осень 2027</font>',M,y,CW-100,24,bold=True,leading=31)-22
y=para('<b>Пример дат: 17-26 октября.</b> Это предложение, не бронь. Перелёты и длинные пересадки считаем отдельно. В текущей модели - 9 ночей; первый и последний дни частично уйдут на дорогу.',M,y,CW,11)-19
y=table(['База','Ночи','Зачем останавливаемся'],[
 ['Токио','3','Аниме, JoJo, городские районы и первое знакомство с Японией'],
 ['Кавагутико / Фудзи','1','Озеро, виды на гору и ещё одно утреннее окно для ясной погоды'],
 ['Киото','3','Фусими Инари, старые улицы и спокойные прогулки'],
 ['Осака','2','Еда, вечерний город и вылет домой через KIX']],
 [CW*.25,CW*.12,CW*.63],y,10.3,7)
y=heading('Что уже решили',y)
y=para('Едем шестером, тремя парами. <b>Для каждой пары отдельный двухместный номер.</b> Все граждане РФ; четверо впервые в Японии. Наш бюджет ниже рассчитан только на нас двоих, не на всю компанию.',M,y,CW,10.7)-11
y=para('<b>Обязательно:</b> Фусими Инари и THE JOJO WORLD с IGGY CAFE. Остальные места пока выбираем. Обычно ходим умеренно; после насыщенного пешего дня следующий спокойнее.',M,y,CW,10.7)-15
y=note('<b>Бюджет на двоих.</b> Поездка до '+money(550000,'RUB')+'; покупки отдельно '+money(100000,'RUB')+'. Общий предел '+money(650000,'RUB')+'.',y)
y=para('<b>Почему октябрь:</b> по климатическим нормам он мягче ноября. У Кавагутико средний суточный максимум / минимум октября около +18 / +9 °C. На утро нужна тёплая одежда. Видимость Фудзи и погоду 2027 гарантировать нельзя. [1]',M,y,CW,10.2)-10
y=para('Отели, билеты и точные даты не выбраны. Подбор конкретных отелей оставлен на потом. Все суммы: <b>YEN / RUB</b>, условный курс <b>1 YEN = 0,53 RUB</b>; это не текущая котировка.',M,y,CW,9.7,color=MUTED)

# 2 / Tokyo days
y=newpage('02 / Дни','Первые три дня: Токио','Даты ниже иллюстрируют окно 17-26 октября. Альтернатива заменяет часть дня, а не добавляется к нему.')
y=day(1,'17 октября','Прилететь и выдохнуть','Токио',
 'Аэропорт, дорога в отель, заселение и отдых. Если останутся силы - короткий вечер в <b>Shinjuku</b> и ужин.',
 '<b>Shibuya Crossing</b> вместо Shinjuku, только если удобно от отеля. При позднем прилёте - без прогулки.',
 'Лёгкий день. Не ставим обязательные места и невозвратные входные билеты. На прогулку до 1-2 часов.',y)
y=day(2,'18 октября','Старый Токио и аниме-магазины','Токио',
 'Утром <b>Asakusa и Senso-ji</b>: храм и прилегающие улицы, около 2 часов. После обеда <b>Akihabara</b>: 2-3 часа на аниме-магазины, мерч и паузы.',
 '<b>teamLab Borderless</b> вместо утреннего блока Asakusa: музей света, проекций и зеркал, планировочно 2-3 часа. Akihabara сохраняем, заново проверив дорогу. [3]',
 'Средняя нагрузка, вечер свободный. Если выбран teamLab, старый ориентир на двоих от '+money(7200)+'; точный тариф ещё проверить.',y)
y=day(3,'19 октября','Наш день JoJo','Токио',
 'Короткий <b>Meiji Jingu</b>, затем Shibuya PARCO: <b>THE JOJO WORLD + IGGY CAFE</b>. Для магазина, кафе и мерча оставляем 2,5-3,5 часа. <b>Shibuya Sky</b> - если хочется и есть удобный слот. [2]',
 '<b>Harajuku</b> вместо Meiji Jingu. JoJo не заменяем. Если день затягивается, первой убираем смотровую.',
 'Средний темп. Sky: старый ориентир на двоих '+money(6800)+'. Кафе примерно '+rng(4000,6000)+' уже внутри питания; мерч отдельно.',y)

# 3 / Fuji
y=newpage('02 / Дни','Фудзи и дорога в Киото','Одна ночь у озера даёт вечер и утро для видов. Гора может оставаться в облаках - запасной план нужен в любом случае.')
y=day(4,'20 октября','Токио - Кавагутико','Кавагутико',
 'Утром выселение и автобус из Shinjuku. Оставляем багаж в отеле, обедаем. После отдыха - <b>озеро Kawaguchiko и Oishi Park</b>, без попытки объехать всё побережье.',
 '<b>Mt. Fuji Panoramic Ropeway</b> вместо Oishi Park, если позволяют погода и очередь. Старый ориентир на двоих '+money(2000)+'.',
 'На переезд с багажом закладываем полдня. На прогулку 1,5-2,5 часа с остановками. При дожде короткая прогулка, еда и отдых.',y)
y=day(5,'21 октября','Утренний вид на Фудзи - Киото','Киото',
 'Короткий выход к озеру до завтрака, если удобно от места ночёвки. Затем <b>автобус в Mishima и синкансэн в Kyoto</b>. Вечером заселение; <b>Gion</b> только по силам.',
 '<b>Chureito / Arakurayama Sengen Park</b> вместо прогулки у озера, только если хватает времени, погоды и сил. Не совмещаем обе утренние прогулки.',
 'Главный блок - переезд: примерно 5-7 часов от отеля до отеля. Внутри этого времени оставляем 60-90 минут на стыковку. Утреннюю опцию убираем первой.',y)
y=note('<b>Фудзи без гонки.</b> Раннее окно у озера практичнее обязательного подъёма перед автобусом. JNTO рекомендует ночёвку и утренний вид: позже дымка и облака могут скрывать гору. Это дополнительная возможность, не гарантия. [1]',y)
y=heading('Где пока оставляем гибкость',y)
y=para('Если вид на Фудзи станет важнее ещё одного городского дня, можно отдельно сравнить две ночи у озера. Пока в план добавлена только одна. Переставить день по погоде можно лишь при подходящих условиях отмены жилья и транспорта.',M,y,CW,11)

# 4 / Kyoto
y=newpage('02 / Дни','Киото: тории и спокойные прогулки','Фусими Инари обязательно. Подъём до вершины - по желанию; за насыщенным днём следует более лёгкий.')
y=day(6,'22 октября','Фусими Инари и старый Киото','Киото',
 'Утром <b>Fushimi Inari Taisha</b>: святилище и дорожки с красными тории. Базово 1,5-2,5 часа без обязательной вершины. После обеда и отдыха - компактный блок <b>Kiyomizu-dera / Higashiyama</b>. [4]',
 '<b>Gion</b> вместо Kiyomizu-dera / Higashiyama: короткая прогулка в одном районе. Сам Фусими Инари остаётся в любом варианте.',
 'Полный маршрут по горе займёт планировочно 3-4 часа: тогда без второго большого пешего блока. Старый ориентир Kiyomizu на двоих '+money(1000)+'. Условия общего входа в Inari ещё сверим.',y)
y=day(7,'23 октября','Arashiyama без спешки','Киото',
 'Без ранней гонки едем в <b>Arashiyama</b>: бамбуковая роща и компактная прогулка около 1,5-2 часов, затем кафе и отдых. Вечером <b>Pontocho</b> с ужином по желанию.',
 '<b>Kinkaku-ji</b> вместо Arashiyama, а не после неё. Старый ориентир на двоих '+money(1000)+'.',
 'Спокойный день, особенно после полного Inari. Не добавляем ещё несколько храмов и не пытаемся обойти два удалённых района.',y)
y=note('<b>Правило комфорта:</b> выбираем один главный утренний блок и один небольшой вечерний. Кафе, транспорт и время на отдых входят в день так же, как достопримечательности.',y)
y=para('Названия районов в плане не означают длинный пеший маршрут целиком. Точные входы, остановки, часы и длину прогулок определим после выбора базы. Общий маршрут всей шестёрки пока не утверждён.',M,y,CW,10.5)

# 5 / Osaka
y=newpage('02 / Дни','Осака и возвращение домой','Предпочтительный вариант - городской день без парка. USJ остаётся одной полной заменой, если захочется аттракционов.')
y=day(8,'24 октября','Киото - Осака, замок и вечерний город','Осака',
 'Выселение, обычный поезд, багаж в отель. <b>Osaka Castle</b> по силам; вечером <b>Namba и Dotonbori</b> одним блоком с ужином.',
 '<b>Shinsekai</b> вместо посещения замка. Вечер в Dotonbori сохраняем.',
 'После смены базы не перегружаемся. Парк у замка и музей внутри - разные варианты. Старый ориентир музея на двоих '+money(2400)+'.',y)
y=day(9,'25 октября','Еда, покупки и свободная Осака','Осака',
 '<b>Kuromon Market</b> с едой, затем отдых и покупки без спешки. <b>Umeda Sky Building</b> по желанию, если ещё хочется смотровую. Вечером собрать багаж.',
 '<b>Universal Studios Japan</b> вместо всего городского дня: тематический парк с аттракционами и мирами Nintendo, Harry Potter и другими. Отдельный полный день, не музей JoJo. [5]',
 'Городской вариант умеренный. Umeda: старый ориентир на двоих '+money(4000)+'. USJ пока не оценён; при выборе пересчитываем входы и нагрузку.',y)
y=day(10,'26 октября','Завтрак и вылет из KIX','Без ночи в Японии',
 'Спокойный завтрак рядом с отелем; короткий выход в <b>Namba</b> только при позднем рейсе. Затем аэропорт <b>Kansai (KIX)</b>, перелёт и пересадка.',
 '<b>Kuromon Market</b> вместо завтрака / прогулки в Namba, только если подходят часы и рейс не ранний. При раннем вылете обе прогулки отменяем.',
 'Прибытие в аэропорт за 3 часа - рабочий запас, требования перевозчика проверим. Дорогу и запас на задержку прибавляем отдельно. Дата прибытия в Москву зависит от рейса.',y)

# 6 / Intercity
y=newpage('03 / Перемещения','Между городами и аэропортами','Все цены ниже на двоих. Это ориентиры из проекта и планировочные допущения, не тарифы или расписания осени 2027.')
transit=[
 ['Москва - Токио<br/>KIX - Москва','Самолёт с пересадкой. Сравним единый multi-city билет с возвратом через Токио.',
  'Для отпуска заложить по 1-2 дня на каждое направление. Точная длительность зависит от рейса; пример 20 ч в Китае - только сама пересадка.',
  rng(140000,220000,'RUB')+'<br/>за оба направления'],
 ['Аэропорт Токио - отель','Поезд или аэропортовый автобус; выбор зависит от HND / NRT и отеля.',
  'Для плана 1-2 ч на наземный путь, отдельно въездные формальности и багаж.',
  money(6000)+'<br/>временный запас, не тариф'],
 ['Токио - Кавагутико','Автобус из Shinjuku.',
  'Около 1 ч 45 мин между остановками по старой оценке; с багажом и отелями - полдня.',
  money(4400)],
 ['Кавагутико - Mishima','Междугородний автобус.',
  'Для плана около 1,5-2 ч в автобусе; фактическое расписание ещё проверить.',
  rng(5000,5400)],
 ['Mishima - Kyoto','Синкансэн; подходящий поезд и необходимость пересадки проверим.',
  'Около 2-2,5 ч в поезде как рабочий ориентир. Весь D05: 5-7 ч от двери до двери.',
  rng(21600,22600)],
 ['Kyoto - Osaka','Обычный поезд JR; синкансэн здесь не обязателен.',
  'Около 25-30 мин между станциями по старой оценке; 1-2 ч на смену отеля с багажом.',
  money(1160)],
 ['Осака - KIX','Поезд или аэропортовый автобус под рейс.',
  'Для плана около 1-1,5 ч на наземный путь; точный маршрут зависит от базы и терминала.',
  'Внутри строки «Осака + KIX» на следующей странице']
]
# more readable two-column segmented cards rather than 4 narrow columns
for title,how,time,cost in transit:
    y=para(title,M,y,CW,12,bold=True)-3
    y=para(how+' <b>Время:</b> '+time,M,y,CW,9.8,leading=13)-4
    y=para('<b>Цена:</b> '+cost,M,y,CW,9.8,leading=13)-11
y=para('Времена 1-2 ч, 1,5-2 ч и 2-2,5 ч - грубые планировочные интервалы, не проверенные отправления. Длинную пересадку выбираем по чистой экономии после еды, ночёвки и багажа; возможность выхода в город заранее проверяем.',M,y,CW,9.2,color=MUTED,leading=12)

# 7 / Local movement and allocation
y=newpage('03 / Перемещения','По городу и с чемоданами','Считаем путь от двери до двери, а не только время поезда. Не покупаем общий проездной до расчёта конкретных поездок.')
y=table(['Где','Как планируем двигаться','Время для плана'],[
 ['Токио','Метро / городские поезда между районами, внутри районов пешком. Asakusa, Akihabara и Shibuya - отдельные блоки.','Ориентир 20-60 мин на переход между районами, включая подход и ожидание.'],
 ['Кавагутико','Местный автобус и короткие пешие участки; конкретная база определит путь к озеру.','Ориентир 20-60 мин на локальный выезд. Очередь на канатку отдельно.'],
 ['Киото','JR / метро / автобус под адреса. Kyoto Station - JR Inari: сайт святилища указывает около 5 мин поездом. [4]','От отеля дольше: добавляем подход, ожидание и пересадки. В Arashiyama не идём пешком из центра.'],
 ['Осака','Поезд / метро между районами; Namba и Dotonbori объединяем в один вечерний блок.','Ориентир 20-45 мин на городской переход; KIX отдельный выезд.']
],[CW*.16,CW*.49,CW*.35],y,10,7)
y=heading('Как устроен рабочий транспортный бюджет',y)
y=para('Ниже - распределение общего лимита, а не ещё один счёт поверх сметы. Все суммы на двоих за всю поездку. Синкансэн уже включён.',M,y,CW,10.2)-10
alloc=[('Токио: городские поездки',6000),('Токио - Кавагутико',4400),('Кавагутико: местные поездки',4000),
('Кавагутико - Mishima',5200),('Синкансэн Mishima - Kyoto',22100),('Киото: городские поездки',6000),
('Kyoto - Osaka',1160),('Осака + дорога в KIX',7000),('Запас: аэропорт прилёта - Токио',6000),('Нераспределённый запас на переезды',5640)]
assert sum(v for _,v in alloc)==67500
y=table(['Статья','YEN / RUB'],[[a,money(b)] for a,b in alloc]+[['<b>Итого в рабочей смете</b>','<b>'+money(67500)+'</b>']],[CW*.57,CW*.43],y,9.5,4)
y=para('В старой детализации не было отдельного трансфера из аэропорта прилёта. Здесь он показан временным запасом внутри общего конверта. После выбора аэропорта проверим достаточность суммы. Доставка/хранение багажа и стирка - отдельная категория бюджета.',M,y,CW,9.2,color=MUTED,leading=12)

# 8 / Full category budget
y=newpage('04 / Бюджет','Полный бюджет на двоих','Примерные суммы за всю поездку. В каждой ячейке YEN / RUB - эквиваленты одной суммы, их не складывают. Курс условный: 1 YEN = 0,53 RUB.')
labels={'flights':'Перелёты туда / обратно','hotels':'Отели, 9 ночей<br/>1 номер на двоих','food':'Питание, 10 дней<br/>включая IGGY CAFE','transport':'Наземный транспорт<br/>включая синкансэн','activities':'Входные билеты<br/>без USJ','documents':'Документы и сервисные расходы','insurance':'Страховка на двоих','connectivity':'Связь на двоих','baggage_laundry':'Хранение / доставка багажа, стирка','hotel_taxes':'Не включённые налоги и сборы жилья'}
rows=[]
for item in B['items']:
    rows.append([labels[item['id']]]+[splitmoney(item['equivalents'][k]['display']) for k in ['low','base','high']])
y=table(['Категория','Нижний','Рабочий','Верхний'],rows,[CW*.31,CW*.23,CW*.23,CW*.23],y,9.3,5)
totals={}
for k in ['low','base','high']:
    j=sum(Decimal(str(x[k])) for x in B['items'] if x['currency']=='JPY')
    ru=sum(Decimal(str(x[k])) for x in B['items'] if x['currency']=='RUB')
    sub=ru+j*R;reserve=sub*Decimal('0.15');total=sub+reserve
    totals[k]=(sub,reserve,total,total+Decimal('100000'))
summary=[]
for label,index in [('До резерва',0),('Резерв 15%',1),('<b>Поездка с резервом</b>',2),('Шопинг отдельно',None),('<b>Всего с покупками</b>',3)]:
    summary.append([label]+[splitmoney(money(100000 if index is None else totals[k][index],'RUB')) for k in ['low','base','high']])
y=table(['Итоги','Нижний','Рабочий','Верхний'],summary,[CW*.31,CW*.23,CW*.23,CW*.23],y,9.3,5)
y=para('<b>Рабочий итог укладывается в предел.</b> Верхний столбец - стресс-сценарий, он превышает согласованный бюджет и не является разрешением потратить больше. Дополнительный резерв на фонд покупок не начислен.',M,y,CW,9.5,color=MUTED,leading=12.5)

# 9 / housing, assumptions, sources
y=newpage('04 / Бюджет','Что стоит за суммами','Рабочий сценарий: '+money(totals['base'][2],'RUB')+' на поездку; с покупками '+money(totals['base'][3],'RUB')+'.')
y=heading('Отели: ориентиры, без выбора конкретных',y)
y=para('Для компании нужны 3 отдельных номера, но ниже стоимость только одного номера для нашей пары. Подбор отелей отложен. Диапазоны - прежние оценки проекта, не предложения на октябрь 2027.',M,y,CW,10.1)-11
hotelrows=[
 ['Токио','3',rng(20000,27000),rng(60000,81000)],
 ['Кавагутико','1',rng(32000,43000),rng(32000,43000)],
 ['Киото','3',rng(25000,40000),rng(75000,120000)],
 ['Осака','2',rng(13000,20000),rng(26000,40000)],
]
y=table(['Город','Ночей','За номер / ночь','За весь блок'],[[a,b,splitmoney(c),splitmoney(d)] for a,b,c,d in hotelrows],[CW*.19,CW*.10,CW*.355,CW*.355],y,9.4,6)
y=heading('Как читаем бюджет',y)
for text in [
 '<b>Шопинг:</b> '+money(100000,'RUB')+' на двоих, в первую очередь JoJo / аниме-мерч. Кафе - питание, игры - развлечения. Дополнительный авиабагаж после покупок проверим отдельно.',
 '<b>Без двойного счёта:</b> синкансэн уже в транспорте; IGGY CAFE внутри питания; гостиничный номер не умножаем на двоих ещё раз. Включённые в тариф налоги и завтраки вычтем из отдельных строк.',
 '<b>Предварительные запасы:</b> документы, страховка, связь, багаж и налоги пока не подтверждены котировками. USJ не включён. Входы - конверт, а не точная сумма всех перечисленных альтернатив.',
 '<b>До бронирований:</b> выберем даты, рейсы и багаж; определим доступную зарубежную оплату и документы для граждан РФ. Отели выберем позже. Время внутри страны и цены перепроверим.'
]:
    y=para(text,M,y,CW,9.9,leading=13.2)-8
y=heading('Источники и статус версии',y,12)
y=para('Сводка проекта на 26.08.2026. Тарифы транспорта, отелей и большинства входов перенесены из исходного диалога как ориентиры; это не новая проверка рынка. Суммы округлены до целых, итоги рассчитаны до округления. Официальные ссылки ниже подтверждают описания мест и климат, но не доступность 2027.',M,y,CW,9,leading=12)-8
sources=[
 ('[1] Климат JMA: Кавагутико','https://ds.data.jma.go.jp/stats/etrn/view/nml_sfc_ym.php?block_no=47640&prec_no=49&view=a2'),
 ('[1] JNTO: озёра Фудзи и утренние виды','https://www.japan.travel/en/itineraries/fuji-five-lakes-itinerary/'),
 ('[2] THE JOJO WORLD / IGGY CAFE','https://bandainamco-am.co.jp/official_shop/jojo/tokyo/'),
 ('[3] teamLab Borderless','https://www.teamlab.art/e/tokyo/'),
 ('[4] Fushimi Inari: как добраться','https://inari.jp/en/access/'),
 ('[5] Universal Studios Japan: зоны парка','https://www.usj.co.jp/web/en/us/areas')]
for name,url in sources:
    y=para('<link href="'+html.escape(url,quote=True)+'" color="#AD483F">'+html.escape(name)+'</link>',M,y,CW,8.8,leading=11.2)-3
C.save()
assert PAGE==9
(QA/'layout-boxes.json').write_text(json.dumps(BOXES,ensure_ascii=False,indent=2),encoding='utf-8')
(QA/'overview-content.txt').write_text('\n\n'.join(TEXT),encoding='utf-8')
print('Created',OUT,'pages',PAGE,'bytes',OUT.stat().st_size)
