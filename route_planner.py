"""
公交路径规划算法模块
实现基于综合代价的改进Dijkstra算法，支持省时/少换乘/省钱三种出行模式
"""

import heapq

# ================== 三种出行模式的权重配置 ==================
MODES = {
    "省时": {"w1": 10, "w2": 1, "w3": 1},     # 放大时间权重
    "少换乘": {"w1": 1, "w2": 20, "w3": 1},   # 换乘惩罚极高
    "省钱": {"w1": 1, "w2": 1, "w3": 10}      # 放大票价权重
}


def _edge_cost(edge_attr, mode_weights):
    """
    计算单条边的综合代价
    :param edge_attr: dict, 包含 't'(时间), 'trans'(换乘标记0或1), 'cost'(费用)
    :param mode_weights: dict, 包含 'w1','w2','w3'
    :return: 综合代价值
    """
    w1 = mode_weights['w1']
    w2 = mode_weights['w2']
    w3 = mode_weights['w3']
    return w1 * edge_attr['t'] + w2 * edge_attr['trans'] + w3 * edge_attr['cost']


def _dijkstra(graph, start, mode_weights):
    """
    改进Dijkstra算法，使用综合代价作为距离
    :param graph: 邻接表 {节点: [(邻居, 边属性字典), ...]}
    :param start: 起点站名
    :param mode_weights: 当前模式权重
    :return: (dist字典, prev字典)
    """
    # 初始化所有节点的综合代价为无穷大，前驱为None
    dist = {node: float('inf') for node in graph}
    prev = {node: None for node in graph}
    dist[start] = 0

    # 优先队列元素：(综合代价, 节点)
    pq = [(0, start)]

    while pq:
        cur_cost, u = heapq.heappop(pq)
        # 如果当前取出的代价大于已记录的最优代价，跳过
        if cur_cost > dist[u]:
            continue

        # 遍历所有邻接边
        for v, attr in graph.get(u, []):
            # 计算这条边的综合代价
            e_cost = _edge_cost(attr, mode_weights)
            new_cost = cur_cost + e_cost

            # 发现更优路径
            if new_cost < dist[v]:
                dist[v] = new_cost
                prev[v] = u
                heapq.heappush(pq, (new_cost, v))

    return dist, prev


def _reconstruct_path(prev, start, end):
    """根据prev字典重建从start到end的节点路径"""
    path = []
    curr = end
    while curr is not None:
        path.append(curr)
        curr = prev[curr]
    path.reverse()
    # 如果起点不是路径的第一个节点，说明不可达
    if path[0] != start:
        return []
    return path


def _calc_metrics(path, graph):
    """
    沿着路径计算实际物理指标
    :return: (总耗时, 总换乘次数, 总票价, 换乘站点列表)
    """
    total_time = 0
    total_trans = 0
    total_cost = 0
    transfer_stations = []  # 发生换乘的站点（进入该站点的边trans==1）

    if len(path) < 2:
        return 0, 0, 0, []

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]
        # 从graph中找到对应的边属性
        edge_attrs = None
        for neighbor, attr in graph.get(u, []):
            if neighbor == v:
                edge_attrs = attr
                break
        if edge_attrs is None:
            # 理论上不应发生，除非图数据有误
            raise ValueError(f"路径段 {u}->{v} 在图数据中不存在")

        total_time += edge_attrs['t']
        total_trans += edge_attrs['trans']
        total_cost += edge_attrs['cost']

        # 标记换乘站点：如果进入v的边是换乘边，且v不是终点，则v为换乘点
        if edge_attrs['trans'] == 1 and v != path[-1]:
            transfer_stations.append(v)

    return total_time, total_trans, total_cost, transfer_stations


