"""Name: Tristan Palazzo
CS230: Section 001
Data: MA Crash Data
Description:
This program analyzes the 2017 Motor Vehicle Crashes in MA 
from the Massachusetts Department of Transportation. I examined 
a 10,000-record sample of the 145,068 total reported crashes.
My queries look to gain insight on how location, age, and type of crash
play a role within MA crashes. 
"""

#Importing various packages for databases and visualization
import pandas as pd
import numpy as np
import pydeck as pdk
import streamlit as st
import matplotlib.pyplot as plt
     #This is for the horizontal option menu displayed throughout the website.
     #package needs to be added manually first: 
     #(https://discuss.streamlit.io/t/streamlit-option-menu-is-a-simple-streamlit-component-that-)allows-users-to-select-a-single-item-from-a-list-of-options-in-a-menu/20514
from streamlit_option_menu import option_menu

#Loads the csv file which we will be using throughout. Note: There were around 100 columns so I used
#"usecols" to only get what I found interesting
def loadData():
    df = pd.read_csv('FinalCSV_2017_Crashes_10000_sample.csv',
                     header=0,
                     usecols=['CITY_TOWN_NAME',
                            'CRASH_SEVERITY_DESCR', 'MAX_INJR_SVRTY_CL', 'NUMB_VEHC',    
                            'NUMB_NONFATAL_INJR','NUMB_FATAL_INJR',   
                            'MANR_COLL_DESCR', 'AMBNT_LIGHT_DESCR', 'WEATH_COND_DESCR',   
                            'ROAD_SURF_COND_DESCR','RDWY', 'LAT', 'LON', 'YEAR','FIRST_HRMF_EVENT_DESCR',
                            'AGE_DRVR_YNGST', 'AGE_DRVR_OLDEST','CNTY_NAME','CITY', 'HIT_RUN_DESCR',  
                            'SPEED_LIMIT', 'WORK_ZONE_RELD_DESCR', 'SURFACE_TP', 'SPEED_LIM'])  
    return df


#Cleans data. Note there were 2 speed limits so I combined them and made a new column

def cleanedData(df):
    df['ROAD_SPEED_LIMIT'] = df['SPEED_LIMIT'].combine_first(df['SPEED_LIM'])
    df_cleaned = df.dropna(subset=['AGE_DRVR_OLDEST'])
    
    return df_cleaned, df

#First Page of Website. contains a header, description, and image
def homePage():

    with st.container():
        st.header("Exploring Massachusetts Motor Vehicle Crashes in 2017")
        st.subheader("This web-based Python application analyzes 2017 Motor Vehicle Crashes in MA "
                    "from the Massachusetts Department of Transportation. "
                    "We examined a 10,000-record sample of the 145,068 total reported crashes.")
        
        st.image("PicOFBostonForPythonCROPPED.jpg", use_column_width=True)
        

#2nd Page. Map of crashes with a filter for the town and the type of crash.
def crashesMap(df):
    
    st.header("Map of Crashes in Different Cities")
    
    #Selection bow with the unique values of the city column using pandas unique
    city = st.selectbox("Select City", sorted(df['CITY'].dropna().unique()))
    
    #Creates a filtered view showing the latitude and longnitude next to each City name
    df_filtered = df[df['CITY'] == city].dropna(subset=['LAT', 'LON'])
    
    #finds the total number of crashes via the number of rows
    total_crashes = len(df_filtered)
    
    if not df_filtered.empty:
        #finds the collision types using pandas unique
        crashTypes = df_filtered['FIRST_HRMF_EVENT_DESCR'].unique()
        
        #SUPER COOL!! uses list comprehension inside of a dictionary to assign 3 random numbers to a type of crash
        #These numbers will later be used with rgb color coding!!
        crashColorDict = {crashtype: [np.random.randint(0, 256) for i in range(3)] for crashtype in
                            crashTypes}
        
        #Puts makes a color row and assigns the rgb list to the designated key
        df_filtered['Color'] = df_filtered['FIRST_HRMF_EVENT_DESCR'].map(crashColorDict)

        selectedType = st.selectbox("Select Crash Type",
                                               ['All'] + list(sorted(df_filtered['FIRST_HRMF_EVENT_DESCR'].unique())))
        if selectedType != 'All':
            df_filtered = df_filtered[df_filtered['FIRST_HRMF_EVENT_DESCR'] == selectedType]
            
            
        #using df_filtered and gets the color using the list assigned
        scatterplot = pdk.Layer(
            "ScatterplotLayer",
            data=df_filtered,
            get_position=["LON", "LAT"],
            get_color="[Color[0], Color[1], Color[2], 255]",
            get_radius=20,
        )
        #creates the view by looking at the average long and lad
        view = pdk.ViewState(
            longitude=df_filtered['LON'].mean(),
            latitude=df_filtered['LAT'].mean(),
            zoom=13
        )
        #Special map(looks nicer :) but doesn't have special properties)
        deck = pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            layers=[scatterplot],
            initial_view_state=view,
        )

        st.pydeck_chart(deck)

    else:
        st.warning("No data available for the selected city.")

