import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from PIL import Image
import subprocess
import os
import base64
import pickle

MENU_NO = 1

def streamlit_menu(MENU=1):
    if MENU == 1:
        selected = option_menu(
            menu_title=None,  
            options=["Home", "Predict", "About", "Team"], 
            icons=["house", "layer-backward", "file-earmark-text", "people"],  
            menu_icon="none",  
            default_index=0,  
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "black", "font-family": "Times New Roman", "font-size": "21px"},
                "nav-link": {
                    "font-family": "Serif",
                    "font-size": "21px",
                    "text-align": "left",
                    "margin": "1px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "crimson"},
            },
        )
        return selected
  
selected = streamlit_menu(MENU=MENU_NO)

if selected == "Home":     
    # Logo image
    image = Image.open('logo_latest.png')

    st.image(image, use_column_width=True)

    # Page title
    welcome_title = '<p style="font-family:Serif; color:firebrick; font-size: 25px; text-align: center; ">Welcome to <b>M<sup>Pro</sup> <b> pred !</p>'
    st.markdown(welcome_title, unsafe_allow_html=True)
    
    original_subtitle = '<p style="font-family:Serif; color:olive; font-size: 25px; text-align: center; ">Predict bioactivity of compounds against the "Main Protease" of <b>SARS-CoV-2<b></p>'
    st.markdown(original_subtitle, unsafe_allow_html=True)
    
    st.text("")

    predict_title = '<p style="font-family:Serif; color:black; font-size: 20px; text-align: center; ">Go to "<b>Predict</b>" menu to start submission!</p>'
    st.markdown(predict_title, unsafe_allow_html=True)
    
    st.text("")
    st.text("")
    st.text("")
    st.text("")
    
    st.markdown(
    """<a style='font-family:Serif; display: block; text-align: center;' href="https://www.worldometers.info/coronavirus/">COVID-19 Live Update!</a>
    """,
    unsafe_allow_html=True)
    
if selected == "Predict":
     # Logo image
    image = Image.open('logo_latest.png')
    st.image(image, use_column_width=True)
    
    # Molecular descriptor calculator option
    def desc_calc():
        # Performs the descriptor calculation
        bashCommand = "java -Xms2G -Xmx2G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/MACCSFingerprinter.xml -dir ./ -file descriptors_output.csv"
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        os.remove('molecule.smi')

    # File download option
    def filedownload(df):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Download Predictions</a>'
        return href

    # Model building section
    def build_model(input_data):
        # Reads in saved regression model
        load_model = pickle.load(open('Mpro_model.pkl', 'rb'))
        # Apply model to make predictions
        prediction = load_model.predict(input_data)
        st.header('**Prediction results**')
        prediction_output = pd.Series(prediction, name='pIC50')
        molecule_name = pd.Series(load_data[1], name='molecule_name')
        df = pd.concat([molecule_name, prediction_output], axis=1)
        st.write(df)
        st.markdown(filedownload(df), unsafe_allow_html=True)

    # Sidebar setting
    with st.sidebar.header('Data upload section'):
        uploaded_file = st.sidebar.file_uploader("Upload your input file", type=['txt'])
        st.sidebar.markdown("""
    [Example input file](https://raw.githubusercontent.com/Nadimfrds/Mpropred/master/sample_input.txt)
    """)

    if st.sidebar.button('Predict!'):
        load_data = pd.read_table(uploaded_file, sep=' ', header=None)
        load_data.to_csv('molecule.smi', sep = '\t', header = False, index = False)

        st.header('**Your input data**')
        st.write(load_data)

        with st.spinner("Calculating descriptors...wait a while"):
            desc_calc()

        # Read in the calculated descriptors and display the dataframe
        st.header('**Calculated molecular descriptors from your data**')
        desc = pd.read_csv('descriptors_output.csv')
        st.write(desc)
        st.write(desc.shape)

        # Read the descriptor list used in previously built model
        st.header('**Subset of descriptors from MACCS models**')
        Xlist = list(pd.read_csv('lists_of_descriptor.csv').columns)
        desc_subset = desc[Xlist]
        st.write(desc_subset)
        st.write(desc_subset.shape)

        # Apply the trained model to make prediction on query compounds
        build_model(desc_subset)
    else:
        st.info('Upload your input data in the sidebar to start prediction!')
