#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from main_visual_prog_flowchart_tm_backend.planner_extractor import command_line, planner_extractor

def demo_single_plans():
    print("\n=== Demo: Single plans ===")
    single = ["pickup arm1 blue_wire table",
                "insert arm1 blue_wire power_supply_5",
                "putdown arm1 blue_wire power_supply_5",
                "lock arm2 blue_wire power_supply_5"]

    # Build graph
    node, link = [], []
    robots, last_action_node_id_on_each_robot,prev_robot_active, link_id= None, None, "-",0
    for i in range(len(single)):
        node, link, robots, last_action_node_id_on_each_robot,prev_robot_active,link_id  = planner_extractor.AI_plan_to_graph_plan(node, link, single[i],robots, last_action_node_id_on_each_robot, prev_robot_active, link_id)


    print("\nnode:\n")
    print(node)

    print("\nlink:\n")
    print(link)

def demo_multiple_plans():
    print("\n=== Demo: Multiple plans ===")
    multiple = """
(pickup arm1 blue_wire table)
(insert arm1 blue_wire power_supply_5)
(putdown arm1 blue_wire power_supply_5)
(lock arm2 blue_wire power_supply_5)
"""

    # Build graph
    node, link = [], []
    node, link = planner_extractor.AI_plans_to_graph_plans(multiple)

    print("\nnode:\n")
    print(node)

    print("\nlink:\n")
    print(link)



if __name__ == "__main__":
    demo_single_plans()
