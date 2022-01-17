from flask import Blueprint, render_template, request
import pandas as pd, folium, numpy as np, random, copy

start_coor = {}
start_coor["Delhi"] = [28.7041, 77.1025]
start_coor["Bangalore"] = [12.972442, 77.580643]


def citydata(city):
    routes_ = "static/gtfs/" + city + "/routes.csv"
    trips_ = "static/gtfs/" + city + "/trips.csv"
    stops_ = "static/gtfs/" + city + "/stops.csv"
    stop_times_ = "static/gtfs/" + city + "/stop_times.csv"
    routes = pd.read_csv(routes_)
    trips = pd.read_csv(trips_)
    stops = pd.read_csv(stops_)
    stops.set_index('stop_id', inplace = True)
    stop_times = pd.read_csv(stop_times_)
    return routes, trips, stops, stop_times



def max_ovl(route, thresh, route_seq):
    ovl_per = {}
    ovl_num = {}
    route_seq_ = copy.deepcopy(route_seq)
    r1 = route_seq_[route]
    r1.sort()
    for i in route_seq_.keys():
        if i == route:
            ovl_per[i] = 0
            ovl_num[i] = 0
            continue
        r2 = route_seq_[i]
        if len(r2) == 0:
            ovl_per[i] = 0.0
            continue
        r2.sort()
        score = 0
        i1 = 0
        i2 = 0
        while i1 < len(r1) and i2 < len(r2):
            if r1[i1] == r2[i2]:
                score += 1
                i1 += 1
                i2 += 1
            elif r1[i1] < r2[i2]:
                i1 += 1
            else:
                i2 += 1
        if score <= 1:
            score = 0
        ovl_num[i] = score
        score /= len(r1)
        ovl_per[i] = score * 100.0
    l = []
    for i in route_seq_.keys():
        if i == route:
            continue
        if ovl_per[i] >= thresh:
            l.append((ovl_per[i], i))
    # print(l)
    l.sort(key = lambda y : y[0])
    return l, ovl_per, ovl_num


def route_stops(routes, trips, stop_times):
    route_seq = {}
    max_routes = len(routes)

    for i in routes.index:
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


def plot_route(r, m, color, flag, route_seq, stops, ovl_num, ovl_per):
    fg = folium.FeatureGroup(name = "Route" + str(r), show = False)
    # print(fg)
    ls = route_seq[r]
    coor = [0] * len(route_seq[r])
    txt = "Overlap with Route " + str(r) + ", Number of stops overlapping : " + str(ovl_num[r]) + "(" + str(ovl_per[r]) + "%)"
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

def plot_ovl(ovl, route, stops, routes, trips, stop_times, ovl_per, ovl_num, route_seq, city):
    m = folium.Map(location = start_coor[city], tiles = "cartodbpositron", zoom_start = 13)
    n = len(ovl)
    plot_route(route, m, 'blue', 1, route_seq, stops, ovl_num, ovl_per)
    color = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])for i in range(n)]
    for i in range(n):
        plot_route(ovl[n - i - 1][1], m, color[i], 0, route_seq, stops, ovl_num, ovl_per)
    folium.LayerControl().add_to(m)
    return m._repr_html_()

def wrapper(thresh, route, city):
    routes, trips, stops, stop_times= citydata(city)
    route_seq = route_stops(routes, trips, stop_times)
    req_list, ovl_per, ovl_num = max_ovl(route, thresh, route_seq)
    return plot_ovl(req_list, route, stops, routes, trips, stop_times, ovl_per, ovl_num, route_seq, city)