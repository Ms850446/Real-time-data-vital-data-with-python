import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import serial
import streamlit as st
import time as t
from datetime import datetime
import altair as alt
def plot_animation(df):
    brush = alt.selection_interval()
    chart1 = alt.Chart(df).mark_line().encode(
            x=alt.X('time', axis=alt.Axis(title='time')),
            y=alt.Y('value', axis=alt.Axis(title='value')),
        ).properties(
             width=900,
            height=100
        ).add_selection(
            brush
        )


st.set_page_config(layout='wide')
st.markdown("""
<style>
.css-18ni7ap.e8zbici2
{
    visibility:hidden;
}
.css-qri22k.egzxvld0
{
    visibility:hidden;
}
.css-9s5bis.edgvbvh3
{
    visibility:hidden;
}
.block-container.css-18e3th9.egzxvld2
{
    padding: 1rem 1rem 1rem 1rem;
}
.css-10trblm.e16nr0p30
{
    text-align:center;
    font-family: Arial;
}
.css-hxt7ib.e1fqkh3o4
{
    padding: 0.5rem 1rem 0rem 1rem;
}
.css-81oif8.effi0qh3
{
    font-size:16px;
}
.css-1p46ort.effi0qh3 {
    font-size: 1px;
    color: rgb(49, 51, 63);
    display: flex;
    visibility: hidden;
    margin-bottom: 0rem;
    height: auto;
    min-height: 0rem;
    vertical-align: middle;
    flex-direction: row;
    -webkit-box-align: center;
    align-items: center;
}
.css-k8kh4s {
    font-size: 1px;
    color: rgba(49, 51, 63, 0.4);
    display: flex;
    visibility: hidden;
    margin-bottom: 0rem;
    height: auto;
    min-height: 0rem;
    vertical-align: middle;
    flex-direction: row;
    -webkit-box-align: center;
    align-items: center;
}
</style>
""", unsafe_allow_html=True)



if 'arduino' in st.session_state:
    st.session_state.arduino.close()


def cb_live_active():
    st.session_state.cb_live = True
    st.session_state.cb_sig1 = False
    st.session_state.cb_sig2 = False


def cb_sig1_active():
    st.session_state.cb_live = False
    st.session_state.cb_sig1 = True
    st.session_state.cb_sig2 = False


def cb_sig2_active():
    st.session_state.cb_live = False
    st.session_state.cb_sig1 = False
    st.session_state.cb_sig2 = True





