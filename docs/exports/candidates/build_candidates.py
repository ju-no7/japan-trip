from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import urlencode
import json, re, html
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT/'output/pdf/japan-places-candidates-2027.pdf'
QA = ROOT/'tmp/pdfs/candidates'
QA.mkdir(parents=True, exist_ok=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
FX = Decimal(str(json.loads((ROOT/'budget/assumptions.json').read_text(encoding='utf-8-sig'))['fx_rub_per_jpy']))
def fm(n): return f"{Decimal(str(n)).quantize(Decimal('1'), rounding=ROUND_HALF_UP):,}".replace(',', ' ')
def money(n): return fm(n)+' YEN / '+fm(Decimal(str(n))*FX)+' RUB'
def money_range(a,b): return fm(a)+'-'+fm(b)+' YEN / '+fm(Decimal(str(a))*FX)+'-'+fm(Decimal(str(b))*FX)+' RUB'
def E(city,files,title,tier,when,time,load,why,fit,cost,query=None):
    return dict(city=city,files=['places/'+city+'/'+f+'.md' for f in files.split(',')],title=title,tier=tier,when=when,time=time,load=load,why=why,fit=fit,cost=cost,query=query or title+' '+city)

# Рейтинг - редакционное предложение для текущего маршрута, не изменение статусов карточек.
ENTRIES=[
 E('tokyo','jojo-world,iggy-cafe','THE JOJO WORLD + IGGY CAFE','Обязательно','D03 · 19 октября','2,5-3,5 ч на весь блок','умеренная',
   'Официальный магазин JoJo и кафе внутри него в Shibuya PARCO. Самое точное попадание в ваши общие интересы: мерч, тематическая еда и время спокойно всё рассмотреть.',
   'Сохраняем первым. Это две карточки проекта, но одна поездка и один общий запас времени. Посадка всей шестёрки и правила входа на 2027 ещё не подтверждены.',
   'Кафе: '+money_range(4000,6000)+' на двоих, уже внутри питания. Мерч отдельно; общий вход не оценён.','THE JOJO WORLD TOKYO Shibuya PARCO'),
 E('tokyo','akihabara','Akihabara','Приоритет','D02 · 18 октября','2-3 ч','умеренная',
   'Район для аниме-магазинов, фигурок и поиска мерча. Для вас это самостоятельная часть путешествия, а не короткая остановка между храмами.',
   'Оставляем полноценный блок с паузами. Не заменяем его автоматически на музей или смотровую; магазины и конкретные покупки выберем отдельно.',
   'Мерч - из фонда шопинга; кафе - из питания. Отдельный общий вход в район не заложен.','Akihabara Tokyo'),
 E('tokyo','asakusa,sensoji','Asakusa + Senso-ji','Приоритет','D02 · 18 октября','1-2 ч вместе','умеренная',
   'Старый Токио: храм Senso-ji и прогулка по прилегающим улицам Asakusa. Хороший контраст к аниме-магазинам и современной Shibuya.',
   'Один утренний блок, не две отдельные экскурсии. Сокращаем прогулку при усталости; специальные платные зоны и услуги проверим отдельно.',
   'Вход отдельно не оценён в проекте; еда, покупки и платные услуги отдельно.','Senso-ji Asakusa Tokyo'),
 E('tokyo','shibuya','Shibuya / Crossing','Приоритет','D03 · 19 октября','0,5-1 ч вне PARCO','низкая при коротком круге',
   'Знаменитый перекрёсток и современный городской район. Удобная короткая прогулка в тот же день, когда едем за JoJo в PARCO.',
   'Объединяем с JoJo по географии, но не добавляем ещё несколько часов хождения по магазинам. Можно увидеть район и без подъёма на Sky.',
   'Покупки и заведения отдельно; общий прогулочный билет не заложен.','Shibuya Scramble Crossing Tokyo'),
 E('tokyo','meiji','Meiji Jingu','Приоритет','D03 · 19 октября','1-1,5 ч','умеренная',
   'Синтоистское святилище среди деревьев. Спокойное начало дня перед шумной Shibuya и тематическим магазином.',
   'Короткий утренний вариант в текущем плане. Harajuku может заменить его; проходить обе зоны полностью перед JoJo не требуется.',
   'Общий вход отдельно не оценён; доступ и стоимость выбранных дополнительных зон ещё проверить.','Meiji Jingu Tokyo'),
 E('tokyo','shibuya-sky','Shibuya Sky','По желанию','D03 · 19 октября','1-1,5 ч + очередь','умеренная',
   'Смотровая над Shibuya: панорама города как завершение дня. Из кандидатов на смотровую наиболее естественно сочетается с днём JoJo.',
   'Только если останутся силы и будет удобный слот. Не жертвуем временем в кафе ради заката; ветер и доступ на крышу могут изменить план.',
   'Исторический ориентир: '+money(6800)+' на двоих, онлайн после 15:00. Не тариф 2027.','Shibuya Sky Tokyo'),
 E('tokyo','teamlab','teamLab Borderless','Альтернатива','Вместо блока D02','2-3 ч + дорога','умеренная, много стоя',
   'Цифровой художественный музей света, проекций и зеркал в Azabudai Hills. Кандидат на необычное свидание; это не музей аниме и не teamLab Planets.',
   'Заменяет Asakusa + Senso-ji, а не добавляется сверху. Akihabara стараемся сохранить; географию дня пересчитываем. Проверить предупреждения о свете и тёмных помещениях.',
   'Исторический ориентир: от '+money(7200)+' на двоих. Точный билет на 2027 не выбран.','teamLab Borderless Azabudai Hills Tokyo'),
 E('tokyo','harajuku','Harajuku','По желанию','Замена Meiji в D03','1-1,5 ч','умеренная',
   'Район уличной моды, магазинов и яркой городской атмосферы. Скорее вариант для прогулки и разглядывания витрин, чем обязательная достопримечательность.',
   'Выбираем вместо Meiji, если больше хочется города и покупок. В насыщенный день сокращаем первым; JoJo остаётся главным блоком.',
   'Покупки отдельно; кафе учитываем в питании.','Harajuku Tokyo'),
 E('tokyo','shinjuku','Shinjuku','По силам','D01 · 17 октября','до 1-2 ч','низкая при коротком круге',
   'Первое знакомство с вечерним Токио: городские огни, улицы и ужин. Его ценность в плане - мягко начать поездку после перелёта.',
   'Только после отдыха и если удобно от отеля. При позднем прилёте отменяем без потерь; Shibuya может заменить прогулку по расположению базы.',
   'Отдельный вход не заложен; ужин и выбранные заведения отдельно.','Shinjuku Tokyo'),
 E('tokyo','skytree','Tokyo Skytree','Альтернатива','Вместо другой смотровой','1,5-2 ч + очередь','умеренная',
   'Высотная смотровая башня. Подойдёт, если панорама города важнее ещё одного прогулочного района или если предпочтёте её Shibuya Sky.',
   'Не ставим обе токийские смотровые автоматически. Если переносим посещение в D02, заново распределяем время, сохраняя приоритет аниме-магазинов.',
   'Исторический ориентир: '+money_range(4800,7600)+' на двоих; зависит от типа билета.','Tokyo Skytree'),
 E('tokyo','ueno','Ueno','Резерв','Замена крупного блока D02','1,5-3 ч','умеренная',
   'Парковый и музейный район для более спокойной прогулки. Может понравиться, если захочется зелени или конкретного музея вместо части шопинга.',
   'В каталоге сохраняем, но по вашим интересам Akihabara выше. Музей или зоопарк не считаем уже выбранными и не добавляем в свободное время автоматически.',
   'Музеи и зоопарк отдельно: YEN - уточнить / RUB - уточнить.','Ueno Park Tokyo'),
 E('fuji','kawaguchiko','Озеро Kawaguchiko','Приоритет','D04-D05 · 20-21 октября','1-2 ч + короткое утро','низкая при коротком участке',
   'Главная идея ночёвки у Фудзи: озеро, виды на гору и время без спешки. Выбираем доступный участок берега, а не полный обход озера.',
   'Сохраняем вечер и короткое утреннее окно рядом с ночёвкой. Облака могут скрыть гору; видимость не гарантируется.',
   'Отдельный вход в проекте не указан; местный транспорт отдельно.','Lake Kawaguchi Japan'),
 E('fuji','oishi-park','Oishi Park','Приоритет','D04 · 20 октября','0,5-1 ч + дорога','низкая',
   'Парк у берега озера как конкретная точка для прогулки и фотографий. Дополняет озеро, а не требует отдельной большой экскурсии.',
   'Основной кандидат после заселения. Выбираем по погоде и дороге от отеля; не обещаем определённое цветение или осеннюю окраску.',
   'Цена в исходных карточках не указана: YEN - уточнить / RUB - уточнить.','Oishi Park Kawaguchiko'),
 E('fuji','ropeway','Mt. Fuji Panoramic Ropeway','Альтернатива','Вместо Oishi Park в D04','1-1,5 ч + очередь','низкая-умеренная',
   'Канатная дорога к панорамной точке над озером. Вариант, если хочется посмотреть на пейзаж сверху без длинной пешей прогулки.',
   'Выбираем вместо Oishi, если подходят погода и очередь. При ветре или плохой видимости не привязываем к ней весь день.',
   'Исторически туда-обратно: '+money(2000)+' на двоих. Не тариф 2027.','Mt Fuji Panoramic Ropeway'),
 E('fuji','chureito','Chureito / Arakurayama Sengen Park','Резерв','Утро D05 · 21 октября','1,5-2,5 ч + дорога','повышенная: подъём',
   'Пагода и известный ракурс с Фудзи. Сильный фотокандидат, но требует больше сил и времени, чем короткая прогулка у озера.',
   'Только вместо утреннего берега и с надёжным запасом до автобуса. Лестницы, доступ и возврат за багажом проверить; межгород важнее.',
   'В исходном диалоге вход указан бесплатным; на 2027 не подтверждено. Транспорт отдельно.','Chureito Pagoda Arakurayama Sengen Park'),
 E('kyoto','fushimi-inari','Fushimi Inari Taisha','Обязательно','D06 · 22 октября','1,5-2,5 ч; полный 3-4 ч','умеренная; полный - высокая',
   'Святилище с дорожками красных тории. Главный обязательный пункт Киото; подъём до вершины не нужен, чтобы включить его в поездку.',
   'База - без обязательной вершины. Если выбираем полный горный маршрут, убираем второй большой пеший блок, а следующий день оставляем легче.',
   'Условия общего входа ещё проверить: YEN - уточнить / RUB - уточнить.','Fushimi Inari Taisha Kyoto'),
 E('kyoto','kiyomizu,higashiyama','Kiyomizu-dera + Higashiyama','Приоритет','D06 · 22 октября','около 2-3 ч вместе','умеренная-повышенная',
   'Храм Kiyomizu-dera и старые улицы Higashiyama. Один связанный блок для знакомства с историческим Киото, с остановками и отдыхом.',
   'После обеда и паузы, только при коротком Inari. Не суммируем время одних и тех же улиц дважды. При усталости заменяем блок коротким Gion.',
   'Kiyomizu: исторически '+money(1000)+' на двоих. В Higashiyama покупки и еда отдельно.','Kiyomizu-dera Kyoto'),
 E('kyoto','gion','Gion','Приоритет','Один вечер D05 или D06','0,5-1 ч','низкая при коротком круге',
   'Исторический район для вечерней прогулки. Подходит как небольшое знакомство с Киото после заселения или как облегчённая замена длинному блоку.',
   'Достаточно одного вечера, не повторяем ради отметки в списке. Уважаем частные территории и правила фото; это не обещание встречи с гейко.',
   'Расходы заведений отдельно; прогулочный вход не заложен.','Gion Kyoto'),
 E('kyoto','arashiyama','Arashiyama / Bamboo Grove','Приоритет','D07 · 23 октября','1,5-2 ч в коротком варианте','умеренная',
   'Бамбуковая роща и прогулка по району Arashiyama. Природный контраст храмам и улицам предыдущего дня.',
   'Для восстановительного дня оставляем компактный круг, кафе и отдых. Не добавляем по умолчанию сады, храмы и ещё один удалённый район.',
   'Отдельный вход не заложен; выбранные платные зоны и дорога отдельно.','Arashiyama Bamboo Grove Kyoto'),
 E('kyoto','pontocho','Pontocho','По желанию','Вечер D07 · 23 октября','1-1,5 ч вместе с ужином','низкая',
   'Атмосферная ресторанная улица для вечернего завершения дня. Это прежде всего прогулка с ужином, а не дополнительная экскурсия.',
   'Оставляем по силам. Конкретное заведение, меню и возможность посадить шестерых выберем позже; бронирование не подразумевается.',
   'Ужин внутри категории питания, не добавляем второй раз.','Pontocho Kyoto'),
 E('kyoto','kinkakuji','Kinkaku-ji','Альтернатива','Вместо Arashiyama в D07','1-1,5 ч + дорога','умеренная',
   'Золотой павильон: ещё один яркий образ Киото. Хороший выбор, если архитектура и храмовый сад интереснее бамбуковой рощи.',
   'В текущем темпе это замена Arashiyama, а не обязательная вторая половина дня. Учитываем отдельную дорогу и часы закрытия.',
   'Исторический ориентир: '+money(1000)+' на двоих. Не тариф 2027.','Kinkaku-ji Kyoto'),
 E('osaka','dotonbori,namba','Dotonbori + Namba','Приоритет','D08 · 24 октября','1,5-2 ч с ужином','умеренная',
   'Вечерняя Осака: яркие вывески, городской шум и еда. Namba - связующий район, Dotonbori - центр выбранного вечернего впечатления.',
   'Один блок после заселения, не две прогулки подряд. Если устанем после переезда, сокращаем круг, но оставляем спокойный ужин.',
   'Еда внутри питания; покупки и отдельные заведения по факту.','Dotonbori Namba Osaka'),
 E('osaka','kuromon','Kuromon Market','Приоритет','D09 · 25 октября','1-1,5 ч с едой','низкая-умеренная',
   'Рынок для прогулки и еды небольшими порциями. Хорошо соответствует свободному городскому дню перед возвращением домой.',
   'Основной лёгкий блок D09. D10 - лишь запасной вариант при подходящем времени рейса; специально возвращаться дважды не нужно.',
   'Еда внутри питания, не отдельная категория входных билетов.','Kuromon Market Osaka'),
 E('osaka','castle','Osaka Castle','По силам','D08 · 24 октября','1,5-2,5 ч','умеренная',
   'Замок и окружающий парк. Можно выбрать наружную прогулку либо посещение музея внутри; это разные по времени и впечатлению варианты.',
   'После переезда только по силам. Если музей неинтересен, не покупаем билет ради галочки; Shinsekai может заменить этот блок.',
   'Музей: исторически '+money(2400)+' на двоих. Не переносим эту цену на прогулку по парку.','Osaka Castle Japan'),
 E('osaka','shinsekai','Shinsekai','Альтернатива','Вместо замка в D08','1-1,5 ч','умеренная',
   'Район с ретро-атмосферой и городскими вывесками. Больше подойдёт для улиц и еды, чем для музейного посещения.',
   'Выбираем вместо замка, если хочется ещё городской Осаки. Платные объекты внутри района не считаем включёнными автоматически.',
   'Платные объекты, еда и покупки отдельно; точные суммы не оценены.','Shinsekai Osaka'),
 E('osaka','umeda-sky','Umeda Sky Building','По желанию','D09 · 25 октября','1-1,5 ч + дорога','умеренная',
   'Смотровая с панорамой Осаки. Вариант на завершение поездки, если после Токио ещё хочется посмотреть на город сверху.',
   'Не обязательна, особенно если уже выбрана Shibuya Sky или Skytree. Добавляем только с запасом на дорогу и сбор багажа вечером.',
   'Исторический ориентир: '+money(4000)+' на двоих. Не тариф 2027.','Umeda Sky Building Osaka'),
 E('osaka','usj','Universal Studios Japan','Полная замена дня','Вместо городского D09','целый день','высокая',
   'Большой тематический парк аттракционов и шоу с мирами Nintendo, Harry Potter и другими. Это не JoJo-парк; будущие аниме-коллаборации не обещаем.',
   'Выбирать, если действительно нравятся аттракционы. Заменяет весь городской день, требует пересчёта нагрузки, билетов и бюджета. Низкое место в топе - из-за формата маршрута.',
   'Не включён в смету: YEN - уточнить / RUB - уточнить. Нужный набор билетов ещё не выбран.','Universal Studios Japan Osaka'),
]

CITY={
 'tokyo':dict(name='Токио',n=13,blocks=11,days='17-20 октября · 3 ночи',intro='JoJo и аниме - в центре плана. Остальное выбираем вокруг двух полных городских дней.',pages=[[0,1,2],[3,4,5],[6,7,8],[9,10]],page=2),
 'fuji':dict(name='Кавагутико / Фудзи',n=4,blocks=4,days='20-21 октября · 1 ночь',intro='Цель - увидеть гору и побыть у озера. Четыре кандидата не означают четыре обязательных выезда.',pages=[[0,1],[2,3]],page=6),
 'kyoto':dict(name='Киото',n=7,blocks=6,days='21-24 октября · 3 ночи',intro='Фусими Инари обязательно. В остальные часы балансируем старые улицы, природу и отдых.',pages=[[0,1,2],[3,4,5]],page=8),
 'osaka':dict(name='Осака',n=7,blocks=6,days='24-26 октября · 2 ночи',intro='Еда, вечерний город и свободное время. USJ - отдельное решение на целый день.',pages=[[0,1,2],[3,4,5]],page=10),
}
for city in CITY:
 for rank,item in enumerate([x for x in ENTRIES if x['city']==city],1): item['rank']=rank
allfiles=[f for x in ENTRIES for f in x['files']]
actual={str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'places').rglob('*.md') if p.name!='README.md'}
assert len(ENTRIES)==27 and len(allfiles)==31 and len(set(allfiles))==31
assert set(allfiles)==actual, (set(allfiles)^actual)
for x in ENTRIES:
 x['source_titles']=[(ROOT/f).read_text(encoding='utf-8-sig').splitlines()[0][2:] for f in x['files']]
 x['map_url']='https://www.google.com/maps/search/?'+urlencode({'api':'1','query':x['query']})
