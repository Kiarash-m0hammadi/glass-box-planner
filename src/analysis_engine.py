"""
The Glass Box Planner - Core Analysis Engine

This script is the reproducible, transparent computational core of the paper's method.
It performs a deductive, policy-driven land use compatibility audit using a simple,
vectorized adjacency model and a user-supplied compatibility matrix.

Design philosophy (brief):
- Prioritize transparency over algorithmic complexity: the engine implements
  straightforward geometric adjacency + lookup logic so that every step is inspectable.
- Comments explain methodological choices ("why"), not just the mechanics ("what").
- Defaults point to the repository's data layout so the project is runnable out-of-the-box.

Usage:
    Run from CLI with explicit paths, or let the GUI inject configuration into the
    CONFIGURATION SECTION and run the script without CLI args.
"""
# =============================================================================
# A SCALABLE, VECTORIZED ENGINE FOR LAND USE COMPATIBILITY ANALYSIS
# Production-ready, repo-aligned variant placed in /src for project structure.
# =============================================================================

import geopandas as gpd
import pandas as pd
from pathlib import Path
import time
import argparse

# =============================================================================
# --- CONFIGURATION SECTION ---
# Edit these values for ad-hoc runs. When using the GUI, the GUI will inject
# matching config values into the same markers found below.
# =============================================================================

# --- Choose ONE of the following input data formats ---
# By default the engine looks for inputs in the repository data/input folder.
# This encourages reproducible workflows: inputs are colocated and outputs are
# written to data/output (which should be empty in version control).
INPUT_DATA_PATH = Path("data/input/gis_qazvin/Qazvin_Parcels.shp")  # shapefile or .gpkg recommended

# If using a File Geodatabase (.gdb), set INPUT_DATA_PATH to that .gdb and
# provide the GDB layer name here:
# INPUT_DATA_PATH = Path("data/input/CityData.gdb")
# GDB_LAYER_NAME = "Qazvin_Parcels"

# The compatibility matrix CSV (recommended location: data/input/)
MATRIX_CSV_PATH = Path("data/input/Compatibility Matrix.csv")

# Output GeoPackage path (written to data/output/)
OUTPUT_GEOPACKAGE = Path("data/output/Qazvin_Final_Results.gpkg")

# Column name in the input parcel data that contains the land use classification.
LAND_USE_COLUMN = "KARBARI_MO"

# Distance (meters) to define adjacency (a uniform buffer is intentional).
ADJACENCY_DISTANCE_METERS = 10

# =============================================================================
# --- ANALYSIS ENGINE ---
# (Do not edit below this line unless you understand the pipeline)
# =============================================================================

def generate_reports(gdf, output_dir, base_name, land_use_col):
    """
    Calculates and saves two summary CSV reports.

    Rationale:
    The overall summary gives a city-wide distribution of compatibility scores,
    useful for high-level argumentation. The detailed breakdown by land-use
    type supports the paper's claim that disaggregated diagnostics reveal
    localized policy frictions that city-level aggregates can hide.
    """
    print("  > Generating summary reports...")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Overall Summary Report
    overall_summary = gdf['compat_score'].value_counts().sort_index().to_frame(name='parcel_count')
    overall_summary['percentage'] = (overall_summary['parcel_count'] / overall_summary['parcel_count'].sum()) * 100
    overall_summary = overall_summary.reindex(range(1, 6), fill_value=0)  # Ensure scores 1-5 are present
    overall_summary_path = output_dir / f"{base_name}_overall_summary.csv"
    overall_summary.to_csv(overall_summary_path, index_label='compatibility_score')
    print(f"    - Overall summary saved to: {overall_summary_path.name}")

    # 2. Detailed Breakdown Report
    detailed_summary = gdf.groupby([land_use_col, 'compat_score']).size().unstack(fill_value=0)
    # Ensure all score columns 1-5 exist
    for score in range(1, 6):
        if score not in detailed_summary.columns:
            detailed_summary[score] = 0
    detailed_summary = detailed_summary[sorted(detailed_summary.columns)]  # Sort columns
    detailed_summary['total_parcels'] = detailed_summary.sum(axis=1)
    detailed_summary_path = output_dir / f"{base_name}_detailed_breakdown.csv"
    detailed_summary.to_csv(detailed_summary_path)
    print(f"    - Detailed breakdown saved to: {detailed_summary_path.name}")