#3d page of website. Bar chart of the age of driver in the crash 
 
def crashAges(df):
    st.header("Top Ages to Crash")
    
    topCrashes = df['AGE_DRVR_OLDEST'].value_counts()

    fig, ax = plt.subplots()

    # User can choose the color of the bar graph
    color = st.color_picker("Choose Graph Color:", '#9ed6f7')
    
    ax.bar(topCrashes.index, topCrashes, color=color)
    ax.set_xlabel('Age Range', fontweight='bold', fontsize=12)
    ax.set_ylabel('Count', fontweight='bold', fontsize=12)
    ax.set_title('Top Ages to Crash', fontweight='bold', fontsize=14)
    ax.set_xticks(range(len(topCrashes.index)))
    #labels each bar of the chart by the crashes
    ax.set_xticklabels(topCrashes.index, rotation=30, ha='right', fontsize=10)
    fig.set_facecolor('#dbedff')

    st.pyplot(fig)

#Page 4. Crash type - Barchart & pie chart views
def crashTypes(df):
    st.header("Crash Type Analysis")

    # Sorting the wards in ascending order
    crashlist = sorted(df['MANR_COLL_DESCR'].unique())

    # User selects a ward
    crashtype = st.selectbox("Select Crash Type", crashlist)

    # Filter the df based on the selected ward
    df_filtered = df[df['MANR_COLL_DESCR'] == crashtype]

    # Display information about the selected ward
    st.write("Selected Crash Type:", crashtype)


    if not df_filtered.empty:
        # Bar chart or pie chart showing the percentage of open vs. closed violations
        CrashCounts = df_filtered['HIT_RUN_DESCR'].value_counts()
        labels = CrashCounts.index
        values = CrashCounts.values

        # Plotting the data
        fig, ax = plt.subplots()
        if st.checkbox("Show as Pie Chart"):
            ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#fa6868', '#6cef6d'])
            ax.axis('equal')
        else:
            ax.bar(labels, values, color=['#fa6868', '#6cef6d'])
        
        ax.set_title("Hit and Run Distribution", fontsize=16, fontweight='bold')
        ax.set_xlabel("Hit and Run?", fontsize=14)
        ax.set_ylabel("Count", fontsize=14)
        fig.set_facecolor('#dbedff')

        st.pyplot(fig)
    
#Runs the different functions
def main():
    #Assigns df to the dataframe returned after loading the csv
    df = loadData()
    df_cleaned = cleanedData(df)[0]
    #Coloring for background. Takes a text file with colors and fonts and displays them into the website 
    # youtube video to learn how to do this: (https://www.youtube.com/watch?time_continue=291&v=gr_KyGfO_eU&embeds_referring_euri=https%3A%2F%2Fwww.bing.com%2F&embeds_referring_origin=https%3A%2F%2Fwww.bing.com&source_ve_path=MzY4NDIsMjg2NjY&feature=emb_logo)

    with open('PYFinalAssignColors&Fonts.css') as file:
        css_code = file.read()
        st.markdown(f'<style>{css_code}</style>', unsafe_allow_html=True)
        
        #Horizontal option menu. All info sourced from here: 
        # https://discuss.streamlit.io/t/streamlit-option-menu-is-a-simple-streamlit-component-that-allows-users-to-select-a-single-item-from-a-list-of-options-in-a-menu/20514
        menu_selection = option_menu(None, ['Home Page', "Crash Map", "Crash Ages", "Crash Types"],
                                     orientation='horizontal',
                                     icons=['house', 'map', 'truck-front','house','building'],
                                     default_index=0,
                                     styles={
                                               "options": {"text-align": "center", "font-size": "16px", "font-weight": 100},
                                               "container": {"padding": "5px", "background-color": "#fafafa"},
                                               "icon": {"color": '#00479a', "font-size": "15px", "text-align": "center"},
                                               "nav-link": {"font-size": "18px", "text-align": "center", "margin": "0px",
                                                            "--hover-color": '#d6e9ff'},
                                               "nav-link-selected": {"background-color": '#2b8dff'},
                                                })
        
        #runs each function when the corresponding option menu button is selected
        if menu_selection == "Home Page":
            homePage()
        if menu_selection == "Crash Map":
            crashesMap(df)
        if menu_selection == "Crash Ages":
            crashAges(df_cleaned)
        if menu_selection == "Crash Types":
            crashTypes(df)
          

if __name__ == "__main__":
    main()


