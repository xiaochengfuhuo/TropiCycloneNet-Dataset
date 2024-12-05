from netCDF4 import Dataset
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import argparse


def read_3D(dataset_path, TC_name, TC_date, area):
    # Open the NetCDF file
    year = TC_date[:4]
    file_path = os.path.join(dataset_path, 'Data3D', area, year, TC_name, f"TCND_{TC_name}_{TC_date}_sst_z_u_v.nc")

    # Open the NetCDF file
    nc_data = Dataset(file_path, mode='r')

    # Retrieve data from the NetCDF file
    pressure_levels = nc_data.variables['pressure_level'][:]  # Pressure levels
    u = nc_data.variables['u'][:]  # U component
    v = nc_data.variables['v'][:]  # V component
    z = nc_data.variables['z'][:]  # Geopotential
    sst = nc_data.variables['sst'][:]  # Sea Surface Temperature (assuming it's named 'sst')

    latitude = nc_data.variables['latitude'][:]  # Latitude
    longitude = nc_data.variables['longitude'][:]  # Longitude

    # Close the NetCDF file
    nc_data.close()

    # Plot all pressure levels (U, V, Z, SST)
    plot_all_pressure_levels(u, v, z, sst, pressure_levels, latitude, longitude)


def read_env(dataset_path,TC_name,TC_date,area):
    year = TC_date[:4]
    # Build the file path for environmental data
    path = os.path.join(dataset_path,'Env-Data', area, year, TC_name, TC_date + '.npy')
    env_data = np.load(path, allow_pickle=True).item()

    # Read the corresponding NetCDF file for pressure levels and geophysical data
    file_path = os.path.join(dataset_path,'Data3D',area,year,TC_name,f"TCND_{TC_name}_{TC_date}_sst_z_u_v.nc")
    nc_data = Dataset(file_path, mode='r')

    z = nc_data.variables['z'][:]  # Geopotential
    latitude = nc_data.variables['latitude'][:]  # Latitude
    longitude = nc_data.variables['longitude'][:]  # Longitude
    pressure_levels = nc_data.variables['pressure_level'][:]  # Pressure levels
    print("Pressure levels:", pressure_levels)  # Print the pressure levels

    # Find the index of 500 hPa
    pressure_500hPa = 500
    idx_500hPa = np.abs(pressure_levels - pressure_500hPa).argmin()  # Find the closest index to 500 hPa
    print(f"Index of 500 hPa: {idx_500hPa}")

    print(env_data)

    # Plot the environmental data along with the geophysical data
    plot_env(env_data, z, latitude, longitude, pressure_levels, idx_500hPa)


def plot_env(env_data, z, latitude, longitude, pressure_levels, idx_500hPa):
    # Example dictionary data to plot
    real_key = [
        'move_velocity',
        'month',
        'location_long',
        'location_lat',
        'history_direction24',
        'history_inte_change24'
    ]

    data = {
        "Key": [
            "Moving Velocity",
            "Month",
            "Location Longitude",
            "Location Latitude",
            "History Direction (24 h)",
            "History Intensity Change (24 h)",
            "Subtropical High"
        ],
        "Value": [str(env_data[x]) for x in real_key]
    }
    data['Value'].append('GPH')  # Add GPH (Geopotential Height) to the data

    # Convert the data to a pandas DataFrame for easy display
    df = pd.DataFrame(data)

    # Create the figure for plotting
    fig, ax = plt.subplots(figsize=(14, 6), nrows=1, ncols=2)

    # First part: Display GPH image for 500 hPa
    ax[1].set_title("500 hPa GPH")
    gph_500 = z[0, idx_500hPa, :, :]  # Use the index for 500 hPa
    contour = ax[1].contourf(longitude, latitude, gph_500, cmap='viridis')
    fig.colorbar(contour, ax=ax[1], orientation='vertical', label='Geopotential (gpm)')
    ax[1].set_xlabel('Longitude')
    ax[1].set_ylabel('Latitude')

    # Second part: Display the table with environmental data
    ax[0].axis('tight')
    ax[0].axis('off')

    # Create the table
    table = ax[0].table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc='center',
        loc='center'
    )

    # Set font size and column width
    table.auto_set_font_size(False)
    table.set_fontsize(10)

    # Manually set column widths
    column_widths = [2.0, 3.0]  # Adjust column width as needed
    for i, width in enumerate(column_widths):
        table.auto_set_column_width(col=[i])  # Set column width

    # Set cell height
    for key, cell in table.get_celld().items():
        if key[0] == 0:  # Header cells
            cell.set_height(0.1)  # Set header row height
        else:  # Data cells
            cell.set_height(0.1)  # Set data cell height

    # Adjust layout so the table and plot are well spaced
    plt.subplots_adjust(wspace=0.3)  # Adjust space between the two subplots

    # Show the plot and table
    plt.tight_layout()
    plt.show()