if selected == "About":
    # Logo image
    image = Image.open('logo_latest.png')
    st.image(image, use_column_width=True)
    
    st.markdown("""
    **About the WebApp**
    - The WebApp is developed on **Python**,  **HTML** & **Streamlit** 
    - The Molecular descriptors of compounds were calculated using [PaDEL-Descriptor](http://www.yapcwsoft.com/dd/padeldescriptor/)
    - **MACCS** (Molecular ACCess System) fingerprints were used to measure the molecular similarity of the datasets and query compounds
    - The dataset is comprised of **758** compounds having inhibition efficacy against the **Main Protease**  published in peer-reviewed journals between January 2020 and August 2021
    ---
    **Usage**
    - **Step 1**: Gather SMILES notation of your query compounds of interest from any of the public databases such as [Drugbank](https://go.drugbank.com/), [PubChem](https://pubchem.ncbi.nlm.nih.gov/), [ChemSpider](http://www.chemspider.com/), [ChEMBL](https://www.ebi.ac.uk/chembl/) etc. (alternatively you can draw your compound and generate the SMILES notation from any editors such as [JSME structure editor](https://cactus.nci.nih.gov/gifcreator/editor.html), ChemDraw, ChemAxon MarvinSketch etc.)
    - **Step 2**: Upload your input molecules as SMILES notation in a text (.txt) file containing the SMILES notation and a given name or ID (space separated) by clicking on the **“Browse files”** button. 
    - **Step 3**: Click **“Predict!”** button to start the prediction process
    - **Step 4**: The results are automatically showed in a box found below the **“Prediction results”** heading. You can also download the results as a CSV file by clicking the **“Download Predictions”** button.
    ---
    **About Main Protease**
    - The **Main protease** is considered as one of the most promising drug targets of SARS-CoV-2
    - The protease is essential for processing the polyproteins of SARS-CoV-2 that are translated from the viral RNA 
    - It has 3 domains where the Domain I and Domain II contribute one residue to the catalytic dyad **Cys145** and **His41** which is cruicial for the proteolytic activity
    - Pfizer’s recently developed oral antiviral **PAXLOVID™** (nirmatrelvir [PF-07321332] tablets and ritonavir tablets) is an active **Main protease** inhibitor
    ---
    """)
if selected == "Team":
    # Logo image
    image = Image.open('logo_latest.png')
    st.image(image, use_column_width=True)
    
    st.markdown("<h1 style='text-align: center; font-family:Serif; color: black;'>Developers</h1>", unsafe_allow_html=True)
    st.markdown("""
    - **[Nadim Ferdous](https://www.researchgate.net/profile/Nadim-Ferdous)**, **Senior year student**, Department of Biotechnology & Genetic Engineering, Faculty of Life Science, Mawlana Bhashani Science and Technology University, Santosh, Tangail-1902, Bangladesh
    - **[Mahjerin Nasrin Reza](https://www.researchgate.net/profile/Mahjerin-Nasrin-Reza)**, **Senior year student**, Department of Biotechnology & Genetic Engineering, Faculty of Life Science, Mawlana Bhashani Science and Technology University, Santosh, Tangail-1902, Bangladesh
    - **[Mohammad Uzzal Hossain](https://www.researchgate.net/profile/Mohammad-Hossain-85)**, **Scientific Officer & Head**, Bioinformatics Division, National Institute of Biotechnology, Ganakbari, Ashulia, Savar, Dhaka-1349, Bangladesh
    ---
    """)
    st.markdown("<h1 style='text-align: center; font-family:Serif; color: black;'>Investigators</h1>", unsafe_allow_html=True)
    st.markdown("""
    - **[Prof. Dr. A.K.M. Mohiuddin] (https://www.researchgate.net/profile/A-K-M-Mohiuddin)**, **Professor**, Department of Biotechnology & Genetic Engineering, Faculty of Life Science, Mawlana Bhashani Science and Technology University, Santosh, Tangail-1902, Bangladesh
    - **[Shahin Mahmud] (https://www.researchgate.net/profile/Shahin-Mahmud-2)**, **Assistant Professor**, Department of Biotechnology & Genetic Engineering, Faculty of Life Science, Mawlana Bhashani Science and Technology University, Santosh, Tangail-1902, Bangladesh
    ---
    """)
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from PIL import Image
import subprocess
import os
import base64
import pickle

