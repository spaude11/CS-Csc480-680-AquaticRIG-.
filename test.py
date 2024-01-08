import streamlit as st
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import tempfile

st.set_page_config(layout="wide", page_title="NC Uploader")

st.write("## Upload nc file")
st.write(" Try uploading an nc file :grin:")
st.sidebar.write("## Upload :gear:")

MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB

def visualizeNC(uploaded_file, depth_index):
    try:
        # Get the content of the file as bytes
        file_content = uploaded_file.getvalue()

        # Create a BytesIO object
        file_bytesio = BytesIO(file_content)

        # Create a temporary file and write the BytesIO content to it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".nc") as temp_file:
            temp_file.write(file_content)

        with nc.Dataset(temp_file.name, 'r') as dataset:
            # Extract data for visualization
            lon = dataset.variables['lon'][:]
            lat = dataset.variables['lat'][:]
            data_temp = dataset.variables['temp'][0, depth_index, :, :]

            # Plot the data
            fig, ax = plt.subplots(figsize=(12, 8))
            cax = ax.contourf(lon, lat, data_temp, cmap='viridis')
            fig.colorbar(cax, label='Temperature (°C)')
            ax.set_title(f'Temperature at Depth {depth_index}')
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')

            # Display the figure in Streamlit
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error reading NetCDF file: {str(e)}")
    finally:
        # Clean up: Delete the temporary file
        if 'temp_file' in locals():
            temp_file.close()

def dataNC(uploaded_file):
    try:
        # Get the content of the file as bytes
        file_content = uploaded_file.getvalue()

        # Create a BytesIO object
        file_bytesio = BytesIO(file_content)

        # Create a temporary file and write the BytesIO content to it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".nc") as temp_file:
            temp_file.write(file_content)

        with nc.Dataset(temp_file.name, 'r') as dataset:
            st.text("NC file contents:")
            st.text(dataset)

            st.markdown("**Dimensions:**")
            for dim_name, dim in dataset.dimensions.items():
                st.text(f"{dim_name}({len(dim)})")

            st.markdown("**Variables:**")
            for var in dataset.variables.keys():
                if var not in dataset.dimensions:
                    st.text(f"{var}")
    except Exception as e:
        st.error(f"Error reading NetCDF file: {str(e)}")
    finally:
        # Clean up: Delete the temporary file
        if 'temp_file' in locals():
            temp_file.close()
            #st.text(f"Temporary file {temp_file.name} deleted.")


my_upload = st.sidebar.file_uploader("Upload an .nc", type=["nc"])

# Use st.session_state to persistently store the depth_index
if 'depth_index' not in st.session_state:
    st.session_state.depth_index = 0  # Initialize depth_index if not already present

if my_upload is not None:
    if my_upload.size > MAX_FILE_SIZE:
        st.error("The uploaded file is too large. Please upload an image smaller than 1GB.")
    else:
        # Buttons for increasing and decreasing depth
        if st.button("Increase Depth ⬆️"):
            st.session_state.depth_index += 1
        if st.button("Decrease Depth ⬇️"):
            st.session_state.depth_index = max(0, st.session_state.depth_index - 1)

        visualizeNC(my_upload, st.session_state.depth_index)
        dataNC(my_upload)
else:
    st.error("No file was uploaded")