(Path(__file__).parent/'catalog.json').write_text(json.dumps(ENTRIES,ensure_ascii=False,indent=2),encoding='utf-8')

for name,fn in [('A','arial.ttf'),('AB','arialbd.ttf'),('AI','ariali.ttf')]:
 pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/fn)))
pdfmetrics.registerFontFamily('A',normal='A',bold='AB',italic='AI',boldItalic='AB')
W,H=A4; M=42; CW=W-2*M; MIN_Y=55
INK=HexColor('#263C36'); RED=HexColor('#AD483F'); MUTED=HexColor('#68756F'); BG=HexColor('#FAF7F0'); LINE=HexColor('#DCDDD3'); PALE=HexColor('#EEF1E9')
C=canvas.Canvas(str(OUT),pagesize=A4,pageCompression=1)
C.setTitle('Япония 2027 | Полный топ мест-кандидатов')
C.setAuthor('План поездки')
C.setSubject('31 кандидат проекта, 27 блоков, 4 базы. Рейтинг для первой поездки на 10 дней. Версия 26.08.2026.')
PAGE=0; TOTAL=12; BOXES=[]; TEXT=[]; SEEN=[]
def norm(s):
 s=str(s).replace('★',' ').replace('\u2011','-').replace('\u2013','-').replace('\u2014','-').replace('\u2212','-')
 s=re.sub(r'(?<=\d) (?=\d{3}(?:\D|$))','\u00a0',s)
 return re.sub(r'(?<=\d) (?=(?:YEN|RUB)\b)','\u00a0',s)
