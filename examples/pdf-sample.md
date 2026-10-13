# Provera PDF izvoza

Ovaj dokument prikazuje sadržaj koji se direktno iz Markdown izvora objavljuje
u PDF. Fontovi su ugrađeni u dokument, a tekst može da se selektuje i kopira.
Srpska latinica: Čćšžđ. Ћирилица: Извештај о објављивању.

## Formatiranje teksta

Običan tekst sa **podebljanim delom**, *kurzivom*, ***kombinovanim stilom***
i `kodom u redu`. [Primer bezbednog linka](https://example.com?q=1&b=2)
ostaje aktivan. ![**Opis** slike](https://example.com/image.png) ostaje tekst.

## Liste i citati

- Prva stavka
  - Ugnježdena stavka
  - Druga ugnježdena stavka
- Druga stavka

3. Treći korak
4. Četvrti korak

Zasebna lista:

1. Novi prvi korak
2. Novi drugi korak

> Izvorni tekst ostaje sačuvan, uključujući dijakritike i ćirilicu.
>
> PDF se izrađuje bez preuzimanja slika i bez izvršavanja skripti iz izvora.

## Primer koda

```python
poruke = ["Zdravo", "Здраво"]
for poruka in poruke:
    print(poruka)
```

### Naslov sa *kurzivom*

Naslov iz komande postavlja svojstvo PDF dokumenta. Vidljivi naslovi dolaze iz
Markdown izvora. Jezik se čuva u PDF metapodacima.

## *Duži dokumenti*

A4 stranice koriste margine od 2,5 cm. Pasusi i kod prelaze na novu stranicu kada
je potrebno; dugi redovi koda prelamaju se unutar margina. Izlaz se prepisuje
samo uz izričitu opciju, a greška čuva prethodni fajl.
