# UI a UX návrh, Diamond Plus Revenue Intelligence

## Cíl

UI nemá vypadat jako další dashboard. Má rychle odpovědět na 4 otázky:

1. Jak si vede byznys doopravdy?
2. Co je měřená pravda a co je jen marketing claim?
3. Kde vzniká nový demand a kde jen sklízíme existující poptávku?
4. Co má management nebo marketing udělat hned?

## Doporučený informační model

### 1. Homepage = decision layer
Nahoře mají být jen tyto bloky:
- observed revenue
- after marketing
- measured new vs returning truth
- channel trust summary
- explicitní action panel

Homepage nemá začínat tabulkami. Má začínat významem.

### 2. Druhá vrstva = truth strips
Pod hero sekcí doporučuju 4 horizontální stripy:
- Business truth
- Customer truth
- Acquisition truth
- Measurement truth

Každý strip má mít:
- 1 headline větu
- 2 až 4 klíčové metriky
- 1 warning
- 1 CTA do detailu

### 3. Třetí vrstva = rozhodovací plochy
Samostatné stránky:
- Management
- Marketing
- Finance
- Channels
- Audit

Každá stránka má mít nahoře:
- co řešit teď
- co je jisté
- co je risk

## UX principy

### A. Claim versus truth musí být vždy vedle sebe
Nikdy neukazovat platform revenue samotné. Vždy vedle něj:
- observed revenue
- trust badge
- otázku, kterou to ještě neřeší

### B. Brand, remarketing, retention a acquisition nikdy nemíchat
Tohle je klíčové. Pokud se to smíchá, UI bude opticky hezké, ale rozhodovací logika bude špatně.

### C. Nejistotu neukrývat
Místo “one number fantasy” radši:
- measured
- estimated
- claimed
- missing

### D. Management readability nad analytickou exhibicí
Přednost mají:
- jasné věty
- krátké interpretace
- limit top 5 až top 8 řádků
- default collapsed detail

## Doporučené další UI komponenty

### 1. Truth badge system
Každý blok nebo metrika dostane badge:
- measured
- observed
- claimed
- modeled
- missing

### 2. Severity cards
Pro hlavní problémy:
- vysoký unattributed share
- Meta claim vs observed gap
- brand-heavy search
- repeat-heavy revenue dependence

Každá karta:
- problém
- proč je důležitý
- co s tím

### 3. Decision cards
Například:
- Scale carefully
- Protect efficiency
- Validate before trust
- Separate before budget change

### 4. Time-window labels
U každého většího bloku explicitně ukázat:
- last 7d
- previous full month
- YTD measured window

Bez toho vzniká falešné srovnání.

## Doporučený další frontend krok

1. Přidat sticky truth filter nahoře:
- All
- Business
- Customer
- Acquisition
- Measurement

2. Přidat compact / analyst mode toggle:
- Compact = management
- Analyst = detailní tabulky a více breakdownů

3. Přidat homepage decision rail vpravo:
- 3 nejdůležitější warnings
- 3 doporučené akce
- 1 status refresh info

## Co by produkt posunulo nad běžný dashboard

- explicitní decision logic místo jen metrik
- lokální business vocabulary místo agenturního jazyka
- oddělené truth layers
- audit-ready exporty
- jasné přiznání nejistoty tam, kde data nejsou finální

## Shrnutí

Nejlepší verze UI pro tenhle produkt je:
- nahoře stručná a rozhodovací
- uprostřed upřímná o nejistotě
- dole detailní pro operativu

Tím se dostaneme blíž k tomu, aby to nebyl jen interní dashboard, ale skutečný revenue operating system.
