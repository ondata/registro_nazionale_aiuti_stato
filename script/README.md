# Script di Utilità

Questa cartella contiene script per il download e l'elaborazione dei dati del Registro Nazionale degli Aiuti di Stato (RNA).

## Panoramica degli Script

### rna_files_list.sh
Scarica l'elenco dei dataset disponibili dal portale open data dell'RNA e recupera:
- File di dati delle misure
- File di dati degli aiuti
Lo script crea la struttura delle directory necessaria e salva sia i file ZIP grezzi che gli elenchi JSON.

### misure_export.sh
Elabora i dati delle misure scaricati:
- Estrae i file XML dagli archivi ZIP
- Rimuove i caratteri non validi
- Converte in formato Parquet usando Python
- Crea file Parquet consolidati per diverse categorie di dati (strumenti, misure, settori, obiettivi, dotazioni, aree)

### aiuti_export.sh
Elabora i dati degli aiuti scaricati:
- Estrae i file XML dagli archivi ZIP
- Rimuove i caratteri non validi
- Converte in formato Parquet usando Python
- Genera file Parquet separati per aiuti, componenti e strumenti

### check_xml.sh
Valida i file XML negli archivi degli aiuti:
- Controlla la presenza di caratteri non validi (0x02, 0x10, 0x1A)
- Registra i file problematici
- Valida la struttura XML dopo la pulizia dei caratteri
