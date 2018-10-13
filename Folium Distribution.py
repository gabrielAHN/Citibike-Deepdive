import folium
import matplotlib.pyplot as plt
import pandas as pd

data1 = pd.read_csv('C:\\Users\\Gabriel Hidalgo\\PycharmProjects\\Maps\\nyc_citi\\201701-citibike-tripdata.csv')
data2 = pd.read_csv('C:\\Users\\Gabriel Hidalgo\\PycharmProjects\\Maps\\nyc_citi\\201702-citibike-tripdata.csv')
data3 = pd.read_csv('C:\\Users\\Gabriel Hidalgo\\PycharmProjects\\Maps\\nyc_citi\\201703-citibike-tripdata.csv')
data4 =pd.read_csv('C:\\Users\\Gabriel Hidalgo\\PycharmProjects\\Maps\\nyc_citi\\201704-citibike-tripdata.csv')
data5 =pd.read_csv('C:\\Users\\Gabriel Hidalgo\\PycharmProjects\\Maps\\nyc_citi\\201705-citibike-tripdata.csv')
data6 =pd.read_csv('C:\\Users\\Gabriel Hidalgo\\PycharmProjects\\Maps\\nyc_citi\\201706-citibike-tripdata.csv')
data7 =pd.read_csv('C:\\Users\\Gabriel Hidalgo\\PycharmProjects\\Maps\\nyc_citi\\201707-citibike-tripdata.csv')
data8 =pd.read_csv('C:\\Users\\Gabriel Hidalgo\\PycharmProjects\\Maps\\nyc_citi\\201708-citibike-tripdata.csv')
data9 =pd.read_csv('C:\\Users\\Gabriel Hidalgo\\PycharmProjects\\Maps\\nyc_citi\\201709-citibike-tripdata.csv')
data10 =pd.read_csv('C:\\Users\\Gabriel Hidalgo\\PycharmProjects\\Maps\\nyc_citi\\201710-citibike-tripdata.csv')
data11 =pd.read_csv('C:\\Users\\Gabriel Hidalgo\\PycharmProjects\\Maps\\nyc_citi\\201711-citibike-tripdata.csv')
data12 =pd.read_csv('C:\\Users\\Gabriel Hidalgo\\PycharmProjects\\Maps\\nyc_citi\\201712-citibike-tripdata.csv')

data = pd.concat([data1,data2,data3,data4,data5,data6,data7,data8,data9,data10,data11,data12],ignore_index=True,sort=False)

a = data['start station id'].value_counts()
a = a.rename_axis('start station id').reset_index(name='start counts')
a = a.sort_values(by=['start station id']).reset_index().drop(columns=['index'])
b = data['end station id'].value_counts()
b = b.rename_axis('end station id').reset_index(name='end counts')
b = b.sort_values(by=['end station id']).reset_index().drop(columns=['index'])
c = data[['start station name','start station id','start station latitude','start station longitude']]
c = c.drop_duplicates('start station id').sort_values(by=['start station id']).reset_index().drop(columns=['index'])

d = pd.concat([a, b,c], axis=1)
d = d.drop(columns=['start station id'])
d = d.dropna().reset_index().drop(columns=['index'])
d['sum counts'] = d["end counts"].add(d["start counts"])

nyc = (40.7128,-74.0060)

m = folium.Map(location=nyc,zoom_start=13, tiles = "Stamen Toner")
trip_sum = folium.FeatureGroup(name = 'Sum of All Trips')

for i in range(0,len(d)):
    colors = ['#ff4d4d', '#6666ff']
    plt.figure(i)
    plt.figure(figsize=(5, 5))
    dis = pd.DataFrame([d.iloc[i]['end counts'], d.iloc[i]['start counts']], index=['end','start'], columns=['Amount'])
    a = dis['Amount'].plot(kind='pie', subplots=False, figsize=(16, 16), fontsize=50, labels=[d.iloc[i]['end counts'], d.iloc[i]['start counts']], colors=colors)
    plt.legend( labels=['Trips Ended Here', 'Trips Started Here'], bbox_to_anchor=(0.25, 1),fontsize=40,)
    plt.ylabel('')
    png = 'graphs\\{}.png'.format(i)
    plt.savefig(png)

    radius = (int(d.iloc[i]['sum counts'])/int(d['sum counts'].max()))*10
    if 0.45 <= ((d.iloc[i]['start counts']) / (d.iloc[i]['sum counts'])) <= 0.55:
        color = '#ffff66'
    if (d.iloc[i]['start counts']) / (d.iloc[i]['sum counts']) > 0.55:
        color = '#6666ff'
    if (d.iloc[i]['end counts']) / (d.iloc[i]['sum counts']) > 0.55:
        color = '#ff4d4d'
    popup_text = """<center><div style="border: 7px solid{};border-radius: 15px;"><br>
                        <font size='2' style="font-family:'Raleway', sans-serif;"><b>{}</b></font><br>
                        <font size='2'style="font-family:'Raleway', sans-serif;">Total Trip Station Activity:</font><br>
                        <font size='2' style="font-family:'Raleway', sans-serif;">{}</font><br>
                        <font size='2' style="font-family:'Raleway', sans-serif;"><b>Graph of Station Activity:</b></font><br>
        <img src="https://www.gabrielhn.com/static/images/citi_graph/Pie/{}.png" style='width:175px;height:175px;margin-top:0.5cm;'></div>"""

    popup_text = popup_text.format(color,str(d.iloc[i]['start station name']), str(d.iloc[i]['sum counts']), str(i))
    iframe = folium.IFrame(popup_text, width=250, height=310)
    popup = folium.Popup(iframe, max_width=400)
    trip_sum.add_child(folium.CircleMarker([d.iloc[i]['start station latitude'],d.iloc[i]['start station longitude']],
                  popup = popup,radius= radius, color= color ,fill=True))

