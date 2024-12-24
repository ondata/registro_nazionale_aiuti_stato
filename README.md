# Intro

## Note sugli XML

Alcuni file contengono caratteri non consentiti e mandano in errore vari *parser*.

Qualche test ha fatto emergere la necessità di rimuovere ad esempio `x02`, che è un carattere di controllo e che non è consentito in XML.
Ad esempio con `sed -i 's/\x02/ /g' OpenData_Aiuti_2022_05.xml` si rimuove il carattere e si rende il file leggibile.
