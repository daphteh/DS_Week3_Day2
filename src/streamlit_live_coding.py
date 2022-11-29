# Streamlit live coding script
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import pandas as pd
import numpy as np
import streamlit as st
from copy import deepcopy
import json

# First some Data Exploration
@st.cache
def load_data(path):
    dff = pd.read_csv(path)
    return dff

hunde_df_raw = load_data("./data/20200306_hundehalter.csv")
df = deepcopy(hunde_df_raw)

BEV325OD3250_df_raw = load_data("./data/BEV325OD3250.csv")
pop_data = deepcopy(BEV325OD3250_df_raw)

@st.cache
def json_data(path):
    g_data = open(path)
    return g_data

geo_data_raw = json_data('./data/stzh.adm_stadtkreise_a.json')
#geo_data = deepcopy(geo_data_raw)

# Add title and header
st.title("Exploring Zurich's Human and Dog Population")
st.header("Open Data Sourced from the City of Zurich")

# Setting up columns
left_column, right_column = st.columns([1, 1])
# Widgets: checkbox (you can replace st.xx with st.sidebar.xx)

Human_data = left_column.checkbox("Display Human Dataset")
if Human_data:
    st.subheader("Data on People (1998 - 2022)")
    st.dataframe(data=pop_data)

Dog_data = right_column.checkbox("Display Dog Dataset")
if Dog_data:
    st.subheader("Data on Dogs (2020):")
    st.dataframe(data=df)

#Data for Population Data
temp1 = pop_data.groupby(['StichtagDatJahr','StichtagDatMM']).AnzBestWir.sum().to_frame().reset_index()
Pop_over_time =temp1.groupby('StichtagDatJahr').AnzBestWir.mean().to_frame()
Pop_over_time = Pop_over_time.reset_index()
Pop_over_time = Pop_over_time.rename(columns={'StichtagDatJahr': 'Year', 'AnzBestWir':'Total_Pop'})
Pop_over_time = Pop_over_time.reset_index()

temp1 = pop_data.groupby(['StichtagDatJahr','StichtagDatMM','HerkunftLang']).AnzBestWir.sum().to_frame().reset_index()
foreigness_over_time =temp1.groupby(['StichtagDatJahr','HerkunftLang']).AnzBestWir.mean().to_frame().reset_index()
foreigness_over_time = foreigness_over_time.rename(columns={'StichtagDatJahr': 'Year', 'AnzBestWir':'Foreign_Pop'})
foreigness_over_time = foreigness_over_time[(foreigness_over_time['HerkunftLang']=="Ausländer/in")]

over_time = pd.merge(Pop_over_time, foreigness_over_time, left_on='Year', right_on= 'Year')
over_time = over_time.drop(['HerkunftLang'],axis = 1)

#All Measures
fig_all = go.Figure()

fig_all.add_trace(
    go.Scatter(x=over_time['Year'], y=over_time['Total_Pop'], name="Number of People",
               marker={"color": "Red"},
               mode="lines"
              )
)

fig_all.add_trace(
    go.Scatter(x=over_time['Year'], y=over_time['Foreign_Pop'], name="Number of Foreigners",
               marker={"color": "Purple"},
               mode="lines"
              )
)
fig_all.update_layout(height=800, width=800)

fig_all.update_layout(
    title="Economically Active Population Changes Overtime",
    title_x=0.5,
    xaxis_title="Year",
    yaxis_title="# People",
    font=dict(
        family="Arial",
        size=12,
        color="Black"
    )
)

## Only Total Pop
fig_tot = go.Figure()

fig_tot.add_trace(
    go.Scatter(x=over_time['Year'], y=over_time['Total_Pop'], name="Number of People",
               marker={"color": "Red"},
               mode="lines"
              )
)

fig_tot.update_layout(height=800, width=800)

fig_tot.update_layout(
    title="Economically Active Population Changes Overtime",
    title_x=0.5,
    xaxis_title="Year",
    yaxis_title="# People",
    font=dict(
        family="Arial",
        size=12,
        color="Black"
    )
)

#Foreign Measure
fig_foreign = go.Figure()

fig_foreign.add_trace(
    go.Scatter(x=over_time['Year'], y=over_time['Foreign_Pop'], name="Number of Foreigners",
               marker={"color": "Purple"},
               mode="lines"
              )
)
fig_foreign.update_layout(height=800, width=800)

fig_foreign.update_layout(
    title="Economically Active Population Changes Overtime",
    title_x=0.5,
    xaxis_title="Year",
    yaxis_title="# People",
    font=dict(
        family="Arial",
        size=12,
        color="Black"
    )
)
# Widgets: selectbox
measures = ["All"]+sorted(list(over_time.columns.values))
measure = st.selectbox("Choose a Measure", measures)

# Flow control and plotting
if measure == "All":
    st.plotly_chart(fig_all)

if measure == "Total_Pop":
    st.plotly_chart(fig_tot)

if measure == "Foreign_Pop":
    st.plotly_chart(fig_foreign)

# Another header
st.header("Dog Population")

#Data Prep for Dog Chart
df['Count'] = 1
dups = df.groupby(['HALTER_ID']).Count.count().reset_index()
dog_p_owner = dups.groupby('Count').HALTER_ID.count().reset_index()
dog_p_owner = dog_p_owner.rename(columns={"Count": "num_dogs_owned", "HALTER_ID": "num_owners"})
dog_p_owner['logged_owners'] = np.log(dog_p_owner['num_owners'])
fig1 = go.Figure(
    data=[
        go.Bar(name="# Dogs per Owner", x=dog_p_owner['num_dogs_owned'], y=dog_p_owner['logged_owners']),
    ]
)

fig1.add_annotation(
  x=14,  # arrows' head
  y=0,  # arrows' head
  ax=12,  # arrows' tail
  ay=2,  # arrows' tail
  xref='x',
  yref='y',
  axref='x',
  ayref='y',
  text='The maximum # dogs per owner is 14',  # if you want only the arrow
  showarrow=True,
  arrowhead=3,
  arrowsize=1,
  arrowwidth=1,
  arrowcolor='black'
)

fig1.update_layout(height=800, width=800)

fig1.update_layout(
    title="Only 1 Person has 14 Dogs (max)",
    title_x=0.5,
    xaxis_title="# Dogs",
    yaxis_title="Logged # of Owners",
    font=dict(
        family="Arial",
        size=12,
        color="Black"
    )
)

st.plotly_chart(fig1)

# Total Dog Map
df_trial1 = df.groupby('STADTKREIS').count()
df_trial2 = df_trial1[['HALTER_ID']]
df_trial3 = df_trial2.copy()
df_trial3 = df_trial3.rename(columns={'HALTER_ID': 'Tot_Dogs'})
df_trial3 = df_trial3.reset_index()

max_dogs = df_trial3['Tot_Dogs'].max()

f = open('./data/stzh.adm_stadtkreise_a.json')
geo_data_raw = json.load(f)

fig141 = px.choropleth_mapbox(df_trial3, geojson=geo_data_raw,
                      locations='STADTKREIS',
                      color='Tot_Dogs',
                      color_continuous_scale="Oranges",
                      range_color=(0, max_dogs),
                      featureidkey="properties.objid",
                      mapbox_style="carto-positron",
                      opacity=0.5,
                      center = {"lat": 47.3769, "lon": 8.5417},
                    )
fig141.update_layout(margin={"r":0,"t":0,"l":0,"b":0},)
st.plotly_chart(fig141)

url = "https://data.stadt-zuerich.ch/g"
st.write("Data Source:", url)