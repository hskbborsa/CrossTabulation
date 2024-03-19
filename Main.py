import streamlit as st
import pandas as pd 
#uncomment this line for mysql
from query import *

#set page
st.set_page_config(page_title="Bilgi Paneli",page_icon="🌓",layout="wide")

UI()

#uncomment these two lines if using Mysql database
#result=viewData()
#df=pd.DataFrame(result,columns=["name","gender","history","geography","kiswahili","civics","maths","total","average","grade","comment","rank","stream","id"])

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

        selected_criteria = {}
        for col in categorical_columns:
            selected_criteria[col] = st.sidebar.multiselect(
                label=f"Select {col}",
                options=df[col].unique(),
                default=df[col].unique()
            )

        filtered_df = df.copy()
        for col, values in selected_criteria.items():
            filtered_df = filtered_df[filtered_df[col].isin(values)]

        st.write(filtered_df)

if __name__ == "__main__":
    main()





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




if 'df' not in st.session_state:
    df = pd.DataFrame({
        'Animal':['Dog','Dog','Dog','Dog','Cat','Cat','Spider','Spider'],
        'Breed':['bulldog','X','X','asky','Y','Y','asky','asky'],
        'Color':['Brown','Black','Black','Green','Yellow','Brown','White','Black']
    })
    st.session_state.df = df

df = st.session_state.df
df_filtered = df.copy()

# Session state values to track the order of filter selection
if 'confirmed' not in st.session_state:
    st.session_state.confirmed = []
    st.session_state.last_edited = None

def last_edited(i,col):
    '''Update session state values to track order of editing
    
    i:int
        index of the column that was last edited
    col:str
        name of the column that was last edited
    '''
    if st.session_state.last_edited is None: # Nothing was previously selected/edited
        st.session_state.last_edited = (i,col)
        return
    if st.session_state.last_edited == (i,col): # The same column was last edited
        undo(col)
        return
    # Some other column was last edited:
    confirmed(*st.session_state.last_edited)
    st.session_state.last_edited = (i,col)
    return
        
def undo(col):
    '''Undoes the last confirmation if the last edit was to clear a filter

    col : str
        name of the column that was last edited
    '''
    if st.session_state['col_'+col] == []: # Check state of widget by key
        last_confirmed = safe_pop(st.session_state.confirmed,-1)
        st.session_state.last_edited = last_confirmed

def safe_pop(lst, i):
    '''Pops the ith element of a list, returning None if the index is out of bounds
    
    lst : list
        list to pop from
    i : int
        index to pop
    '''
    try:
        return lst.pop(i)
    except IndexError:
        return None

def confirmed(i,col):
    '''Adds the last edited column to the confirmed list
    
    i:int
        index of the column that was last edited
    col:str
        name of the column that was last edited
    '''
    st.session_state.confirmed.append((i,col))

# Columns to display the filters (Streamlit with create multiselect widgets
# according to the order of user edits, but columns will keep them displaying
# in their original order for the user)
cols = st.columns(3)

selected = dict(zip(df.columns, [[],[],[]]))

# Confirmed filters
for i,col in st.session_state.confirmed:
    selected[col] = cols[i].multiselect(
        col, df_filtered[col].unique(), key=f'col_{col}', 
        on_change=last_edited, args=[i,col], disabled=True
    )
    df_filtered = df_filtered[df_filtered[col].isin(selected[col])]

#Currently editing
if st.session_state.last_edited is not None:
    i,col = st.session_state.last_edited
    selected[col] = cols[i].multiselect(
        col, df_filtered[col].unique(), key=f'col_{col}', 
        on_change=last_edited, args=[i,col]
    )
    df_filtered = df_filtered[df_filtered[col].isin(selected[col])]

# Not yet edited filters
for i, col in enumerate(df_filtered.columns):
    if (i,col) not in st.session_state.confirmed and (i,col) != st.session_state.last_edited:
        selected[col] = cols[i].multiselect(
            col, df_filtered[col].unique(), key=f'col_{col}', 
            on_change=last_edited, args=[i,col]
        )
    if selected[col] != []:
        df_filtered = df_filtered[df_filtered[col].isin(selected[col])]

cols = st.columns(2)
cols[0].write(df)
cols[1].write(df_filtered)