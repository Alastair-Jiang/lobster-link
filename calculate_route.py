#!/usr/bin/env python3
"""
估算从三元街69号到东财之远楼的地铁路线时间
基于公开的大连地铁信息和步行速度估算
"""

import math

# 坐标估算（基于公开地图数据）
# 注：这些是近似坐标，用于距离计算
SAN_YUAN_STREET = (38.912, 121.593)  # 三元街69号近似坐标
DONG_CAI = (38.882, 121.560)         # 东北财经大学近似坐标
YI_ER_JIU_STATION = (38.915, 121.590)  # 一二九街站
XIAN_ROAD_STATION = (38.912, 121.585)  # 西安路站
XUE_YUAN_STATION = (38.885, 121.558)   # 学苑广场站

def haversine_distance(coord1, coord2):
    """计算两个坐标之间的直线距离（公里）"""
    from math import radians, sin, cos, sqrt, atan2
    
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return 6371 * c  # 地球半径6371km

def estimate_time():
    """估算总行程时间"""
    
    print("=== 从三元街69号到东财之远楼路线估算 ===")
    print()
    
    # 1. 步行到一二九街站
    walk_to_station = haversine_distance(SAN_YUAN_STREET, YI_ER_JIU_STATION)
    walk_time1 = (walk_to_station / 5.0) * 60  # 步行速度5km/h
    
    print(f"1. 步行到一二九街站:")
    print(f"   距离: {walk_to_station:.2f}公里")
    print(f"   时间: {walk_time1:.0f}分钟 (步行速度5km/h)")
    print()
    
    # 2. 地铁行程
    # 一二九街 → 西安路
    station1_to_2 = haversine_distance(YI_ER_JIU_STATION, XIAN_ROAD_STATION)
    metro_time1 = 3  # 1站约3分钟
    wait_time1 = 4   # 平均等车时间
    
    # 西安路换乘
    transfer_time = 5  # 站内换乘步行
    
    # 西安路 → 学苑广场
    station2_to_3 = haversine_distance(XIAN_ROAD_STATION, XUE_YUAN_STATION)
    metro_time2 = 8   # 3站约8分钟
    wait_time2 = 4    # 换乘等车时间
    
    print(f"2. 地铁行程:")
    print(f"   一二九街 → 西安路: 1站, 约{metro_time1}分钟")
    print(f"   等车时间: 约{wait_time1}分钟")
    print(f"   西安路站内换乘: 约{transfer_time}分钟")
    print(f"   西安路 → 学苑广场: 3站, 约{metro_time2}分钟")
    print(f"   换乘等车时间: 约{wait_time2}分钟")
    print(f"   地铁总时间: {metro_time1 + wait_time1 + transfer_time + metro_time2 + wait_time2}分钟")
    print()
    
    # 3. 学苑广场站到之远楼
    walk_to_dest = haversine_distance(XUE_YUAN_STATION, DONG_CAI)
    walk_time2 = (walk_to_dest / 5.0) * 60
    
    print(f"3. 学苑广场站到之远楼:")
    print(f"   距离: {walk_to_dest:.2f}公里")
    print(f"   时间: {walk_time2:.0f}分钟")
    print()
    
    # 总时间
    total_walk = walk_time1 + walk_time2
    total_metro = metro_time1 + wait_time1 + transfer_time + metro_time2 + wait_time2
    total_time = total_walk + total_metro
    
    print("=== 总估算 ===")
    print(f"步行总时间: {total_walk:.0f}分钟")
    print(f"地铁总时间: {total_metro:.0f}分钟")
    print(f"行程总时间: {total_time:.0f}分钟")
    print()
    
    # 保守估计（考虑实际因素）
    conservative_time = total_time * 1.3  # 增加30%缓冲
    
    print("=== 保守估计（考虑实际因素）===")
    print(f"建议预留时间: {conservative_time:.0f}分钟")
    print(f"（包含：找路、拥挤、意外延迟等）")
    print()
    
    # 地铁票价估算
    distance_km = station1_to_2 + station2_to_3
    if distance_km <= 6:
        fare = 2
    elif distance_km <= 12:
        fare = 3
    else:
        fare = 4
    
    print(f"地铁票价估算: {fare}元 (按里程计费)")
    print(f"地铁里程: {distance_km:.1f}公里")

if __name__ == "__main__":
    estimate_time()