def style(size=10.5,bold=False,color=INK,leading=None):
 return ParagraphStyle('p',fontName='AB' if bold else 'A',fontSize=size,leading=leading or size*1.34,textColor=color,allowWidows=0,allowOrphans=0)
def measure(s,w,size=10.5,bold=False,color=INK,leading=None):
 p=Paragraph(norm(s),style(size,bold,color,leading)); _,h=p.wrap(w,H); return p,h
def para(s,x,y,w,size=10.5,bold=False,color=INK,leading=None):
 p,h=measure(s,w,size,bold,color,leading)
 assert y-h>=MIN_Y-0.1, f'Page{PAGE} overflow {y-h}: {s[:80]}'
 p.drawOn(C,x,y-h); BOXES.append([PAGE,x,y-h,w,h]); TEXT.append(norm(s)); return y-h
def newpage(chapter,title,sub='',anchor=None):
 global PAGE
 if PAGE:C.showPage()
 PAGE+=1
 C.setFillColor(BG);C.rect(0,0,W,H,fill=1,stroke=0)
 C.setStrokeColor(LINE);C.line(M,43,W-M,43)
 C.setFillColor(MUTED);C.setFont('A',8);C.drawString(M,28,'Япония 2027 | Каталог кандидатов | 26.08.2026');C.drawRightString(W-M,28,f'{PAGE} / {TOTAL}')
 C.setFillColor(RED);C.setFont('AB',9);C.drawString(M,H-38,norm(chapter).upper())
 if anchor:C.bookmarkPage(anchor);C.addOutlineEntry(title,anchor,level=0,closed=False)
 y=para(title,M,H-67,CW,25,True,leading=30)
 if sub:y=para(sub,M,y-8,CW,10.1,color=MUTED,leading=13.5)
 return y-18
