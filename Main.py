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