m.add_child(trip_sum)

##Top 10 Stations for Activity
ten = d.sort_values(by=['sum counts'],ascending=False)[0:10].reset_index()
used = folium.FeatureGroup(name = 'Top Used Stations')

for i in range(0,len(ten)):
    popup_text = """<center>
                        <font size='2' style="font-family:'Raleway', sans-serif;"><b>{}</b></font><br>
                        <font size='2'style="font-family:'Raleway', sans-serif;">Total Trip Station Activity:</font><br>
                        <font size='2' style="font-family:'Raleway', sans-serif;">{}</font>
                        <br><font size='3' style="font-family:'Raleway', sans-serif;"><b>#{} most used Dock</b></font>"""

    popup_text = popup_text.format(str(ten.iloc[i]['start station name']), str(ten.iloc[i]['sum counts']),(i+1))
    iframe = folium.IFrame(popup_text, width=200, height=95)
    popup = folium.Popup(iframe, max_width=400)
    icon = folium.features.CustomIcon('https://www.gabrielhn.com/static/images/citi_graph/pics/stars.png',icon_size=(18, 20))
    used.add_child(folium.Marker([ten.iloc[i]['start station latitude'],ten.iloc[i]['start station longitude']],icon=icon,popup=popup))

m.add_child(used)


#Start Trip Count
start = folium.FeatureGroup(name = 'Start Trip Station Count',show=False)

for i in range(0,len(d)):
    popup_text = """<center><div style="border: 7px solid #6666ff;border-radius: 15px;"><br>
                        <font size='2' style="font-family:'Raleway', sans-serif;"><b>{}</b></font><br>
                        <font size='2'style="font-family:'Raleway', sans-serif;">Total Trip Station Activity:</font><br>
                        <font size='2' style="font-family:'Raleway', sans-serif;">{}</font><br>
                        <font size='2' style="font-family:'Raleway', sans-serif;"><b>Graph of Station Activity:</b></font><br>
        <img src="https://www.gabrielhn.com/static/images/citi_graph/Pie/{}.png" style='width:175px;height:175px;margin-top:0.5cm;'></div>"""

    popup_text = popup_text.format(str(d.iloc[i]['start station name']), str(d.iloc[i]['start counts']), str(i))
    iframe = folium.IFrame(popup_text, width=250, height=310)
    popup = folium.Popup(iframe, max_width=400)
    radius = (int(d.iloc[i]['start counts'])/int(d['start counts'].max()))*10
    start.add_child(folium.CircleMarker([d.iloc[i]['start station latitude'],d.iloc[i]['start station longitude']],
              popup = popup,radius= radius, color= '#6666ff' ,fill=True))

m.add_child(start)

#End Trip Count
end = folium.FeatureGroup(name = 'End Trip Station Count',show=False)

for i in range(0,len(d)):
    popup_text = """<center><div style="border: 7px solid #ff4d4d;border-radius: 15px;"><br>
                        <font size='2' style="font-family:'Raleway', sans-serif;"><b>{}</b></font><br>
                        <font size='2'style="font-family:'Raleway', sans-serif;">Total Trip Station Activity:</font><br>
                        <font size='2' style="font-family:'Raleway', sans-serif;">{}</font><br>
                        <font size='2' style="font-family:'Raleway', sans-serif;"><b>Graph of Station Activity:</b></font><br>
        <img src="https://www.gabrielhn.com/static/images/citi_graph/Pie/{}.png" style='width:175px;height:175px;margin-top:0.5cm;'></div>"""

    popup_text = popup_text.format(str(d.iloc[i]['start station name']), str(d.iloc[i]['start counts']), str(i))
    iframe = folium.IFrame(popup_text, width=250, height=310)
    popup = folium.Popup(iframe, max_width=400)
    radius = (int(d.iloc[i]['end counts'])/int(d['end counts'].max()))*10
    end.add_child(folium.CircleMarker([d.iloc[i]['start station latitude'],d.iloc[i]['start station longitude']],
              popup = popup,radius= radius, color= '#ff4d4d' ,fill=True))

m.add_child(end)


folium.LayerControl().add_to(m)


m.save('bike_amount.html')