def note(s,y):
 _,h=measure(s,CW-24,10.2,leading=14)
 assert y-h-22>=MIN_Y
 C.setFillColor(PALE);C.roundRect(M,y-h-22,CW,h+22,8,fill=1,stroke=0)
 para(s,M+12,y-11,CW-24,10.2,leading=14)
 return y-h-35
def table(headers,rows,widths,y,size=10):
 data=[[Paragraph(norm(v),style(size,True,white)) for v in headers]]+[[Paragraph(norm(v),style(size)) for v in row] for row in rows]
 t=Table(data,colWidths=widths)
 st=[('BACKGROUND',(0,0),(-1,0),INK),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]
 for i in range(1,len(data)):st+=[('BACKGROUND',(0,i),(-1,i),white if i%2 else PALE),('LINEBELOW',(0,i),(-1,i),0.4,LINE)]
 t.setStyle(TableStyle(st));tw,th=t.wrap(CW,H);assert y-th>=MIN_Y
 t.drawOn(C,M,y-th);BOXES.append([PAGE,M,y-th,tw,th]);TEXT.extend(str(v) for r in rows for v in r);return y-th-17
def card(x,y,compact=False):
 size=9.5 if compact else 10.3; lead=12.6 if compact else 14
 title_size=12.1 if compact else 13.2; width=CW-28
 title=x['title'];meta=x['tier'].upper()+' · '+x['when']
 lines=[('<b>Что это и зачем.</b> '+html.escape(x['why']),size,INK),('<b>В нашем плане.</b> '+html.escape(x['fit']),size,INK),('<b>Расходы.</b> '+html.escape(x['cost']),size-0.4,MUTED)]
 _,th=measure(title,CW-64,title_size,True,leading=16)
 _,mh=measure(meta,CW-64,8.4,True,RED,11)
 time='<b>Время:</b> '+x['time']+' · <b>Нагрузка:</b> '+x['load']
 _,dh=measure(time,width,9.1,leading=12)
 h=12+th+3+mh+8+dh+8
 for txt,sz,col in lines:h+=measure(txt,width,sz,color=col,leading=lead)[1]+6
 h+=17
 assert y-h>=MIN_Y, f'Card{title} p{PAGE} overflow {y-h}, h={h}'
 C.setFillColor(white);C.setStrokeColor(LINE);C.roundRect(M,y-h,CW,h,9,fill=1,stroke=1)
 C.setFillColor(RED if x['tier']=='Обязательно' else INK);C.circle(M+22,y-24,12,fill=1,stroke=0)
 C.setFillColor(white);C.setFont('AB',9.5);C.drawCentredString(M+22,y-27,str(x['rank']).zfill(2))
 yy=para(title,M+44,y-12,CW-58,title_size,True,leading=16)
 yy=para(meta,M+44,yy-3,CW-58,8.4,True,RED,11)-8
 yy=para(time,M+14,yy,width,9.1,leading=12)-8
 for txt,sz,col in lines:yy=para(txt,M+14,yy,width,sz,color=col,leading=lead)-6
 link='<link href="'+html.escape(x['map_url'],quote=True)+'" color="#AD483F">Открыть на карте</link>'
 para(link,M+14,yy,width,8.5,color=RED,leading=11)
 SEEN.extend(x['files']);return y-h-12

