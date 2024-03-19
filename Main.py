import streamlit as st
import pandas as pd 
#uncomment this line for mysql
from query import *

#set page
st.set_page_config(page_title="Bilgi Paneli",page_icon="🌓",layout="wide")
UI()
#####

import streamlit as st
import pandas as pd

def load_data(file):
    if file is not None:
        if file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file)
        elif file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            st.warning("Unsupported file format. Please upload a CSV or Excel file.")
            return None
    else:
        st.warning("No file uploaded. Using default CSV file.")
        df = pd.read_csv("results.csv")
    return df

def main():
    uploaded_file = st.sidebar.file_uploader("Choose a file")
    df = load_data(uploaded_file)

    if df is not None:
        st.write("File loaded successfully.")

        categorical_columns = [col for col in df.columns if df[col].dtype == 'object']

        # Seçim kriterleri için kategorik sütunları oluşturun
        selected_criteria = {}
        for col in categorical_columns:
            selected_criteria[col] = st.sidebar.multiselect(
                label=f"Select {col}",
                options=list(df[col].unique()),  # 'All' seçeneği kaldırıldı
                default=list(df[col].unique())   # Tüm seçenekler varsayılan olarak seçildi
            )

        # Diğer seçenekleri dinamik olarak güncelleyin
        for selected_col, selected_values in selected_criteria.items():
            for col in categorical_columns:
                if col != selected_col:  # Seçilen sütunu güncelleme
                    selected_criteria[col] = st.sidebar.multiselect(
                        label=f"Select {col}",
                        options=list(df[df[selected_col].isin(selected_values)][col].unique()),  # Diğer seçenekleri güncelle
                        default=list(df[df[selected_col].isin(selected_values)][col].unique()),  # Tüm seçenekler varsayılan olarak seçildi
                    )

        # Sütun başlıklarının gösterilip gösterilmeyeceğini belirleyin
        all_columns = df.columns.tolist()
        show_columns = st.sidebar.multiselect(
            label="Select columns to show",
            options=all_columns,
            default=all_columns  # Tüm sütunlar varsayılan olarak seçildi
        )

        # DataFrame'i seçilen kriterlere göre filtreleyin
        filtered_df = df.copy()
        for col, values in selected_criteria.items():
            filtered_df = filtered_df[filtered_df[col].isin(values)]

        # Yalnızca belirli sütunları gösterin
        filtered_df = filtered_df[show_columns]

        st.write(filtered_df)

if __name__ == "__main__":
    main()


#side bar: switcher
gender=st.sidebar.multiselect(
    label="Select Gender",
    options=df["gender"].unique(),
    default=df["gender"].unique(),
    )

stream=st.sidebar.multiselect(
    label="select Stream",
    options=df["stream"].unique(),
    default=df["stream"].unique(),
    )
comment=st.sidebar.multiselect(
    label="select Comment",
    options=df["comment"].unique(),
     default=df["comment"].unique(),
    )


#get selected item

df_selection=df.query(
    "gender==@gender & stream==@stream & comment==@comment"
)

#method to dowload dataframe as excel
@st.cache_resource
def convert_df(dataConvert):
    return dataConvert.to_csv(index=True).encode('utf=8')

with st.expander("⏱ Filter Tabulation"):
 #plot tabulation
 tab=pd.crosstab([df_selection["gender"],df_selection["comment"]],df_selection["stream"],margins=True)
 st.dataframe(tab,use_container_width=True)
 #downloading link
 csv1=convert_df(tab)
 st.download_button("Press to Download",csv1,"yourfile.csv",key='download-csv')


with st.expander("⏱ All Student List"):
 #plot tabulation
 showData=st.multiselect('Filter Now',df_selection.columns,default=["name","gender","history","geography","kiswahili","civics","maths","total","average","grade","comment","rank","stream"])
 st.dataframe(df_selection[showData],use_container_width=True)
 #downloading link
 csv2=convert_df(df_selection[showData])
 st.download_button("Press to Download",csv2,"yourfile.csv",key='download-csv-file')

with st.expander("⏱ Search student by name"):
    text_search=st.text_input("Search by Name",value="",placeholder="Enter name or stream")
    #filter data using mask
    m1=df["stream"].str.contains(text_search)
    m2=df["name"].str.contains(text_search)
    df_search=df[m1 | m2]
    if text_search:
        st.caption(f"results of: {text_search}")
        st.dataframe(df_search,use_container_width=True )
    else:
        text_search=""