def find_route(graph, start, end, mode="省时"):
    """
    查询最优路径的主函数
    :param graph: dict, 邻接表路网数据
    :param start: str, 起点站名
    :param end: str, 终点站名
    :param mode: str, 出行模式，可选 "省时" / "少换乘" / "省钱"
    :return: dict {
        '路径': [站点列表],
        '总耗时': int/float,
        '换乘次数': int,
        '总票价': int/float,
        '换乘站点': [列表],
        '综合代价': float
    }
    如果出错，返回 {'error': '错误描述'}
    """
    # 1. 模式校验
    if mode not in MODES:
        return {'error': f"无效的出行模式'{mode}'，请选择：{' / '.join(MODES.keys())}"}

    # 2. 站点存在性检查
    if start not in graph:
        return {'error': f"起点站点 '{start}' 不在路网中"}
    if end not in graph:
        return {'error': f"终点站点 '{end}' 不在路网中"}

    # 3. 同站处理
    if start == end:
        return {
            '路径': [start],
            '总耗时': 0,
            '换乘次数': 0,
            '总票价': 0,
            '换乘站点': [],
            '综合代价': 0
        }

    # 4. 运行改进Dijkstra
    mode_weights = MODES[mode]
    dist, prev = _dijkstra(graph, start, mode_weights)

    # 5. 检查可达性
    if dist.get(end, float('inf')) == float('inf'):
        return {'error': f"无法从 {start} 到达 {end}，请检查路网连通性"}

    # 6. 重建路径
    path = _reconstruct_path(prev, start, end)
    if not path:
        return {'error': '路径重建失败，数据结构可能不一致'}

    # 7. 统计物理指标
    total_time, total_trans, total_cost, transfers = _calc_metrics(path, graph)

    return {
        '路径': path,
        '总耗时': total_time,
        '换乘次数': total_trans,
        '总票价': total_cost,
        '换乘站点': transfers,
        '综合代价': dist[end]
    }


# ==================== 简单测试与示例（可直接运行） ====================
if __name__ == '__main__':
    # 构建一个简单的测试路网供演示
    test_graph = {
        'A': [
            ('B', {'t': 5, 'trans': 0, 'cost': 2}),
            ('C', {'t': 10, 'trans': 0, 'cost': 1})
        ],
        'B': [
            ('A', {'t': 5, 'trans': 0, 'cost': 2}),
            ('D', {'t': 8, 'trans': 1, 'cost': 0}),  # 换乘边
            ('E', {'t': 12, 'trans': 1, 'cost': 1})  # 换乘边
        ],
        'C': [
            ('A', {'t': 10, 'trans': 0, 'cost': 1}),
            ('E', {'t': 7, 'trans': 0, 'cost': 2})
        ],
        'D': [
            ('B', {'t': 8, 'trans': 1, 'cost': 0}),
            ('E', {'t': 4, 'trans': 0, 'cost': 1})
        ],
        'E': [
            ('B', {'t': 12, 'trans': 1, 'cost': 1}),
            ('C', {'t': 7, 'trans': 0, 'cost': 2}),
            ('D', {'t': 4, 'trans': 0, 'cost': 1})
        ]
    }

    print("=== 算法模块自测：A -> E ===")
    for mode_name in ["省时", "少换乘", "省钱"]:
        result = find_route(test_graph, 'A', 'E', mode_name)
        if 'error' in result:
            print(f"[{mode_name}] 错误：{result['error']}")
        else:
            print(f"\n出行模式：{mode_name}")
            print(f"路径：{' -> '.join(result['路径'])}")
            print(f"总耗时：{result['总耗时']} min")
            print(f"换乘次数：{result['换乘次数']}")
            print(f"总票价：{result['总票价']} 元")
            print(f"换乘站点：{result['换乘站点'] if result['换乘站点'] else '无'}")
            print(f"综合代价：{result['综合代价']:.2f}")

    # 测试异常情况
    print("\n=== 异常测试 ===")
    print(find_route(test_graph, 'X', 'A', '省时'))  # 起点不存在
    print(find_route(test_graph, 'A', 'Z', '省时'))  # 终点不存在
    print(find_route(test_graph, 'A', 'E', '极速'))  # 无效模式
    # 移除某条边制造不可达（此处仅演示报错，实际测试时需修改graph）