# 1. Обложка и навигация.
y=newpage('Полный список проекта','Куда мы хотим в Японии','Топ мест-кандидатов для первой поездки вдвоём в составе компании.',anchor='start')
C.setFillColor(RED);C.circle(W-M-35,y-32,26,fill=1,stroke=0)
y=para('31 место-кандидат<br/><font color="#AD483F">27 блоков · 4 базы</font>',M,y,CW-90,23,True,leading=31)-20
y=para('Все места из текущего каталога включены. Связанные пары объединены: <b>JoJo + IGGY CAFE</b>, <b>Asakusa + Senso-ji</b>, <b>Kiyomizu + Higashiyama</b>, <b>Dotonbori + Namba</b>. Ничего не нужно посещать только ради полноты списка.',M,y,CW,11)-18
y=table(['Город / база','Кандидатов','Раздел'],[
 ['Токио','13 · 11 блоков','<link href="#tokyo" color="#AD483F">Страницы 2-5</link>'],
 ['Кавагутико / Фудзи','4 · 4 блока','<link href="#fuji" color="#AD483F">Страницы 6-7</link>'],
 ['Киото','7 · 6 блоков','<link href="#kyoto" color="#AD483F">Страницы 8-9</link>'],
 ['Осака','7 · 6 блоков','<link href="#osaka" color="#AD483F">Страницы 10-11</link>'],
 ['Как выбирать и что перепроверить','','<link href="#choice" color="#AD483F">Страница 12</link>']],[CW*.44,CW*.25,CW*.31],y)
