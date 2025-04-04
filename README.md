# TradeOasis
O nama

Projektanti: Jagor Obad i Matej Toth, XV. gimnazija

Kontakt:
Jagor Obad - jagor.obad@gmail.com
Matej Toth - matej.toth021@gmail.com 

Naš cilj

Naš cilj je povećati broj Hrvata koji su iskusni u investiranju. Da bi ekonomija prosperirala, ljudi moraju znati kako pametno iskoristiti svoj novac. Ako zainteresiramo ljude za ulaganje u dionice, možda se odluče na kupovanje dionica na hrvatskoj (zagrebačkoj) burzi i tako potaknu razvoj domaćeg gospodarstva.

O projektu

TradeOasis je online platforma koja korisnicima omogućuje investiranje s virtualnim novcem te obrazovanje o temama dionica i slično. Budući da se investiranje obavlja virtualnim novcem, korisnik ne preuzima nikakav rizik, već ulaže radi vježbanja.

Lokalno pokretanje programa:

Prije svega potrebno je instalirati Python, preporučena je verzija 3.13.2. Također je potrebno instalirati pip (python sustav za upravljanje paketima, preporučena verzija je 25.0.1) pokretanjem komande:

python get-pip.py

Da biste lokalno pokrenuli program potrebno je u glavni folder aplikacije dodati virtualno okružje (tzv. virtual environment) koje omogućuje da svi vanjski programi budu instalirani u pravilnoj inačici. Za otvaranje virtualnog okružja u terminalu pokrenite komandu:

python -m venv venv

Zatim aktivirajte virtualno okružje pokretanjem komande:

venv\Scripts\activate

Da biste instalirali sve potrebne vanjske programe, pokrenite komandu:

pip install -r requirements.txt

Prije pokretanja, važno je migrirati bazu podataka:

python manage.py migrate

Na kraju da biste pokrenuli aplikaciju, pokrenite komandu:

python manage.py runserver

Ako adresu iz terminala pokrenete na svojem web pregledniku, trebali biste vidjeti početnu stranicu TradeOasisa.

Napomena: resetiranje lozinke nije moguće u lokalnoj inačici programa