def run_analysis(parcels_path, matrix_path, output_dir, base_name=None,
                 land_use_col=LAND_USE_COLUMN, adjacency_distance=ADJACENCY_DISTANCE_METERS):
    """Main function to execute the entire analysis workflow with CLI-configurable paths.

    Parameters:
    - parcels_path: path to input parcels (shapefile or .gpkg)
    - matrix_path: path to compatibility matrix CSV
    - output_dir: directory where outputs will be written
    - base_name: base filename for outputs (defaults to input stem or 'Qazvin_processed')
    - land_use_col: name of land use column in parcels
    - adjacency_distance: buffer distance (meters) used to define adjacency
    """
    start_time = time.time()
    print("--- Initializing High-Performance Analysis Engine ---")

    # Normalize and prepare paths/names
    parcels_path = Path(parcels_path)
    matrix_path = Path(matrix_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if base_name:
        base = base_name
    else:
        # Prefer the input filename stem, fallback to a clear default
        base = parcels_path.stem if parcels_path.exists() and parcels_path.stem else "Qazvin_processed"

    output_geopackage = output_dir / f"{base}.gpkg"
    land_use_column = land_use_col
    adjacency_distance = adjacency_distance

    # --- Section 1: Data Loading and Validation ---
    print(f"\n[1/5] Loading and preparing data...")
    try:
        if parcels_path.suffix.lower() == ".gdb":
            # Reading a File Geodatabase requires a layer name; fail fast with a clear message.
            raise RuntimeError(
                "File Geodatabase (.gdb) inputs require an explicit layer. "
                "Please provide parcels as a .gpkg or shapefile, or open the .gdb in Python and "
                "pass the desired layer as a separate argument."
            )
        else:
            if not parcels_path.exists():
                raise FileNotFoundError(f"Input file not found at {parcels_path}")
            print(f"  > Reading from file: {parcels_path}")
            gdf = gpd.read_file(parcels_path)
    except Exception as e:
        print(f"FATAL ERROR: Could not read the input data. Please check path and format.")
        print(f"  > Details: {e}")
        return

    print(f"  > Loaded {len(gdf)} parcels.")
    if land_use_column not in gdf.columns:
        print(f"FATAL ERROR: Land use column '{land_use_column}' not found.")
        print(f"  > Available columns are: {list(gdf.columns)}")
        return

    # Reproject if data are in geographic coordinates.
    if gdf.crs is None:
        print("  > Warning: Input CRS is undefined. Results may be unreliable.")
    elif gdf.crs.is_geographic:
        print(f"  > Warning: CRS is geographic. Re-projecting to estimated UTM zone.")
        gdf = gdf.to_crs(gdf.estimate_utm_crs())
    print(f"  > Using projected CRS: {gdf.crs.name if gdf.crs else 'Unknown'}")

    # --- Section 2: Loading Compatibility Matrix ---
    print(f"\n[2/5] Loading compatibility matrix...")
    if not matrix_path.exists():
        print(f"FATAL ERROR: Matrix CSV not found at {matrix_path}")
        return
    compatibility_matrix = pd.read_csv(matrix_path, index_col=0)
    print("  > Matrix loaded successfully.")

    # --- Section 3: Core Algorithm: Vectorized Adjacency Analysis ---
    print(f"\n[3/5] Performing adjacency analysis...")
    if 'unique_id' not in gdf.columns:
        gdf['unique_id'] = range(len(gdf))
        
    # Use a simple, uniform buffer to define adjacency.
    gdf_buffered = gdf.copy()
    gdf_buffered['geometry'] = gdf.buffer(adjacency_distance)
        
    adjacent_pairs = gpd.sjoin(gdf, gdf_buffered, how="inner", predicate="intersects")
    adjacent_pairs = adjacent_pairs[adjacent_pairs.unique_id_left != adjacent_pairs.unique_id_right]
    adjacent_pairs = adjacent_pairs[['unique_id_left', f'{land_use_column}_left', 'unique_id_right']]

    print(f"  > Found {len(adjacent_pairs)} adjacent parcel pairs.")
    # --- Section 4: Scoring and Aggregation ---
    print(f"\n[4/5] Scoring pairs and aggregating results...")
    # Melt the matrix for a high-performance relational join.
    matrix_long = compatibility_matrix.stack().reset_index()
    matrix_long.columns = ['use_1', 'use_2', 'score']
        
    # Get the land use from the right side of each pair.
    right_uses = gdf[[land_use_column, 'unique_id']].rename(
        columns={land_use_column: f"{land_use_column}_right", 'unique_id': 'unique_id_right'}
    )
    adjacent_pairs = pd.merge(adjacent_pairs, right_uses, on='unique_id_right', how='left')

    # This merge is the vectorized score lookup.
    scored_pairs = pd.merge(
        adjacent_pairs,
        matrix_long,
        left_on=[f'{land_use_column}_left', f'{land_use_column}_right'],
        right_on=['use_1', 'use_2'],
        how='left'
    )

    # Vectorized aggregation: worst-case (minimum) score per parcel.
    final_scores = scored_pairs.groupby('unique_id_left')['score'].min()
    print(f"  > Aggregation complete using 'minimum score' method.")
    # --- Section 5: Finalizing and Exporting ---
    print(f"\n[5/5] Finalizing and exporting results...")
    gdf = gdf.merge(final_scores.rename('compat_score'), left_on='unique_id', right_index=True, how='left')
    # Default unseen parcels to highest compatibility to avoid false negatives.
    gdf['compat_score'] = gdf['compat_score'].fillna(5)
    gdf['compat_score'] = gdf['compat_score'].astype('Int64')
    
    # Clean-up and export
    gdf = gdf.drop(columns=['unique_id'])
    gdf.to_file(output_geopackage, driver="GPKG")
    print(f"  > Main results exported to: {output_geopackage}")

    # Generate and save the summary reports using reproducible filenames
    generate_reports(gdf, output_dir, base, land_use_column)
    
    print("\n--- ANALYSIS COMPLETE ---")
    print(f"  > Total Execution Time: {time.time() - start_time:.2f} seconds.")

if __name__ == "__main__":
    # Derive sensible defaults from the in-file configuration constants so GUI-injected
    # config (which replaces the CONFIGURATION SECTION) is respected.
    try:
        default_parcels = str(INPUT_DATA_PATH)
    except Exception:
        default_parcels = str(Path("data/input/gis_qazvin/Qazvin_Parcels.shp"))

    try:
        default_matrix = str(MATRIX_CSV_PATH)
    except Exception:
        default_matrix = str(Path("data/input/Compatibility Matrix.csv"))

    try:
        default_output_dir = str(Path(OUTPUT_GEOPACKAGE).parent)
        default_base = Path(OUTPUT_GEOPACKAGE).stem
    except Exception:
        default_output_dir = str(Path("data/output"))
        default_base = None

    parser = argparse.ArgumentParser(
        description="Glass Box Planner - Core Analysis Engine (reproducible CLI)"
    )
    parser.add_argument(
        "--parcels", "-p",
        required=False,
        default=default_parcels,
        help="Path to input parcels (shapefile or .gpkg). Example: data/input/parcels.gpkg"
    )
    parser.add_argument(
        "--matrix", "-m",
        required=False,
        default=default_matrix,
        help='Path to compatibility matrix CSV. Example: "Compatibility Matrix.csv"'
    )
    parser.add_argument(
        "--output_dir", "-o",
        required=False,
        default=default_output_dir,
        help="Directory to write outputs (will be created if missing)."
    )
    parser.add_argument(
        "--base_name", "-b",
        required=False,
        default=default_base,
        help="Base name for outputs (defaults to parcels filename stem or 'Qazvin_processed')."
    )
    parser.add_argument(
        "--land_use_col",
        required=False,
        default=LAND_USE_COLUMN,
        help=f"Name of land use column in parcels (default: {LAND_USE_COLUMN})."
    )
    parser.add_argument(
        "--adjacency_distance",
        type=float,
        required=False,
        default=ADJACENCY_DISTANCE_METERS,
        help=f"Adjacency buffer distance in meters (default: {ADJACENCY_DISTANCE_METERS})."
    )

    args = parser.parse_args()
    run_analysis(
        parcels_path=args.parcels,
        matrix_path=args.matrix,
        output_dir=args.output_dir,
        base_name=args.base_name,
        land_use_col=args.land_use_col,
        adjacency_distance=args.adjacency_distance,
    )