y=note('<b>Как устроен топ.</b> Номер - предложенный приоритет внутри города именно для вас: JoJo и аниме, впечатления первой поездки, удобство маршрута и умеренная ходьба. Это не рейтинг качества мест и не порядок посещения.',y)
y=para('<b>Обязательно:</b> THE JOJO WORLD с IGGY CAFE и Fushimi Inari. <b>Приоритет:</b> основа для обсуждения. <b>По желанию / по силам:</b> необязательное дополнение. <b>Альтернатива / резерв:</b> замена, а не ещё один пункт сверху.',M,y,CW,10.4)-15
y=para('<b>Даты пока примерные:</b> 17-26 октября 2027, 10 дней в Японии. Отели и билеты не выбраны; общий маршрут всех шести человек ещё не утверждён. Нумерация D01-D10 соответствует обзорному плану.',M,y,CW,10.4)-13
y=para('<b>Все суммы на двоих, YEN / RUB.</b> Условный курс 1 YEN = 0,53 RUB. Цены из прежних карточек - ориентиры, не тарифы 2027. Неизвестная цена не означает бесплатный вход. Время и нагрузка - наши оценки; дорога и очереди добавляются, если не указаны внутри.',M,y,CW,9.7,color=MUTED,leading=13)

# 2-10. Рейтинг по городам.
for city,info in CITY.items():
 entries=[x for x in ENTRIES if x['city']==city]
 for part,indices in enumerate(info['pages']):
  title=info['name'] if part==0 else info['name']+' · продолжение'
  sub=info['days']+' | '+info['intro']
  count_label=str(len(entries))+(' блока' if len(entries)==4 else ' блоков')
  y=newpage('Топ по городам · '+count_label,title,sub,anchor=city if part==0 else None)
  for idx in indices:y=card(entries[idx],y)
  if city=='tokyo' and part==3:
   y=note('<b>Наш выбор для Токио.</b> Сначала JoJo + IGGY CAFE и Akihabara. Для первого знакомства - Asakusa + Senso-ji, короткие Meiji и Shibuya. Затем выбираем, хочется ли одной смотровой или teamLab. Заполнять всё свободное время кандидатами не нужно.',y)
   y=para('Обычный D02: Asakusa + Senso-ji и Akihabara.<br/>D03: Meiji <i>или</i> Harajuku, затем JoJo + IGGY CAFE и Shibuya. Sky - только при желании и запасе времени.',M,y,CW,10.4)
  elif city=='fuji' and part==0:
   y=note('<b>Один пейзаж, несколько способов увидеть.</b> Oishi Park - конкретная точка у того же озера. Утренний короткий выход у ночёвки дополняет вечернюю прогулку, но не требует ещё одной большой экскурсии.',y)
  elif city=='fuji' and part==1:
   y=note('<b>Сначала надёжный переезд.</b> В D05 едем через Mishima в Киото. Любой подъём утром выбираем только после расчёта дороги, возврата за багажом и запаса на автобус. Если времени мало, остаёмся у озера.',y)
  elif city=='kyoto' and part==1:
   y=note('<b>Защищаем лёгкий день.</b> После полного подъёма в Inari выбираем на следующий день только один основной район: Arashiyama <i>или</i> Kinkaku-ji. Pontocho - ужин по желанию, а не ещё одна обязательная прогулка.',y)
  elif city=='osaka' and part==1:
   y=note('<b>Главная развилка Осаки.</b> Городской D09: Kuromon, покупки, отдых и возможная смотровая. USJ: целый день парка вместо этого набора. Второй вариант выбираем осознанно, а не потому, что любим аниме.',y)

