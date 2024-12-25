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
    aiuti_parquet = os.path.join(output_dir, f"{base_name}_aiuti.parquet")
    componenti_parquet = os.path.join(output_dir, f"{base_name}_componenti.parquet")
    strumenti_parquet = os.path.join(output_dir, f"{base_name}_strumenti.parquet")

    # Read XML file
    with open(input_path, "r", encoding="utf-8") as file:
        data = xmltodict.parse(file.read())

    # Extract LISTA_AIUTI content
    aiuti = data.get("LISTA_AIUTI", {}).get("AIUTO", [])

    # Main tables
    aiuto_records = []
    componenti_records = []
    strumenti_records = []

    for aiuto in aiuti:
        # AIUTO table
        aiuto_base = {key: aiuto.get(key) for key in aiuto if key != "COMPONENTI_AIUTO"}
        aiuto_records.append(aiuto_base)

        # COMPONENTI_AIUTO table
        componenti_aiuto = aiuto.get("COMPONENTI_AIUTO", {}).get("COMPONENTE_AIUTO", [])
        if isinstance(componenti_aiuto, dict):  # Handle single component case
            componenti_aiuto = [componenti_aiuto]

        for componente in componenti_aiuto:
            # Remove STRUMENTI_AIUTO from COMPONENTI table
            componente_record = {key: componente.get(key) for key in componente if key != "STRUMENTI_AIUTO"}
            componente_record["CAR"] = aiuto.get("CAR")  # Foreign key to AIUTO
            componente_record["COR"] = aiuto.get("COR")  # Foreign key to AIUTO
            componenti_records.append(componente_record)

            # STRUMENTI_AIUTO table
            strumenti_aiuto = componente.get("STRUMENTI_AIUTO", {}).get("STRUMENTO_AIUTO", [])
            if isinstance(strumenti_aiuto, dict):  # Handle single instrument case
                strumenti_aiuto = [strumenti_aiuto]

            for strumento in strumenti_aiuto:
                strumento["ID_COMPONENTE_AIUTO"] = componente.get("ID_COMPONENTE_AIUTO")
                strumenti_records.append(strumento)

    # Extract filename for source field
    source_name = os.path.splitext(os.path.basename(input_path))[0]

    # Convert lists to Polars DataFrames and add source
    df_aiuti = (pl.DataFrame(aiuto_records)
                .with_columns([
                    pl.col("DATA_CONCESSIONE").str.strptime(pl.Date, format="%Y-%m-%d", strict=False),
                    pl.all().exclude("DATA_CONCESSIONE").cast(pl.Utf8)
                ])
                .with_columns(pl.lit(source_name).alias("source")))

    df_componenti = (pl.DataFrame(componenti_records)
                     .with_columns(pl.all().cast(pl.Utf8))
                     .with_columns(pl.lit(source_name).alias("source")))

    df_strumenti = (pl.DataFrame(strumenti_records)
                    .with_columns([
                        pl.col("ELEMENTO_DI_AIUTO").cast(pl.Float64),
                        pl.col("IMPORTO_NOMINALE").cast(pl.Float64),
                        pl.all().exclude(["ELEMENTO_DI_AIUTO", "IMPORTO_NOMINALE"]).cast(pl.Utf8)
                    ])
                    .with_columns(pl.lit(source_name).alias("source")))

    # Save to Parquet with optimized compression
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
