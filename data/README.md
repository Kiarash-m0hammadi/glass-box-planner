# Data for "The Glass Box Planner" Project

This document provides details for the primary geospatial dataset used in the paper, *"The Glass Box Planner: An Open-Source Framework for Transparent Pairwise Compatibility Analysis in Urban Planning."*

To comply with FAIR data principles and reproducible research standards, the dataset is not stored in this code repository. Instead, it is permanently archived on Zenodo to ensure long-term availability, versioning, and a stable Digital Object Identifier (DOI).

## Access and Citation

**The official dataset can be accessed and downloaded from Zenodo using the following DOI:**

*   **DOI:** `10.5281/zenodo.17174603`
*   **Direct Link:** [https://doi.org/10.5281/zenodo.17174603](https://doi.org/10.5281/zenodo.17174603)

If you use this dataset in your research, you are required to cite it. Please use the following formal citation:

> Mohammadi, Kiarash. (2025). *Qazvin Parcel Dataset for "The Glass Box Planner" Study* (v1.0.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.17174603

## Dataset Details

*   **Source:** The data was originally sourced from the Qazvin Municipal Planning Office (2012).
*   **Content:** The Zenodo archive (`gis_qazvin.zip`) contains an ESRI Shapefile (`.shp`) and its associated sidecar files.
*   **Coordinate Reference System (CRS):** WGS 84 / UTM zone 39N (EPSG:32639).
*   **Pre-processing:** The raw data was validated to repair any invalid geometries. The land-use taxonomy in the attribute table was standardized to match the schema defined in this project's [`COMPATIBILITY_MATRIX.md`](../COMPATIBILITY_MATRIX.md).

## License

The dataset is licensed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license. You are free to share and adapt the data for any purpose, provided you give appropriate credit by using the citation above.