# Plotting function to visualize U, V, and Z components at all pressure levels
def plot_all_pressure_levels(u_data, v_data, z_data, sst_data, pressure_levels, lat, lon):
    # Use the first time step for visualization
    time_index = 0
    # Set up the figure with multiple subplots: U, V, Z, and SST for each pressure level
    num_levels = len(pressure_levels)
    fig, axes = plt.subplots(num_levels, 4, figsize=(22, num_levels * 6))  # Added extra column for SST

    # Iterate over each pressure level and plot U, V, Z, and SST
    for i, level in enumerate(pressure_levels):
        # Extract the specific pressure level data for U, V, Z, and SST
        u_level = u_data[time_index, i, :, :]
        v_level = v_data[time_index, i, :, :]
        z_level = z_data[time_index, i, :, :]
        sst_level = sst_data  # Sea Surface Temperature data

        # Plot U component
        ax1 = axes[i, 0]
        c1 = ax1.contourf(lon, lat, u_level, cmap='coolwarm')
        ax1.set_title(f"U Component at {level} hPa")
        ax1.set_xlabel("Longitude")
        ax1.set_ylabel("Latitude")
        fig.colorbar(c1, ax=ax1)

        # Plot V component
        ax2 = axes[i, 1]
        c2 = ax2.contourf(lon, lat, v_level, cmap='coolwarm')
        ax2.set_title(f"V Component at {level} hPa")
        ax2.set_xlabel("Longitude")
        ax2.set_ylabel("Latitude")
        fig.colorbar(c2, ax=ax2)

        # Plot Z component
        ax3 = axes[i, 2]
        c3 = ax3.contourf(lon, lat, z_level, cmap='coolwarm')
        ax3.set_title(f"Geopotential at {level} hPa")
        ax3.set_xlabel("Longitude")
        ax3.set_ylabel("Latitude")
        fig.colorbar(c3, ax=ax3)

        # Plot SST data
        if i == 0:
            ax4 = axes[i, 3]
            c4 = ax4.contourf(lon, lat, sst_level, cmap='viridis')
            ax4.set_title(f"SST")
            ax4.set_xlabel("Longitude")
            ax4.set_ylabel("Latitude")
            fig.colorbar(c4, ax=ax4)
        else:
            ax4 = axes[i, 3]
            ax4.set_axis_off()

    plt.tight_layout()
    plt.show()


# Main function for reading 1D data and plotting it
def read_1d(dataset_path,TC_name,TC_date,area,train_val_test):
    # Build file path for 1D data
    year = TC_date[:4]
    path = os.path.join(dataset_path,'Data1D', area, train_val_test, f"{area}{year}BST{TC_name.upper()}.txt")

    # Read the file content
    try:
        data = pd.read_csv(path, delimiter='\t', header=None,
                           names=['ID', 'LONG', 'LAT', 'PRES', 'WND', 'YYYYMMDDHH', 'Name'])
    except FileNotFoundError:
        print(f"File not found: {path}")
        return

    print("Data loaded successfully!")
    print(data.head())  # Print the first few rows of data

    # Filter data based on the specified time
    target_time = float(TC_date)
    selected_data = data[data['YYYYMMDDHH'] == target_time]
    index = data[data['YYYYMMDDHH'] == target_time].index[0]

    # If data for the target time is found, get 5 data points
    if not selected_data.empty:
        print(f"Found data for {target_time}")
        # Get 5 data points, ensuring the specified time point is included
        data_to_plot = data[index:index + 5]  # Get the next 5 rows

        # Visualize the data
        plot_data1d(data_to_plot)

    else:
        print(f"No data found for the time point: {target_time}")


# Function to plot the 1D data in a table format
def plot_data1d(data):
    # Create a new figure for the table
    fig, ax = plt.subplots(figsize=(10, 6))  # Adjust size

    # Set the table title
    ax.set_title("Data1D Example")

    # Create the table with selected columns
    table = ax.table(
        cellText=data[['ID', 'LONG', 'LAT', 'PRES', 'WND', 'YYYYMMDDHH', 'Name']].values,
        colLabels=['ID', 'LONG', 'LAT', 'PRES', 'WND', 'YYYYMMDDHH', 'Name'],
        cellLoc='center',
        loc='center'
    )

    # Set font size and column width
    table.auto_set_font_size(False)
    table.set_fontsize(10)

    # Manually set column widths
    column_widths = [2.0, 3.0, 3.0, 3.0, 3.0, 3.0]
    for i, width in enumerate(column_widths):
        table.auto_set_column_width(col=[i])  # Set column width

    # Set cell height
    for key, cell in table.get_celld().items():
        if key[0] == 0 or key[0] == 1:  # Header cells
            cell.set_height(0.1)  # Set header height
            cell.set_text_props(weight='bold')  # Make header bold
        else:  # Data cells
            cell.set_height(0.08)  # Set data cell height

    # Hide the axes
    ax.axis('off')

    # Adjust layout to make the plot and table well spaced
    plt.tight_layout()
    plt.show()

def read_all(dataset_path,TC_name,TC_date,area,train_val_test):
    read_3D(dataset_path,TC_name,TC_date,area)
    read_env(dataset_path,TC_name,TC_date,area)
    read_1d(dataset_path,TC_name,TC_date,area,train_val_test)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process TCND data')
    parser.add_argument('dataset_path', type=str, help='Path where the dataset is located', nargs='?',
                        default='J:\\TropiCycloneNet_dataset\\TCND')
    parser.add_argument('TC_name', type=str, help='Name of the tropical cyclone to examine', nargs='?',
                        default='Haiyan')
    parser.add_argument('TC_date', type=str, help='Specific date and time of the cyclone in YYYYMMDDHH format',
                        nargs='?', default='2001101406')
    parser.add_argument('area', type=str, help='Ocean region where the cyclone occurred (e.g., WP for Western Pacific)',
                        nargs='?', default='WP')
    parser.add_argument('train_val_test', type=str,
                        help='Indicates whether the queried typhoon belongs to training, validation, or test set',
                        nargs='?', default='train')

    args = parser.parse_args()
    read_all(args.dataset_path, args.TC_name, args.TC_date, args.area, args.train_val_test)


#python read_TCND.py J:\\TropiCycloneNet_dataset\\TCND LINGLING 2019090618 WP test