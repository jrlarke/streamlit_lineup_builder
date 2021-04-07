import streamlit as st
from lineup_creator import run_creator_app
st.set_page_config(page_title='DFS Lineup Creator',layout='wide')

def main():
    st.title('MMA DraftKings Lineup Creator')

    ### Create a menu ###
    #menu = st.sidebar.selectbox("Menu",["Home","About"])

    ### no options...just make this an MMA lineup builder
    run_creator_app()

if __name__ == '__main__':
    main()