# 11. Решения без перегруза и происхождение данных.
y=newpage('Выбор мест','Как собрать из топа нашу поездку','Каталог помогает выбирать. Он не заменяет утверждённый маршрут, билеты или расписание.',anchor='choice')
y=table(['Что хотим','Предпочтительный выбор','Одна замена'],[
 ['Аниме и JoJo','THE JOJO WORLD + IGGY CAFE; Akihabara','Обязательный JoJo не заменяем'],
 ['Старый Токио или визуальное свидание','Asakusa + Senso-ji','teamLab Borderless вместо блока'],
 ['Утро перед JoJo','Meiji Jingu','Harajuku'],
 ['Токио сверху','Shibuya Sky по желанию','Tokyo Skytree'],
 ['Фудзи без гонки','Озеро + Oishi Park','Ropeway вместо Oishi'],
 ['Утро перед Киото','Короткий берег у ночёвки','Chureito при запасе времени'],
 ['После короткого Inari','Kiyomizu + Higashiyama','Короткий Gion'],
 ['Спокойный день Киото','Компактная Arashiyama','Kinkaku-ji'],
 ['После переезда в Осаку','Osaka Castle по силам','Shinsekai'],
 ['Последний полный день','Kuromon, отдых, покупки','USJ вместо всего дня'],
 ],[CW*.30,CW*.36,CW*.34],y,size=9.3)
