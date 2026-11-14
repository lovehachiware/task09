import csv
import streamlit as st
import folium
from streamlit_folium import st_folium


graph = {}

with open("subway.csv", encoding="utf-8-sig") as f:
    for a, b, time in csv.reader(f):
        if a not in graph:
            graph[a] = {}
        if b not in graph:
            graph[b] = {}

        graph[a][b] = int(time)
        graph[b][a] = int(time)


location = {}

with open("subwayLocation.csv", encoding="utf-8-sig") as f:
    for name, lat, lon in csv.reader(f):
        location[name] = [float(lat), float(lon)]


def shortest_path(start, end):
    nodes = set(graph)
    cost = {}

    for node in nodes:
        cost[node] = [float("inf"), None]

    cost[start][0] = 0

    while nodes:
        curNode = None
        mini = float("inf")

        for node in nodes:
            if cost[node][0] < mini:
                mini = cost[node][0]
                curNode = node

        if curNode is None:
            return None, []

        if curNode == end:
            break

        nodes.remove(curNode)

        for node in graph[curNode]:
            new_time = cost[curNode][0] + graph[curNode][node]

            if new_time < cost[node][0]:
                cost[node][0] = new_time
                cost[node][1] = curNode

    path = [end]

    while path[-1] != start:
        path.append(cost[path[-1]][1])

    path.reverse()
    return cost[end][0], path


st.title("지하철 최단 경로")

stations = sorted(graph)
start = st.selectbox("출발역", stations, index=stations.index("서울역(1)"))
end = st.selectbox("도착역", stations, index=stations.index("강남(2)"))

if st.button("경로 검색"):
    minutes, path = shortest_path(start, end)

    if path:
        st.write(f"소요 시간: {minutes}분")
        st.write(" → ".join(path))

        points = []
        for station in path:
            name = station.rsplit("(", 1)[0]
            points.append(location[name])

        m = folium.Map(location=points[0], zoom_start=15)

        if len(points) > 1 and points[0] != points[-1]:
            folium.PolyLine(points, color="red", weight=4).add_to(m)
            m.fit_bounds(points, padding=(25, 25))

        for station, point in zip(path, points):
            folium.CircleMarker(
                location=point,
                radius=4,
                color="blue",
                fill=True,
                tooltip=station
            ).add_to(m)

        st_folium(m, height=450, returned_objects=[])
    else:
        st.write("연결된 경로가 없습니다.")