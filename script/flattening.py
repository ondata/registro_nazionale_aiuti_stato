import xmltodict
import polars as pl
import argparse
import sys
import os

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Convert XML aiuti file to Parquet')
    parser.add_argument('-i', '--input', required=True, help='Input XML file path')
    parser.add_argument('-of', '--output-folder', help='Output folder for parquet files (optional)')
    args = parser.parse_args()

    # Normalizza il path e verifica esistenza file
    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print(f"Error: File {input_path} not found")
        sys.exit(1)

    # Determina cartella output
    output_dir = args.output_folder if args.output_folder else os.path.dirname(input_path)
    output_dir = os.path.abspath(output_dir)

    # Crea cartella output se non esiste
    os.makedirs(output_dir, exist_ok=True)

    # Genera nomi file output
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    aiuti_parquet = os.path.join(output_dir, f"{base_name}_aiuti.parquet")
    componenti_parquet = os.path.join(output_dir, f"{base_name}_componenti.parquet")
    strumenti_parquet = os.path.join(output_dir, f"{base_name}_strumenti.parquet")

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

    # Estrai nome file senza estensione per campo source
    source_name = os.path.splitext(os.path.basename(input_path))[0]

    # Converti liste in DataFrame Polars con processing parallelo e aggiungi source
    df_aiuti = (pl.DataFrame(aiuto_records)
                .with_columns(pl.all().cast(pl.Utf8))
                .with_columns(pl.lit(source_name).alias("source")))

    df_componenti = (pl.DataFrame(componenti_records)
                    .with_columns(pl.all().cast(pl.Utf8))
                    .with_columns(pl.lit(source_name).alias("source")))

    df_strumenti = (pl.DataFrame(strumenti_records)
                   .with_columns(pl.all().cast(pl.Utf8))
                   .with_columns(pl.lit(source_name).alias("source")))

    # Salva in Parquet con compressione ottimizzata
    df_aiuti.write_parquet(
        aiuti_parquet,
        row_group_size=100000,
        compression="zstd",
        use_pyarrow=True
    )

    df_componenti.write_parquet(
        componenti_parquet,
        row_group_size=100000,
        compression="zstd",
        use_pyarrow=True
    )

    df_strumenti.write_parquet(
        strumenti_parquet,
        row_group_size=100000,
        compression="zstd",
        use_pyarrow=True
    )

if __name__ == "__main__":
    main()
