import xmltodict
import pandas as pd
import argparse
import sys
import os

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Convert XML aiuti file to CSV')
    parser.add_argument('input_file', help='Input XML file path')
    args = parser.parse_args()

    # Normalizza il path e verifica esistenza file
    input_path = os.path.abspath(args.input_file)
    if not os.path.exists(input_path):
        print(f"Error: File {input_path} not found")
        sys.exit(1)

    # Genera i nomi file di output nella stessa directory del file di input
    output_dir = os.path.dirname(input_path)
    base_name = os.path.splitext(os.path.basename(input_path))[0]

    # Percorsi completi per i file CSV
    aiuti_csv = os.path.join(output_dir, f"{base_name}_aiuti.csv")
    componenti_csv = os.path.join(output_dir, f"{base_name}_componenti.csv")
    strumenti_csv = os.path.join(output_dir, f"{base_name}_strumenti.csv")

    # Legge il file XML
    with open(input_path, "r", encoding="utf-8") as file:
        data = xmltodict.parse(file.read())

    # Estrai il contenuto di LISTA_AIUTI
    aiuti = data.get("LISTA_AIUTI", {}).get("AIUTO", [])

    # Tabelle principali
    aiuto_records = []
    componenti_records = []
    strumenti_records = []

    for aiuto in aiuti:
        # Tabella AIUTO
        aiuto_base = {key: aiuto.get(key) for key in aiuto if key != "COMPONENTI_AIUTO"}
        aiuto_records.append(aiuto_base)

        # Tabella COMPONENTI_AIUTO
        componenti_aiuto = aiuto.get("COMPONENTI_AIUTO", {}).get("COMPONENTE_AIUTO", [])
        if isinstance(componenti_aiuto, dict):  # Gestione singolo componente
            componenti_aiuto = [componenti_aiuto]

        for componente in componenti_aiuto:
            # Rimuove STRUMENTI_AIUTO dalla tabella COMPONENTI
            componente_record = {key: componente.get(key) for key in componente if key != "STRUMENTI_AIUTO"}
            componente_record["CAR"] = aiuto.get("CAR")  # Chiave esterna verso AIUTO
            componenti_records.append(componente_record)

            # Tabella STRUMENTI_AIUTO
            strumenti_aiuto = componente.get("STRUMENTI_AIUTO", {}).get("STRUMENTO_AIUTO", [])
            if isinstance(strumenti_aiuto, dict):  # Gestione singolo strumento
                strumenti_aiuto = [strumenti_aiuto]

            for strumento in strumenti_aiuto:
                strumento["CAR"] = aiuto.get("CAR")
                strumento["ID_COMPONENTE"] = componente.get("ID_COMPONENTE")
                strumenti_records.append(strumento)

    # Salva i CSV nella stessa directory del file di input
    pd.DataFrame(aiuto_records).to_csv(aiuti_csv, index=False)
    pd.DataFrame(componenti_records).to_csv(componenti_csv, index=False)
    pd.DataFrame(strumenti_records).to_csv(strumenti_csv, index=False)

if __name__ == "__main__":
    main()
