import streamlit as st

st.set_page_config(page_title="LocA", layout="wide", initial_sidebar_state="auto", menu_items=None)

def about():
    st.title("About")
    st.write("""LocA (Location Analysis) is an app designed to find the best locations for Care Homes across England. We took a shapefile containing the boundaries of the ~300 districts in England, and partitioned them into latitude and longitude coordinates 250m apart, used some clever maths to figure out their nearest features and then some clever machine learning to cluster those districts together. Then we used some more clever maths to figure out which districts have the most care homes and where similar locations without care homes are.
This is the crux of our app. Guiding real estate developers and investors on the best locations to build or buy.""")
    tab1, tab2, tab3= st.tabs(["Team", "Maths", "Model"])
    with tab1:
        st.header("Team - GitHub usernames")
        st.write("willbanny") #add links later
        st.write("oppynate")
        st.write("Mih-Sud")
        st.write("Darius1295")

    with tab2:
        st.header("Maths")
        st.write("It's Clever")
        st.balloons()
    with tab3:
        st.header("Model")
        st.write("K-Means classifier with 100 clusters and standard params. One model is trained on all the 250m spaced grid points across England. A second model is trained on just the London Boroughs for London-specific predictions.")
        st.write("We then predict the group of each care home by supplying the coordinates of actual care homes to the trained clustering model.")
if __name__ == "__main__":
    about()
