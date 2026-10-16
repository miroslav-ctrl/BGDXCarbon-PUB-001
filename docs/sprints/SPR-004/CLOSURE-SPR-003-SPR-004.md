# SPR-003 i SPR-004 — završna evidencija

Datum provere: 16. oktobar 2026. Repozitorijum: miroslav-ctrl/BGDXCarbon-PUB-001.
Verifikovani develop: `62637f56dbbdc0f45996688f79c5ae5d4796f415`.
PR #19 je merged u develop kao `8d7ed307ef141a9967b2b6cb0baa2ce68e61b5ba`; trenutni develop uključuje i PR #20.

## Odluka

SPR-003: post-merge verifikacija tri Copilot nalaza je PASS; preporučuje se formalno zatvaranje tog obima.

SPR-004: automatizovani i browser acceptance su PASS. Preporučuje se formalno zatvaranje acceptance obima. Nije utvrđen funkcionalni nedostatak koji zahteva korektivni kod.

Evidencija je pripremljena za dokumentacioni PR prema develop. Statusi GitHub issues nisu menjani; merge i izmene main grane nisu izvršeni.

## SPR-003 dokazi

| Nalaz | Implementacija | Regresioni dokaz |
| --- | --- | --- |
| Immutable JobLifecycle transition pravila | src/bgdxpublisher/jobs/lifecycle.py:15–24, MappingProxyType i frozenset vrednosti | tests/jobs/test_jobs.py:41–60; zabrana izmene i brisanja mapping unosa i mutacije vrednosti |
| Callable execute validacija u konstruktoru | src/bgdxpublisher/pipeline/engine.py:34–37; PipelineDefinitionError | tests/pipeline/test_engine.py:246–266; nedostajući execute, None, broj i string |
| Zasebni pragovi coverage >=95% | .github/workflows/ci.yml:43–48; tri odvojena pytest poziva | Domain 100%, jobs 100%, pipeline 100% u CI |

## SPR-004 acceptance matrica

| Zahtev | Rezultat | Dokaz |
| --- | --- | --- |
| Podrazumevani naslov je stem izvornog fajla; jezik und | PASS | tests/publishing/test_metadata.py:62–90 |
| --title i --lang stižu do HTML metapodataka | PASS | isti CLI test; naslov Izveštaj & pregled i sr-Latn |
| Unicode naslov i HTML escaping | PASS | test_language_and_escaped_title, linija 17; title zatvaranje, script markup, &, navodnici |
| Markdown heading ostaje nepromenjen | PASS | testovi potvrđuju Body/Heading nezavisno od naslova |
| Jezik, script, region i varijante | PASS | osam validnih primera: und, sr, sr-Latn, sr-Cyrl-RS, en-US, es-419, sl-rozaj, de-CH-1901 |
| Nevalidni metapodaci na service ulazu | PASS | 13 kombinacija u test_invalid_metadata_preserves_existing_output, linija 46; PublishingError, nepromenjen izvor i postojeći izlaz, bez privremenih fajlova |
| Nevalidni CLI metapodaci | PASS | šest slučajeva u test_cli_rejects_invalid_metadata_before_publication, linija 103; exit 2, precizna dijagnostika, izlaz nije kreiran |
| Duplirane jezičke varijante | PASS | de-CH-1901-1901 i sl-rozaj-ROZAJ odbijeni bez obzira na case |
| Instalirani wheel izvan repozitorijuma | PASS | CI korak Test installed wheel outside repository: Report & review escaped u title, sr-Latn u html lang; en_US vraća 2 i čuva prethodne izlazne bajtove |
| Browser tab naslov i HTML lang u browseru | PASS | 16.10.2026, Codex In-app Browser; stvarni custom.html: title Izveštaj, lang sr-Latn, heading Izvorni naslov i telo Čćžšđ — Ћирилица. |

Validacija je u src/bgdxpublisher/publishing/metadata.py:13–35; renderer u renderer.py:82–83 poziva validatore, a renderer.py:117–126 gradi escaped HTML head. CLI app.py povezuje opcije sa validatorima. Jezički ugovor je dokumentovani podskup BCP 47, bez registry lookup-a.

