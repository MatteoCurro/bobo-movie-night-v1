# Bobo Movies Night

Ricerca film e serie con autocomplete, ID TMDB e player Vix.

La pagina pubblicata è disponibile su https://matteocurro.github.io/bobo-movie-night-v1/ dopo il completamento del workflow.

## Modifiche

Modifica index.html per aggiornare interfaccia e player. Ogni push su main rigenera e pubblica il sito.
update.py genera film.json, serie.json, stagioni.js e indice/ dai dati pubblici TMDB e CasaFlix, senza chiavi API.
I cataloghi generati vengono inclusi nel sito pubblicato. Il workflow li aggiorna ogni giorno alle 09:35 UTC e può essere avviato manualmente da Actions.

## Uso locale

Esegui python3 update.py e apri public/index.html. La ricerca funziona anche offline. Il player richiede Internet.
Il cambio automatico di stagione dipende dai conteggi episodi disponibili in CasaFlix. Per le altre serie è disponibile la selezione manuale.

I metadati completi e i titoli tradotti sono disponibili solo dove forniti dalle fonti. La disponibilità del player dipende da Vix.
