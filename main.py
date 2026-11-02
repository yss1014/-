"""
公交路径查询系统 - 主程序
提供控制台交互界面，支持三种出行模式查询和对比
"""

from route_planner import find_route
from graph import graph


def print_separator(title=""):
    """打印分隔线"""
    if title:
        print(f"\n{'='*50}")
        print(f"  {title}")
        print(f"{'='*50}")
    else:
        print("-" * 50)


def print_route(result, mode_name):
    """格式化打印单条路径方案"""
    if 'error' in result:
        print(f"  [{mode_name}] 错误：{result['error']}")
        return

    print(f"\n  【{mode_name}】方案")
    print(f"  路径：{' → '.join(result['路径'])}")
    print(f"  总耗时：{result['总耗时']} 分钟")
    print(f"  换乘次数：{result['换乘次数']} 次")
    print(f"  总票价：{result['总票价']} 元")

    if result['换乘站点']:
        print(f"  换乘站点：{'、'.join(result['换乘站点'])}")
    else:
        print(f"  换乘站点：无（直达线路）")


def show_all_stations():
    """显示所有可用站点"""
    print_separator("可用站点列表")
    stations = list(graph.keys())
    for i, station in enumerate(stations, 1):
        print(f"  {i}. {station}")
    print()


def compare_modes(start, end):
    """一键对比三种模式"""
    print_separator(f"三种模式对比：{start} → {end}")

    for mode in ["省时", "少换乘", "省钱"]:
        result = find_route(graph, start, end, mode)
        print_route(result, mode)

    # 对比总结
    print(f"\n  {'─'*40}")
    print("  对比总结：")
    results = {}
    for mode in ["省时", "少换乘", "省钱"]:
        r = find_route(graph, start, end, mode)
        if 'error' not in r:
            results[mode] = r

    if results:
        best_time = min(results.items(), key=lambda x: x[1]['总耗时'])
        best_trans = min(results.items(), key=lambda x: x[1]['换乘次数'])
        best_cost = min(results.items(), key=lambda x: x[1]['总票价'])

        print(f"  ⏱ 最快方案：【{best_time[0]}】耗时 {best_time[1]['总耗时']} 分钟")
        print(f"  🔄 最少换乘：【{best_trans[0]}】换乘 {best_trans[1]['换乘次数']} 次")
        print(f"  💰 最省钱：【{best_cost[0]}】花费 {best_cost[1]['总票价']} 元")


def main():
    """主菜单循环"""
    while True:
        print_separator("哈尔滨公交路径查询系统")
        print("  1. 查看所有站点")
        print("  2. 单模式查询（选择出行偏好）")
        print("  3. 三种模式一键对比")
        print("  0. 退出系统")
        print("-" * 50)

        choice = input("  请输入选项：").strip()

        if choice == '0':
            print("\n  感谢使用，再见！")
            break

        elif choice == '1':
            show_all_stations()

        elif choice == '2':
            print()
            start = input("  请输入起点站名：").strip()
            end = input("  请输入终点站名：").strip()
            print("  请选择出行模式：1-省时  2-少换乘  3-省钱")
            mode_choice = input("  请输入模式编号：").strip()

            mode_map = {'1': '省时', '2': '少换乘', '3': '省钱'}
            if mode_choice not in mode_map:
                print("  ⚠ 无效的模式编号！")
                continue

            mode = mode_map[mode_choice]
            result = find_route(graph, start, end, mode)
            print_separator("查询结果")
            print_route(result, mode)

        elif choice == '3':
            print()
            start = input("  请输入起点站名：").strip()
            end = input("  请输入终点站名：").strip()
            compare_modes(start, end)

        else:
            print("  ⚠ 无效选项，请重新输入！")

        input("\n  按回车键继续...")


if __name__ == '__main__':
    main()