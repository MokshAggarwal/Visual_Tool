from flask import Flask, render_template, request
import folium, random, pandas as pd, numpy as np

app = Flask(__name__)

trips = pd.read_csv(r'static\gtfs\Delhi\trips.csv')
routes = pd.read_csv(r'static\gtfs\Delhi\routes.csv')
stops = pd.read_csv(r'static\gtfs\Delhi\stops.csv')
stops.set_index('stop_id', inplace=True)
stop_times = pd.read_csv(r'static\gtfs\Delhi\stop_times.csv')
ovl_num = np.load(r'static\gtfs\Delhi\statistics\Overlap_Number.npy')
ovl_per = np.load(r'static\gtfs\Delhi\statistics\Overlap_Percentage.npy')

def max_ovl(route, thresh):
    max_routes = len(routes)
    l = []
#     print(len(l))
    for i in range(max_routes):
        if i == route: 
            continue
        if ovl_per[route][i] >= thresh:
            l.append((ovl_per[route][i], i))
    # print(l)
    return l

def route_stops():
    route_seq = {}
    max_routes = len(routes)

    for i in range(max_routes):
        route_seq[i] = []

    trp = trips.groupby('route_id')
    stp = stop_times.groupby('trip_id')

    for i in trp.groups:
        t = trp.get_group(i)
        curr_trip = ""
        if len(list(t['trip_id'])) > 0:
                lis = list(t['trip_id'])
                curr_trip = lis[0]
        else:
            continue
        k = stp.get_group(curr_trip)
        stop_seq = list(k['stop_id'])
        route_seq[i] = stop_seq
    return route_seq


def plot_route(r, m, color, flag, route_seq, prp_route):
    fg = folium.FeatureGroup(name = "Route" + str(r), show = False)
    # print(fg)
    ls = route_seq[r]
    coor = [0] * len(route_seq[r])
    txt = "Overlap with Route " + str(r) + ", Number of stops overlapping : " + str(ovl_num[prp_route][r]) + "(" + str(ovl_per[prp_route][r]) + "%)"
    for i in range(len(ls)):
        x = stops.loc[ls[i]]
        if i == 0:
            fg.add_child(folium.Marker([x['stop_lat'], x['stop_lon']], popup = txt))
#         folium.CircleMarker(location = [x['stop_lat'], x['stop_lon']], radius = 5, popup = x['stop_name'], color = color).add_to(m)
        if flag == 0:
            fg.add_child(folium.CircleMarker(location = [x['stop_lat'], x['stop_lon']], radius = 5, popup = x['stop_name'], color = color))
        else:
            folium.CircleMarker(location = [x['stop_lat'], x['stop_lon']], radius = 5, popup = x['stop_name'], color = color).add_to(m)
        coor[i] = (x['stop_lat'], x['stop_lon'])
#     folium.PolyLine(coor, weight=3, color = color).add_to(m)
    print(coor)
    if flag == 0:
        fg.add_child(folium.PolyLine(coor, weight = 3, color = color))
    else:
        folium.PolyLine(coor, weight = 3, color = color).add_to(m)
    if flag == 0:
        m.add_child(fg)


def plot_ovl(ovl, route):
    m = folium.Map(location = [28.7041, 77.1025], tiles = "cartodbpositron", zoom_start = 13)
    route_seq = route_stops()
    n = len(ovl)
    plot_route(route, m, 'blue', 1, route_seq, route)
    color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])for i in range(n)]
    for i in range(n):
        plot_route(ovl[n - i - 1][1], m, color[i], 0, route_seq, route)
    folium.LayerControl().add_to(m)
    return m._repr_html_()



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods = {'POST'})
def get_route():
    route_sel = int(request.form['route'])
    thresh = float(request.form['thresh'])
    ovl = max_ovl(route_sel, thresh)
    return plot_ovl(ovl, route_sel)

if __name__ == "__main__":
    app.run(debug = True)