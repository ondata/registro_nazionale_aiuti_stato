import os
import argparse
import xmltodict
import json  # Aggiunto import mancante
import polars as pl
from pathlib import Path
from os.path import dirname

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Convert XML misure file to Parquet')
    parser.add_argument('-i', '--input', required=True, help='Input XML file path')
    parser.add_argument('-of', '--output-folder', help='Output folder for parquet files (optional)')
    args = parser.parse_args()

    # Aggiungi debug per il file input
    print(f"Lettura file: {args.input}")

    # Normalize path and check file existence
    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print(f"Error: File {input_path} not found")
        sys.exit(1)

    # Determine output directory
    output_dir = args.output_folder if args.output_folder else os.path.dirname(input_path)
    output_dir = os.path.abspath(output_dir)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate output file names
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    misure_parquet = os.path.join(output_dir, f"{base_name}_misure.parquet")
    settori_parquet = os.path.join(output_dir, f"{base_name}_settori.parquet")
    strumenti_parquet = os.path.join(output_dir, f"{base_name}_strumenti.parquet")
    obiettivi_parquet = os.path.join(output_dir, f"{base_name}_obiettivi.parquet")
    aree_parquet = os.path.join(output_dir, f"{base_name}_aree.parquet")
    dotazioni_parquet = os.path.join(output_dir, f"{base_name}_dotazioni.parquet")

    # Verifica contenuto XML
    with open(input_path, 'r', encoding="utf-8") as f:
        xml_content = f.read()
        print(f"Dimensione XML: {len(xml_content)} bytes")

    try:
        with open(input_path, "r", encoding="utf-8") as file:
            data = xmltodict.parse(file.read())

        print("DEBUG: Printing XML structure")
        print(json.dumps(data, indent=2)[:500])

        # Unico blocco di estrazione misure
        if "ns0:LISTA_MISURE_TYPE" in data:
            misure = data["ns0:LISTA_MISURE_TYPE"].get("MISURA", [])
        elif "LISTA_MISURE_TYPE" in data:
            misure = data["LISTA_MISURE_TYPE"].get("MISURA", [])
        elif "LISTA_MISURE" in data:
            misure = data["LISTA_MISURE"].get("MISURA", [])
        else:
            print("ERRORE: Struttura XML non riconosciuta")
            print("Chiavi disponibili:", list(data.keys()))
            return

        # Forza lista se la misura è singola
        if isinstance(misure, dict):
            misure = [misure]

        print(f"Struttura dati misure: {type(misure)}")
        print(f"Numero effettivo misure: {len(misure)}")
        if len(misure) == 0:
            print("ATTENZIONE: Nessuna misura trovata nel file XML")
            return

    except json.JSONDecodeError as e:
        print(f"Errore nel parsing JSON: {e}")
        return
    except Exception as e:
        print(f"Errore generico: {e}")
        return

    # Aggiungiamo controlli di debug
    print(f"Numero di misure processate: {len(misure)}")

    # Main tables
    misura_records = []
    settori_records = []
    strumenti_records = []
    obiettivi_records = []
    aree_records = []
    dotazioni_records = []

    for misura in misure:
        # Debug per ogni misura
        print(f"Processando CAR: {misura.get('CAR')}")

        # MISURA table - all first level fields
        misura_base = {
            key: value for key, value in misura.items()
            if not key.startswith('LISTA_') and isinstance(value, (str, int, float))
        }

        # Aggiungere nel dizionario misura_base
        status_list = misura.get("LISTA_STATUS_FINALITA_REG", {}).get("STATUS_FINALITA_REG", {})
        status = status_list[0] if isinstance(status_list, list) else status_list

        beneficiario_list = misura.get("LISTA_TIPO_BENEFICIARIO", {}).get("DIM_BENEFICIARIO_TYPE", {})
        beneficiario = beneficiario_list[0] if isinstance(beneficiario_list, list) else beneficiario_list

        # Gestione sicura con get()
        misura_base.update({
            "COD_STATUS": status.get("COD_STATUS") if isinstance(status, dict) else None,
            "DES_STATUS": status.get("DES_STATUS") if isinstance(status, dict) else None,
            "COD_DIM_BENEFICIARIO": beneficiario.get("COD_DIM_BENEFICIARIO") if isinstance(beneficiario, dict) else None,
            "DESCR_DIM_BENEFICIARIO": beneficiario.get("DESCR_DIM_BENEFICIARIO") if isinstance(beneficiario, dict) else None
        })

        misura_records.append(misura_base)

        # LISTA_SETTORI table
        settori = misura.get("LISTA_SETTORI", {}).get("SETTORE", [])
        if isinstance(settori, dict):
            settori = [settori]
        for settore in settori:
            settore_record = {
                "CAR": misura.get("CAR"),
                "COD_SETTORE": settore.get("COD_SETTORE"),
                "DES_SETTORE": settore.get("DES_SETTORE")
            }
            settori_records.append(settore_record)

        # LISTA_STRUMENTI table
        strumenti = misura.get("LISTA_STRUMENTI", {}).get("STRUMENTO", [])
        if isinstance(strumenti, dict):
            strumenti = [strumenti]
        for strumento in strumenti:
            strumento_record = {
                "CAR": misura.get("CAR"),
                "COD_STRUMENTO": strumento.get("COD_STRUMENTO"),
                "DES_STRUMENTO": strumento.get("DES_STRUMENTO")
            }
            strumenti_records.append(strumento_record)

        # LISTA_OBIETTIVI table
        obiettivi = misura.get("LISTA_OBIETTIVI", {}).get("OBIETTIVO", [])
        if isinstance(obiettivi, dict):
            obiettivi = [obiettivi]
        for obiettivo in obiettivi:
            obiettivo_record = {
                "CAR": misura.get("CAR"),  # mantiene il campo di join
                **{key: value for key, value in obiettivo.items()
                   if not key.startswith('LISTA_') and isinstance(value, (str, int, float))}
            }
            obiettivi_records.append(obiettivo_record)

        # LISTA_AREE table
        aree = misura.get("LISTA_AREE", {}).get("AREA", [])
        if isinstance(aree, dict):
            aree = [aree]
        for area in aree:
            area_record = {
                "CAR": misura.get("CAR"),
                "COD_AREA": area.get("COD_AREA"),
                "DES_AREA": area.get("DES_AREA")
            }
            aree_records.append(area_record)

        # LISTA_DOTAZIONI table
        dotazioni = misura.get("LISTA_DOTAZIONI", {}).get("DOTAZIONE", [])
        if isinstance(dotazioni, dict):
            dotazioni = [dotazioni]
        for dotazione in dotazioni:
            dotazione_record = {
                "CAR": misura.get("CAR"),
                **{key: value for key, value in dotazione.items()
                   if not key.startswith('LISTA_') and isinstance(value, (str, int, float))}
            }
            dotazioni_records.append(dotazione_record)

        # Alla fine del processing
        print(f"Totale records estratti:")
        print(f"Misure: {len(misura_records)}")
        print(f"Settori: {len(settori_records)}")
        print(f"Strumenti: {len(strumenti_records)}")
        print(f"Obiettivi: {len(obiettivi_records)}")
        print(f"Aree: {len(aree_records)}")
        print(f"Dotazioni: {len(dotazioni_records)}")

    # Extract filename for source field
    source_name = os.path.splitext(os.path.basename(input_path))[0]

    # Convert lists to Polars DataFrames and add source
    df_misure = (pl.DataFrame(misura_records)
                 .with_columns([
                     # Prima converti tutto in stringa tranne i campi importo
                     pl.all().exclude(["IMPORTO_AIUTO_AD_HOC", "IMPORTO_PRESTITI_GARANTITI"]).cast(pl.Utf8),
                     # Poi gestisci i campi importo come float
                     pl.col("IMPORTO_AIUTO_AD_HOC").cast(pl.Float64).round(2),
                     pl.col("IMPORTO_PRESTITI_GARANTITI").cast(pl.Float64).round(2),
                     # Aggiungi il campo source
                     pl.lit(source_name).alias("source")
                 ]))

    df_settori = (pl.DataFrame(settori_records)
                  .with_columns(pl.all().cast(pl.Utf8))
                  .with_columns(pl.lit(source_name).alias("source")))

    df_strumenti = (pl.DataFrame(strumenti_records)
                    .with_columns(pl.all().cast(pl.Utf8))
                    .with_columns(pl.lit(source_name).alias("source")))

    df_obiettivi = (pl.DataFrame(obiettivi_records)
                    .with_columns(pl.all().cast(pl.Utf8))
                    .with_columns(pl.lit(source_name).alias("source")))

    df_aree = (pl.DataFrame(aree_records)
               .with_columns(pl.all().cast(pl.Utf8))
               .with_columns(pl.lit(source_name).alias("source")))

    df_dotazioni = (pl.DataFrame(dotazioni_records)
                    .with_columns(pl.all().cast(pl.Utf8))
                    .with_columns(pl.lit(source_name).alias("source")))

    # Verifica che i DataFrame vengano creati e salvati
    if len(misura_records) > 0:
        print("Schema df_misure:", df_misure.columns)

    # Save to Parquet with optimized compression
    df_misure.write_parquet(
        misure_parquet,
        row_group_size=100000,
        compression="zstd",
        use_pyarrow=True
    )

    df_settori.write_parquet(
        settori_parquet,
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

    df_obiettivi.write_parquet(
        obiettivi_parquet,
        row_group_size=100000,
        compression="zstd",
        use_pyarrow=True
    )

    df_aree.write_parquet(
        aree_parquet,
        row_group_size=100000,
        compression="zstd",
        use_pyarrow=True
    )

    df_dotazioni.write_parquet(
        dotazioni_parquet,
        row_group_size=100000,
        compression="zstd",
        use_pyarrow=True
    )

if __name__ == "__main__":
    main()