with st.container():
    b1, b2, b3 = st.columns(3)
    cb_live = b1.checkbox("Live Signal", key='cb_live',
                          on_change=cb_live_active)
    cb_sig1 = b2.checkbox("Signal 1", key='cb_sig1',
                          on_change=cb_sig1_active)
    cb_sig2 = b3.checkbox("Signal 2", key='cb_sig2', on_change=cb_sig2_active)


    right_up_col, left_up_col = st.columns([3, 1])
    uploaded_csv = left_up_col.file_uploader("Upload your CSV file", type={"csv", "txt", "csv.xls"},
                                             label_visibility='collapsed', key="file")

   
    if uploaded_csv is not None:
        uploaded_df = pd.read_csv(uploaded_csv)
        csv_data = uploaded_df.to_numpy()
        time = csv_data[:, 0]
        magnitude = csv_data[:, 1]
        if cb_sig1:
            
            meanOfMagnitude=np.mean(magnitude)
            meanOfR=0
            i=1
            length =len(magnitude)-len(magnitude)%20
            for index in range(0,length-20,20):
                max =np.max(magnitude[index:index+1])
                min =np.min(magnitude[index:index+1])
                meanOfR+=(max-min)
            numberOfR=len(magnitude)/20
            meanOfR=meanOfR/numberOfR
            df=pd.DataFrame({'time':time,'value':magnitude},columns=['time','value'])
            lines = plot_animation(df)
            line_plot = st.altair_chart(lines)
            col1, col2 = st.columns(2)
            start_btn = col1.button('Start')
            if start_btn:
                N = df.shape[0]  # number of elements in the dataframe
                burst = 1  # number of elements (months) to add to the plot
                size = burst  # size of the current dataset
            for i in range(1, N):
                step_df =df.iloc[0:size]
                lines = plot_animation(step_df)
                line_plot = line_plot.altair_chart(lines)
                size = i + burst
                if size >= N:
                    size = N - 1

            fig_sig1 = px.line(uploaded_df, x=time,
                               y=magnitude, title="Signal2")
            fig_sig1.add_hline(meanOfMagnitude+0.577*meanOfR, color='red', linestyle='dashed')
            fig_sig1.add_hline(meanOfMagnitude-0.577*meanOfR, color='red', linestyle='dashed')
            fig_sig1.add_hline((meanOfMagnitude), color='blue')

            chart = st.line_chart(
                np.zeros(shape=(1, 1)), height=500, width=1200, use_container_width=False)

            i = 0
            for index in range(0, len(magnitude), 10):
                chart.add_rows(magnitude[i*10:10*(i+1)])
                t.sleep(2)
                i += 1





        if cb_sig2:

            fig_sig2 = px.line(uploaded_df, x=time,
                               y=magnitude, title="Signal2")
            chart = st.line_chart(
                np.zeros(shape=(1, 1)), height=500, width=1200, use_container_width=False)

            i = 0
            for index in range(0, len(magnitude), 10):
                chart.add_rows(magnitude[i*10:10*(i+1)])
                t.sleep(0.05)
                i += 1



        if cb_live:
            
            arduino=serial.Serial(port='COM16', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,bytesize=8)
                                    # bytesize=serial.EIGHTBITS)  # Change the COM port to whichever port your arduino is in
            st.session_state.arduino=arduino

            gauge_placeholder = st.empty()
            chart_placeholder = st.empty()

            def temp_gauge(temp, previous_temp, gauge_placeholder):
                fig = go.Figure(go.Indicator(
                    domain={'x': [0, 1], 'y': [0, 1]},
                    value=temp,
                    mode="gauge+number+delta",
                    title={'text': "Temperature (°C)"},
                    delta={'reference': previous_temp},
                    gauge={'axis': {'range': [0, 40]}}))

                gauge_placeholder.write(fig)

            def temp_chart(df, chart_placeholder):
                fig = px.line(df, x="Time", y="Temperature (°C)",
                              title='Temperature vs. time')
                chart_placeholder.write(fig)

            if arduino.isOpen() == False:
                arduino.open()

            i = 0
            previous_temp = 0
            temp_record = pd.DataFrame(
                data=[], columns=['Time', 'Temperature (°C)'])

            while i < 50000000:  # Change number of iterations to as many as you need
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                try :
                    temp =float(arduino.readline().decode().strip('\r\n'))
                except:
                    temp=0
                    
                temp_record.loc[i, 'Time'] = current_time
                temp_record.loc[i, 'Temperature (°C)'] = temp

                temp_gauge(temp, previous_temp, gauge_placeholder)
                temp_chart(temp_record, chart_placeholder)
                
                i += 1
                previous_temp = temp
                # t.sleep(0.1)

            temp_record.to_csv('temperature_record.csv', index=False)
            






# import serial
# import time
# import streamlit as st
# import plotly.graph_objects as go
# import plotly.express as px
# from datetime import datetime
# import pandas as pd

# arduino = serial.Serial(port='COM16', baudrate=9600, parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS) #Change the COM port to whichever port your arduino is in
# gauge_placeholder = st.empty()
# chart_placeholder = st.empty()

# def temp_gauge(temp,previous_temp,gauge_placeholder):
#     fig = go.Figure(go.Indicator(
#         domain = {'x': [0, 1], 'y': [0, 1]},
#         value = temp,
#         mode = "gauge+number+delta",
#         title = {'text': "Temperature (°C)"},
#         delta = {'reference': previous_temp},
#         gauge = {'axis': {'range': [0, 40]}}))

#     gauge_placeholder.write(fig)

# def temp_chart(df,chart_placeholder):
#     fig = px.line(df, x="Time", y="Temperature (°C)", title='Temperature vs. time')
#     chart_placeholder.write(fig)

# if arduino.isOpen() == False:
#     arduino.open()

# i = 0
# previous_temp = 0
# temp_record = pd.DataFrame(data=[],columns=['Time','Temperature (°C)'])

# while i < 500: #Change number of iterations to as many as you need
#     now = datetime.now()
#     current_time = now.strftime("%H:%M:%S")

#     try:
#         temp = round(float(arduino.readline().decode().strip('\r\n')),1)
#     except:
#         temp=0
#         pass

#     temp_record.loc[i,'Time'] = current_time
#     temp_record.loc[i,'Temperature (°C)'] = temp

#     temp_gauge(temp,previous_temp,gauge_placeholder)
#     temp_chart(temp_record,chart_placeholder)
#     time.sleep(1)
#     i += 1
#     previous_temp = temp

# temp_record.to_csv('temperature_record.csv',index=False)

# if arduino.isOpen() == True:
#     arduino.close()