## CI rezultati

- [Merge PR #19, run 38371486773](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/38371486773): success.
- [Trenutni develop, run 38523978210](https://github.com/miroslav-ctrl/BGDXCarbon-PUB-001/actions/runs/38523978210): success.
- Oba run-a imaju četiri uspešne quality kombinacije: Ubuntu i Windows, Python 3.13 i 3.14; Tests, Ruff, Black, MyPy, Coverage, tri package coverage koraka, build wheel i installed-wheel test su uspešni.
- Pregledani Ubuntu/Python 3.13 logovi oba run-a: 301 passed; ukupni coverage 99,88%; domain 17 passed / 100%; jobs 20 passed / 100%; pipeline 18 passed / 100%.
- Log job-a 115719889361 eksplicitno potvrđuje 28 prolaznih slučajeva u tests/publishing/test_metadata.py, i u običnom i u coverage test prolazu.

## Lokalni Python 3.13 i browser acceptance

Python 3.13.9 Windows x64 prenosivi runtime preuzet je sa zvaničnog python.org izvora. Iz source kopije develop 62637f56 izgrađen je i instaliran wheel bgdxpublisher 1.1.0; acceptance skripta izvršena je izvan repozitorijuma, nad instaliranim paketom. Izvorni runtime kod nije menjan.

Lokalna komanda `python -m pytest tests/publishing/test_metadata.py -q --basetemp=../pytest-temp-approved --tb=short` završena je sa **28 passed in 0.60s**. Prethodni sandbox pokušaji imali su filesystem permission greške; ponavljanje van sandbox-a prolazi.

Browser: Codex In-app Browser, provereno 16.10.2026; alat ne izlaže broj verzije browsera. Stvarni generisani HTML poslužen je preko privremenog servera vezanog za 127.0.0.1. Vizuelni pregled i read-only DOM pregled potvrđuju:

| Fajl | Naslov taba / document.title | html lang | Telo |
| --- | --- | --- | --- |
| default.html | document | und | Izvorni naslov; Čćžšđ — Ћирилица. |
| custom.html | Izveštaj | sr-Latn | identično |
| escaped.html | Izveštaj & <pregled> | sr-Cyrl-RS | identično; bez script elemenata |

CLI je odbio en_US sa exit kodom 2 i sačuvao postojeće izlazne bajtove; source bajtovi su nepromenjeni. SHA-256 custom.html: `69bab63eed24ac52c3ff89ed460f116d6c4d394d742be92fe38bccdb685d6c16`.

Reprodukcija: kreirati document.md sa heading-om Izvorni naslov i telom Čćžšđ — Ћирилица., zatim pokrenuti `bgdxpublisher publish document.md --output custom.html --title "Izveštaj" --lang sr-Latn`. Otvoriti custom.html; proveriti title i html lang. Ponoviti bez opcija i sa naslovom `Izveštaj & <pregled>` i jezikom sr-Cyrl-RS.

Istorijska stavka Review completed before merge ostaje neoznačena: post-merge acceptance ne dokazuje tadašnji pregled. Ovaj zapis potvrđuje sadašnje acceptance stanje.

SPR-004 već postoji kao HTML Document Metadata, ranije implementiran kroz PR #10. Novi pipeline obim treba planirati pod sledećom slobodnom sprint oznakom.

## Predlog završnog zapisa

SPR-003: tri prijavljena Copilot nalaza potvrđeno rešena na develop 62637f56; post-merge CI na 8d7ed307 i aktuelni CI su uspešni. Preporuka: zatvoriti post-merge verifikaciju.

SPR-004: 28 metadata testova lokalno prolazi na Python 3.13.9; postojeći CI i installed-wheel provere prolaze. Browser acceptance je završen i potvrđuje title, lang, escaping i očuvano telo. Preporuka: formalno zatvoriti acceptance obim.