MENU_NO = 1

def streamlit_menu(MENU=1):
    if MENU == 1:
        selected = option_menu(
            menu_title=None,  
            options=["Home", "Predict", "About", "Team"], 
            icons=["house", "layer-backward", "file-earmark-text", "people"],  
            menu_icon="none",  
            default_index=0,  
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "black", "font-family": "Times New Roman", "font-size": "21px"},
                "nav-link": {
                    "font-family": "Serif",
                    "font-size": "21px",
                    "text-align": "left",
                    "margin": "1px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "crimson"},
            },
        )
        return selected
  
selected = streamlit_menu(MENU=MENU_NO)

if selected == "Home":     
    # Logo image
    image = Image.open('logo_latest.png')

    st.image(image, use_column_width=True)

    # Page title
    welcome_title = '<p style="font-family:Serif; color:firebrick; font-size: 25px; text-align: center; ">Welcome to <b>M<sup>Pro</sup> <b> pred !</p>'
    st.markdown(welcome_title, unsafe_allow_html=True)
    
    original_subtitle = '<p style="font-family:Serif; color:olive; font-size: 25px; text-align: center; ">Predict bioactivity of compounds against the "Main Protease" of <b>SARS-CoV-2<b></p>'
    st.markdown(original_subtitle, unsafe_allow_html=True)
    
    st.text("")

    predict_title = '<p style="font-family:Serif; color:black; font-size: 20px; text-align: center; ">Go to "<b>Predict</b>" menu to start submission!</p>'
    st.markdown(predict_title, unsafe_allow_html=True)
    
    st.text("")
    st.text("")
    st.text("")
    st.text("")
    
    st.markdown(
    """<a style='font-family:Serif; display: block; text-align: center;' href="https://www.worldometers.info/coronavirus/">COVID-19 Live Update!</a>
    """,
    unsafe_allow_html=True)
    
if selected == "Predict":
     # Logo image
    image = Image.open('logo_latest.png')
    st.image(image, use_column_width=True)
    
    # Molecular descriptor calculator option
    def desc_calc():
        # Performs the descriptor calculation
        bashCommand = "java -Xms2G -Xmx2G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/MACCSFingerprinter.xml -dir ./ -file descriptors_output.csv"
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        os.remove('molecule.smi')

    # File download option
    def filedownload(df):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Download Predictions</a>'
        return href

    # Model building section
    def build_model(input_data):
        # Reads in saved regression model
        load_model = pickle.load(open('Mpro_model.pkl', 'rb'))
        # Apply model to make predictions
        prediction = load_model.predict(input_data)
        st.header('**Prediction results**')
        prediction_output = pd.Series(prediction, name='pIC50')
        molecule_name = pd.Series(load_data[1], name='molecule_name')
        df = pd.concat([molecule_name, prediction_output], axis=1)
        st.write(df)
        st.markdown(filedownload(df), unsafe_allow_html=True)

    # Sidebar setting
    with st.sidebar.header('Data upload section'):
        uploaded_file = st.sidebar.file_uploader("Upload your input file", type=['txt'])
        st.sidebar.markdown("""
    [Example input file](https://raw.githubusercontent.com/Nadimfrds/Mpropred/master/sample_input.txt)
    """)

    if st.sidebar.button('Predict!'):
        load_data = pd.read_table(uploaded_file, sep=' ', header=None)
        load_data.to_csv('molecule.smi', sep = '\t', header = False, index = False)

        st.header('**Your input data**')
        st.write(load_data)

        with st.spinner("Calculating descriptors...wait a while"):
            desc_calc()

        # Read in the calculated descriptors and display the dataframe
        st.header('**Calculated molecular descriptors from your data**')
        desc = pd.read_csv('descriptors_output.csv')
        st.write(desc)
        st.write(desc.shape)

        # Read the descriptor list used in previously built model
        st.header('**Subset of descriptors from MACCS models**')
        Xlist = list(pd.read_csv('lists_of_descriptor.csv').columns)
        desc_subset = desc[Xlist]
        st.write(desc_subset)
        st.write(desc_subset.shape)

        # Apply the trained model to make prediction on query compounds
        build_model(desc_subset)
    else:
        st.info('Upload your input data in the sidebar to start prediction!')