y=note('<b>Три правила.</b> Одна основная активность за полдня. Связанные районы считаем единым блоком. После тяжёлого пешего дня следующий облегчаем. Ни один номер в топе не обязывает покупать билет.',y)
y=para('<b>До утверждения:</b> выбираем места вместе; затем проверяем часы и доступ на нужные даты, цены, окна продажи, оплату, отмены и посадку шестерых. Для уличных видов оставляем погодный резерв. Неизвестные расходы не обнуляем.',M,y,CW,10.1)-13
y=para('<b>Основа версии.</b> Каталог из 31 карточки, текущие дни D01-D10 и ответы пользователя на 26.08.2026. Этот PDF - полный срез существующих кандидатов; новые города и места не добавлены. Приоритеты, длительности и нагрузка - планировочные оценки. Исторические цены не перепроверялись при экспорте.',M,y,CW,9.5,color=MUTED,leading=12.6)-12
y=para('<b>Официальные страницы из проверок проекта:</b> '
 '<link href="https://bandainamco-am.co.jp/official_shop/jojo/tokyo/" color="#AD483F">THE JOJO WORLD</link> · '
 '<link href="https://bandainamco-am.co.jp/official_shop/jojo/tokyo/cafe/" color="#AD483F">IGGY CAFE</link> · '
 '<link href="https://inari.jp/en/access/" color="#AD483F">Fushimi Inari</link> · '
 '<link href="https://www.teamlab.art/e/tokyo/" color="#AD483F">teamLab Borderless</link> · '
 '<link href="https://www.usj.co.jp/web/en/us/areas" color="#AD483F">USJ</link>. '
 'Ссылки «Открыть на карте» ведут на поиск по названию, не на проверенный вход или маршрут от отеля.',M,y,CW,9.3,color=MUTED,leading=12.4)

assert PAGE==TOTAL
assert len(SEEN)==31 and set(SEEN)==actual
C.save()
reader=PdfReader(OUT)
assert len(reader.pages)==TOTAL
text='\n'.join(p.extract_text() for p in reader.pages).replace('\u00a0',' ')
assert '\ufffd' not in text
map_links=[a.get_object().get('/A',{}).get('/URI','') for p in reader.pages for a in p.get('/Annots',[]) if 'google.com/maps/search' in str(a.get_object().get('/A',{}).get('/URI',''))]
assert len(map_links)==27
flat_text=re.sub(r'\s+',' ',text)
for x in ENTRIES:
 assert norm(x['title']).replace('\u00a0',' ') in flat_text, x['title']
(QA/'extracted.txt').write_text(text,encoding='utf-8')
(QA/'layout-boxes.json').write_text(json.dumps(BOXES),encoding='utf-8')
(Path(__file__).parent/'catalog.md').write_text('# Полный топ мест-кандидатов\n\n'+ '\n\n'.join('## '+CITY[x['city']]['name']+' / '+str(x['rank'])+'. '+x['title']+'\n\n'+x['tier']+' | '+x['when']+' | '+x['time']+' | Нагрузка: '+x['load']+'\n\n'+x['why']+'\n\n'+x['fit']+'\n\nРасходы на двоих: '+x['cost']+'\n\nКарточки: '+', '.join(x['files']) for x in ENTRIES)+'\n',encoding='utf-8')
print(f'PASS: {PAGE} pages, {len(ENTRIES)} ranked blocks, {len(SEEN)} source cards, {OUT.stat().st_size} bytes.\n{OUT}')
