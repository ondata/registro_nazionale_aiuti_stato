# Intro


## Note

### Note sugli XML

Alcuni file contengono caratteri non consentiti e mandano in errore vari *parser*.

Qualche test ha fatto emergere la necessità di rimuovere ad esempio `x02`, che è un carattere di controllo e che non è consentito in XML.
Ad esempio con `sed -i 's/\x02/ /g' OpenData_Aiuti_2022_05.xml` si rimuove il carattere e si rende il file leggibile.

L'elenco dei caratteri invalidi e dei file problematici è questo

|File|Carattere|
|---|---|
| OpenData_Aiuti_2019_01.xml | \x1A |
| OpenData_Aiuti_2019_03.xml | \x10 |
| OpenData_Aiuti_2019_04.xml | \x1A |
| OpenData_Aiuti_2019_05.xml | \x1A |
| OpenData_Aiuti_2021_07.xml | \x02 |
| OpenData_Aiuti_2021_09.xml | \x02 |
| OpenData_Aiuti_2021_12.xml | \x02 |
| OpenData_Aiuti_2021_12_002.xml | \x02 |
| OpenData_Aiuti_2022_02.xml | \x02 |
| OpenData_Aiuti_2022_03.xml | \x02 |
| OpenData_Aiuti_2022_04.xml | \x02 |
| OpenData_Aiuti_2022_05.xml | \x02 |
| OpenData_Aiuti_2022_06.xml | \x02 |
| OpenData_Aiuti_2022_07.xml | \x02 |
| OpenData_Aiuti_2022_09.xml | \x02 |
| OpenData_Aiuti_2022_11.xml | \x02 |
| OpenData_Aiuti_2022_12.xml | \x02 |
| OpenData_Aiuti_2023_01.xml | \x02 |
| OpenData_Aiuti_2023_02.xml | \x02 |
| OpenData_Aiuti_2023_03.xml | \x02 |
| OpenData_Aiuti_2023_04_003.xml | \x02 |
| OpenData_Aiuti_2023_05.xml | \x02 |
| OpenData_Aiuti_2023_05_005.xml | \x02 |
| OpenData_Aiuti_2023_05_006.xml | \x02 |
| OpenData_Aiuti_2023_05_007.xml | \x02 |
| OpenData_Aiuti_2023_06.xml | \x02 |
| OpenData_Aiuti_2023_07.xml | \x02 |
| OpenData_Aiuti_2023_08.xml | \x02 |
| OpenData_Aiuti_2023_10.xml | \x02 |
| OpenData_Aiuti_2023_11.xml | \x02 |
| OpenData_Aiuti_2023_12.xml | \x02 |
| OpenData_Aiuti_2024_06.xml | \x02 |
| OpenData_Aiuti_2024_07.xml | \x02 |
| OpenData_Aiuti_2024_08.xml | \x02 |
| OpenData_Aiuti_2024_10.xml | \x02 |
| OpenData_Aiuti_2024_12.xml | \x02 |

### Sui campi con nome utente e codice fiscale

L'[articolo 26 del CAD](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2013;033~art26) prevede esplicitamente l'obbligo di pubblicazione degli atti relativi alla concessione di sovvenzioni, contributi, sussidi e altri vantaggi economici da parte delle pubbliche amministrazioni, con l'obiettivo di garantire trasparenza e *accountability*.