if selected == "About":
    # Logo image
    image = Image.open('logo_latest.png')
    st.image(image, use_column_width=True)
    
    st.markdown("""
    **About the WebApp**
    - The WebApp is developed on **Python**,  **HTML** & **Streamlit** 
    - The Molecular descriptors of compounds were calculated using [PaDEL-Descriptor](http://www.yapcwsoft.com/dd/padeldescriptor/)
    - **MACCS** (Molecular ACCess System) fingerprints were used to measure the molecular similarity of the datasets and query compounds
    - The dataset is comprised of **758** compounds having inhibition efficacy against the **Main Protease**  published in peer-reviewed journals between January 2020 and August 2021
    ---
    **Usage**
    - **Step 1**: Gather SMILES notation of your query compounds of interest from any of the public databases such as [Drugbank](https://go.drugbank.com/), [PubChem](https://pubchem.ncbi.nlm.nih.gov/), [ChemSpider](http://www.chemspider.com/), [ChEMBL](https://www.ebi.ac.uk/chembl/) etc. (alternatively you can draw your compound and generate the SMILES notation from any editors such as [JSME structure editor](https://cactus.nci.nih.gov/gifcreator/editor.html), ChemDraw, ChemAxon MarvinSketch etc.)
    - **Step 2**: Upload your input molecules as SMILES notation in a text (.txt) file containing the SMILES notation and a given name or ID (space separated) by clicking on the **“Browse files”** button. 
    - **Step 3**: Click **“Predict!”** button to start the prediction process
    - **Step 4**: The results are automatically showed in a box found below the **“Prediction results”** heading. You can also download the results as a CSV file by clicking the **“Download Predictions”** button.
    ---
    **About Main Protease**
    - The **Main protease** is considered as one of the most promising drug targets of SARS-CoV-2
    - The protease is essential for processing the polyproteins of SARS-CoV-2 that are translated from the viral RNA 
    - It has 3 domains where the Domain I and Domain II contribute one residue to the catalytic dyad **Cys145** and **His41** which is cruicial for the proteolytic activity
    - Pfizer’s recently developed oral antiviral **PAXLOVID™** (nirmatrelvir [PF-07321332] tablets and ritonavir tablets) is an active **Main protease** inhibitor
    ---
    """)
if selected == "Team":
    # Logo image
    image = Image.open('logo_latest.png')
    st.image(image, use_column_width=True)
    
    st.markdown("<h1 style='text-align: center; font-family:Serif; color: black;'>Developers</h1>", unsafe_allow_html=True)
    st.markdown("""
    - **[Nadim Ferdous](https://www.researchgate.net/profile/Nadim-Ferdous)**, **Senior year student**, Department of Biotechnology & Genetic Engineering, Faculty of Life Science, Mawlana Bhashani Science and Technology University, Santosh, Tangail-1902, Bangladesh
    - **[Mahjerin Nasrin Reza](https://www.researchgate.net/profile/Mahjerin-Nasrin-Reza)**, **Senior year student**, Department of Biotechnology & Genetic Engineering, Faculty of Life Science, Mawlana Bhashani Science and Technology University, Santosh, Tangail-1902, Bangladesh
    - **[Mohammad Uzzal Hossain](https://www.researchgate.net/profile/Mohammad-Hossain-85)**, **Scientific Officer & Head**, Bioinformatics Division, National Institute of Biotechnology, Ganakbari, Ashulia, Savar, Dhaka-1349, Bangladesh
    ---
    """)
    st.markdown("<h1 style='text-align: center; font-family:Serif; color: black;'>Investigators</h1>", unsafe_allow_html=True)
    st.markdown("""
    - **[Prof. Dr. A.K.M. Mohiuddin] (https://www.researchgate.net/profile/A-K-M-Mohiuddin)**, **Professor**, Department of Biotechnology & Genetic Engineering, Faculty of Life Science, Mawlana Bhashani Science and Technology University, Santosh, Tangail-1902, Bangladesh
    - **[Shahin Mahmud] (https://www.researchgate.net/profile/Shahin-Mahmud-2)**, **Assistant Professor**, Department of Biotechnology & Genetic Engineering, Faculty of Life Science, Mawlana Bhashani Science and Technology University, Santosh, Tangail-1902, Bangladesh
    ---
    """)
