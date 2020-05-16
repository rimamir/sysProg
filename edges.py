import json
import random

from edge import Edge


class Edges:
    edges_dict = {}

    def __init__(self, start_id):
        self._start_id = start_id
        self._edges = list()

        Edges.edges_dict[self._start_id] = self

    def get_start_id(self):
        return self._start_id

    def add_edge(self, end_id, throughput):
        present_edges = [start_id for start_id in Edges.edges_dict.keys()]

        if end_id not in present_edges:
            return

        present_edges_end_index = [edge.get_end_id() for edge in Edges.edges_dict[end_id].get_edges()]

        if self.get_start_id() == end_id:
            return
        if self.get_start_id() in present_edges_end_index:
            return

        for edge in self.get_edges():
            if edge.get_end_id() == end_id:
                if edge.get_throughput() == throughput:
                    return
                else:
                    edge.set_throughput(throughput)
                    return
        else:
            self._edges.append(Edge(end_id, throughput))


    def get_edges(self):
        return self._edges

    def set_edges(self, new_edges):
        self._edges = list()
        for edge in new_edges:
            self.add_edge(edge.get_end_id(), edge.get_throughput())

    @staticmethod
    def get_all_edges(index):
        adjacent_v = []
        for edge in Edges.edges_dict[index].get_edges():
            adjacent_v.append({'id': edge.get_end_id(),
                               'weight': edge.get_throughput()})

        for edges in Edges.edges_dict.values():
            for edge in edges.get_edges():
                if edge.get_end_id() == index:
                    adjacent_v.append({'id': edges.get_start_id(),
                                       'weight': edge.get_throughput()})
        return adjacent_v

    def print_all_edges(self):
        for edge in self.get_edges():
            print(edge.get_info())

    @classmethod
    def pop_edge(cls, start_id, pop_id):
        cls.edges_dict[start_id]._edges.pop(pop_id)

    @classmethod
    def delete_connected_edges(cls, vertex_id):
        Edges.edges_dict.pop(vertex_id)

        need_to_del = []
        for edges in Edges.edges_dict.values():
            for edge in edges.get_edges():
                if edge.get_end_id() == vertex_id:
                    need_to_del.append([edges.get_start_id(), edges.get_edges().index(edge)])

        for index in need_to_del:
            cls.pop_edge(index[0], index[1])

    @classmethod
    def total_flow(cls, start_id):
        throughput_sum = 0

        for edges in Edges.edges_dict.values():
            for edge in edges.get_edges():
                if edge.get_end_id() == start_id:
                    throughput_sum += edge.get_throughput()

        edges = Edges.edges_dict[start_id].get_edges()

        for edge in edges:
            throughput_sum += edge.get_throughput()

        return throughput_sum

    @classmethod
    def create_json_format(cls):
        json_format = []
        for start_id, edges in cls.edges_dict.items():
            for edge in edges.get_edges():
                json_format.append({'start_id': start_id,
                                    'end_id': edge.get_end_id(),
                                    'throughput': edge.get_throughput()})
        return json_format

    @classmethod
    def fill_from_json(cls, json_file):
        with open(json_file, 'r') as read_file:
            data = json.load(read_file)

        for edge in data['edges']:
            check = False
            start_id = edge['start_id']
            end_id = edge['end_id']
            throughput = edge['throughput']

            for edges in Edges.edges_dict.values():
                for edge in edges.get_edges():
                    if edges.get_start_id() == end_id and edge.get_end_id() == start_id:
                        check = True
                    if edges.get_start_id() == start_id and edge.get_end_id() == end_id:
                        check = True

            if start_id == end_id:
                check = True

            if check:
                continue
            else:
                if start_id in Edges.edges_dict.keys():
                    Edges.edges_dict[start_id].add_edge(end_id, throughput)
                else:
                    Edges(start_id)
                    Edges.edges_dict[start_id].add_edge(end_id, throughput)
