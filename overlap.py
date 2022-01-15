from flask import Blueprint, render_template, request
import pandas as pd, folium, numpy as np, random


def citydata(city):
    routes_ = "static/gtfs/" + city + "/routes.csv"
    trips_ = "static/gtfs/" + city + "/trips.csv"
    stops_ = "static/gtfs/" + city + "/stops.csv"
    stop_times_ = "static/gtfs/" + city + "/stop_times.csv"
    ovl_num_ = "static/gtfs/" + city + "/statistics/Overlap_Number.npy"
    ovl_per_ = "static/gtfs/" + city + "/statistics/Overlap_Percentage.npy"
    routes = pd.read_csv(routes_)
    trips = pd.read_csv(trips_)
    stops = pd.read_csv(stops_)
    stops.set_index('stop_id', inplace = True)
    stop_times = pd.read_csv(stop_times_)
    ovl_num = np.load(ovl_num_)
    ovl_per = np.load(ovl_per_)
    return routes, trips, stops, stop_times, ovl_num, ovl_per



def max_ovl(route, thresh, routes, ovl_per):
    max_routes = len(routes)
    l = []
#     print(len(l))
    for i in range(max_routes):
        if i == route: 
            continue
        if ovl_per[route][i] >= thresh:
            l.append((ovl_per[route][i], i))
    # print(l)
    l.sort(key = lambda y : y[0])
    return l


def route_stops(routes, trips, stop_times):
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


def plot_route(r, m, color, flag, route_seq, prp_route, stops, ovl_num, ovl_per):
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
    # print(coor)
    if flag == 0:
        fg.add_child(folium.PolyLine(coor, weight = 3, color = color))
    else:
        folium.PolyLine(coor, weight = 3, color = color).add_to(m)
    if flag == 0:
        m.add_child(fg)

def plot_ovl(ovl, route, stops, routes, trips, stop_times, ovl_per, ovl_num):
    m = folium.Map(location = [28.7041, 77.1025], tiles = "cartodbpositron", zoom_start = 13)
    route_seq = route_stops(routes, trips, stop_times)
    n = len(ovl)
    plot_route(route, m, 'blue', 1, route_seq, route, stops, ovl_num, ovl_per)
    color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])for i in range(n)]
    for i in range(n):
        plot_route(ovl[n - i - 1][1], m, color[i], 0, route_seq, route, stops, ovl_num, ovl_per)
    folium.LayerControl().add_to(m)
    return m._repr_html_()

def wrapper(thresh, route, city):
    routes, trips, stops, stop_times, ovl_num, ovl_per = citydata(city)
    req_list = max_ovl(route, thresh, routes, ovl_per)
    return plot_ovl(req_list, route, stops, routes, trips, stop_times, ovl_per, ovl_num)