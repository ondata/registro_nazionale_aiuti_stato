# Intro

Analizzando l'HTML si vedono vari pezzi di codice legati a nomi file

```
span class="visually-hidden">OpenData_Misura_2025_12.xml nello ZIP personalizzato</span></label></div></td><td><!-- THEME DEBUG --><!-- THEME HOOK: 'views_view_field' --><!-- BEGIN OUTPUT from 'core/modules/views/templates/views-view-field.html.twig' --><a data-nid="2761" data-filename="OpenData_Misura_2025_12.xml" data-file-ext="xml" href="#" class="OpenDataXmlDownload table-tablejs__link-xml" data-focus-mouse="false">xml
      <span class="visually-hidden">OpenData_Misura_2025_12.xml</span></a><a data-nid="2761" data-filename="OpenData_Misura_2025_12.xml" data-file-ext="zip" href="#" class="OpenDataZipDownload table-tablejs__link-zip">zip
     <span class="visually-hidden">OpenData_Misura_2025_12.xml</span></a><!-- END OUTPUT from 'core/modules/views/templates/views-view-field.html.twig' --></td></tr><tr><th class="td" scope="row"><span aria-hidden="true" role="presentation" class="d-none">25-10-01</span>
                    Ottobre 2025
                                  </th><td><!-- THEME DEBUG --><!-- THEME HOOK: 'views_view_field' --><!-- BEGIN OUTPUT from 'core/modules/views/templates/views-view-field.html.twig' -->
OpenData_Misura_2025_10.xml
<!-- END OUTPUT from 'core/modules/views/templates/views-view-field.html.twig' --></td><td><div class="form-check form-check--trasparenza form-check--zip"><input id="checkboxz2850" data-nid="2850" type="checkbox"><label for="checkboxz2850" class="active">
                          Aggiungi
                          <span class="visually-hidden">OpenData_Misura_2025_10.xml nello ZIP personalizzato</span></label></div></td><td><!-- THEME DEBUG --><!-- THEME HOOK: 'views_view_field' --><!-- BEGIN OUTPUT from 'core/modules/views/templates/views-view-field.html.twig' --><a data-nid="2850" data-filename="OpenData_Misura_2025_10.xml" data-file-ext="xml" href="#" class="OpenDataXmlDownload table-tablejs__link-xml" data-focus-mouse="false">xml
      <span class="visually-hidden">OpenData_Misura_2025_10.xml</span></a><a data-nid="2850" data-filename="OpenData_Misura_2025_10.xml" data-file-ext="zip" href="#" class="OpenDataZipDownload table-tablejs__link-zip">zip
     <span class="visually-hidden">OpenData_Misura_2025_10.xml</span></a><!-- END OUTPUT from 'core/modules/views/templates/views-view-field.html.twig' --></td></tr><tr><th class="td" scope="row"><span aria-hidden="true" role="presentation" class="d-none">25-08-01</span>
                    Agosto 2025
                                  </th><td><!-- THEME DEBUG --><!-- THEME HOOK: 'views_view_field' --><!-- BEGIN OUTPUT from 'core/modules/views/templates/views-view-field.html.twig' -->
OpenData_Misura_2025_08.xml
```

Facendo click su uno dei buttoni di download degli zip, dagli strumenti di sviluppo si vede questa chiamata

```
curl 'https://www.rna.gov.it/opendata/misure-agevolative/download' \
  -H 'Accept: */*' \
  -H 'Accept-Language: it,en-US;q=0.9,en;q=0.8' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: 96c109206086521e6d079a6affe1a922=e86c1346b5cd366cdd8787ebf7710791; cookies_consent=true' \
  -H 'Origin: https://www.rna.gov.it' \
  -H 'Referer: https://www.rna.gov.it/open-data/misure-agevolative' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36' \
  -H 'X-Requested-With: XMLHttpRequest' \
  -H 'sec-ch-ua: "Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  --data-raw '{"nids":"2761","file_extension":"zip"}'
```

La parte interessante è `--data-raw '{"nids":"2761","file_extension":"zip"}'`, che richiama quello che si vede nell'HTML: `<a data-nid="2761" ...`.

Il comando semplificato è questo:

```
curl 'https://www.rna.gov.it/opendata/misure-agevolative/download' \
  -H 'Accept: */*' \
  -H 'Content-Type: application/json' \
  -H 'Origin: https://www.rna.gov.it' \
  -H 'Referer: https://www.rna.gov.it/open-data/misure-agevolative' \
  --data-raw '{"nids":"2685","file_extension":"zip"}'
```

Che restistuisce il path del file ZIP da scaricare:

```
{"content":"\/sites\/rna.mise.gov.it\/files\/opendata\/download_zips\/Opendata-4409c919f040e01300d802602a1c57ff4ded4d5aa5c5ea5f16cf11363f986463.zip"}
```

Lo scarico allora con:

```
curl -o file.zip 'https://www.rna.gov.it/sites/rna.mise.gov.it/files/opendata/download_zips/Opendata-d2cc2cd378a0cbf24293e9059fff3a2435ec802d01893fc38edf444fb9f4decc.zip'
```

L'elenco dei nid si può estrarre con

```
curl -kL "https://www.rna.gov.it/open-data/misure-agevolative" | scrape -be '//a[@data-nid]'
```
