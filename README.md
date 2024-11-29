# TropiCycloneNet-Dataset

## Overview

This project introduces the details of the **TropiCycloneNet Dataset (TCND)**, a comprehensive dataset for studying tropical cyclones (TCs). It includes **1D**, **3D**, and **environmental data (Env-Data)** collected for various tropical cyclones in the major oceanic regions from 1950 to 2023. The dataset is aimed at providing valuable insights for tropical cyclone research and predictive modeling.

## Download

We offer two download options for the **TropiCycloneNet Dataset (TCND)**:

- **Full Dataset**: Contains tropical cyclone data from 1950 to 2023, across six major oceans. The data size is approximately `xxx GB`.
    - [Full Dataset](www.xxxxxx)
  
- **Test Subset**: A smaller subset of data from 2017 to 2023, intended for testing purposes. The data size is approximately `xxx GB`.
    - [Test Subset](www.xxxxxx)

## Check Data

We provide code to read and visualize **Data1D**, **Data3D**, and **Env-Data**. Researchers can flexibly use our dataset and visualize different types of data using the provided scripts.

### Steps to Use the Dataset

1. **Download and Extract the Dataset**: 
   - Download and extract the TCND dataset to your desired path (`path_a`).
   
2. **Set Up the Environment**:
   - Install Python 3.7 and the necessary dependencies:
   
     ```bash
     pip install netCDF4==1.5.8
     pip install matplotlib==3.5.3
     pip install pandas==1.1.1
     pip install numpy==1.19.0
     ```
   
3. **Run the Code**:
   - After setting up the environment, run the `read_TCND.py` script:
   
     ```bash
     python read_TCND.py dataset_path TC_name TC_date area
     ```
   
     Here:
     - `dataset_path` refers to the path where the dataset is located.
     - `TC_name` is the name of the tropical cyclone you wish to examine.
     - `TC_date` is the specific date and time of the cyclone in `YYYYMMDDHH` format.
     - `area` specifies the ocean region where the cyclone occurred (e.g., WP for Western Pacific, EP for Eastern Pacific, etc.).

   - After running the script, you will find visualized images of **Data1D**, **Data3D**, and **Env-Data** in the current directory. The images will be named `Data1D.png`, `Data3D.png`, and `Env-Data.png`.

## Visualization Example

### Visualizing All Data

1. **Get Details for Data3D**:
   The **3D data** covers the **25° x 25° region** around the tropical cyclone's center. The spatial resolution is **0.25°**, and the temporal resolution is **6 hours**. We collect **Geopotential Height (GPH)**, **U-component of wind**, and **V-component of wind** at **200 hPa, 500 hPa, 850 hPa**, and **925 hPa** pressure levels. **Sea Surface Temperature (SST)** data is also included in the **Data3D** set.

2. **Example of Data1D, Data3D, and Env-Data**:
   The following command visualizes the tropical cyclone data for a specific time (`2001101418` for `Haiyan` in the Western Pacific region):

   ```bash
   python read_TCND.py dataset_path Haiyan 2001101418 WP

After running the script, you will see the corresponding cyclone **Data1D**, **Data3D**, and **Env-Data** visualizations.

**Image 1**:  
(Link to the image displaying **Data1D** visualization)  
![Data1D Example](images/Data1D_example.png)

### 3D Data Visualization

We crop the data covering a **25° x 25°** region around the TC center. The spatial resolution is **0.25°**, and the time resolution is **6 hours**. We collect **Geopotential Height (GPH)**, **U-component of wind**, and **V-component of wind** at **200 hPa**, **500 hPa**, **850 hPa**, and **925 hPa** pressure levels. **Sea Surface Temperature (SST)** data is also included in the **Data3D** set.

**Image 2**:  
(Link to the image displaying **3D data** visualization)  
![3D Data Example](images/Data3D_example.png)

### Visualizing Data1D

#### Examples of **Data1D**:

- **ID**: Time step of the TC.
- **LONG**: Longitude of the TC center (with a precision of **0.1°E**).
- **LAT**: Latitude of the TC center (with a precision of **0.1°N**).
- **PRES**: Minimum pressure (hPa) near the TC center.
- **WND**: Two-minute mean maximum sustained wind (MSW; m/s) near the TC center.
- **YYYYMMDDHH**: Date and time (UTC) of the TC event.
- **Name**: Name of the TC.

The **Data1D** is normalized using specific rules to make it suitable for **deep learning (DL)** methods to extract useful information.

**Image 3**:  
(Link to the image displaying **Data1D details** visualization)  
![Data1D Details](images/Data1D_details.png)

### Visualizing **Env-Data**

The **Env-Data** includes the following attributes:

- **Movement Velocity**: The movement velocity of the tropical cyclone.
- **Month**: Month of occurrence.
- **Location Longitude and Latitude**: The relative location on Earth.
- **24-hour History of Direction**: The movement direction of the cyclone in the past 24 hours.
- **24-hour History of Intensity Change**: The intensity change of the cyclone in the past 24 hours.
- **Subtropical High Region**: Extracted from **500 hPa Geopotential Height (GPH)** data. This variable is processed to make the data more suitable for input to **DL models**.

**Image 4**:  
(Link to the image displaying **Env-Data** visualization)  
![Env-Data Example](images/EnvData_example.png)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

We would like to acknowledge the support of the research community and the institutions that contributed to the development of this dataset. The **TropiCycloneNet Dataset** has been designed for academic and research purposes in tropical cyclone studies.

---

Feel free to reach out with any questions or comments regarding the **TropiCycloneNet Dataset** or how to use this project.
