import tkinter as tk
import json
import copy
import random

# Secondary classes
from vertex import Vertex
from router import Router
from edges import Edges
from edge import Edge


def fill_all_data():
    Router.fill_from_json('data.json')
    Vertex.fill_from_json('data.json')
    Edges.fill_from_json('data.json')
    Vertex.update_routers()


load_matrix = dict()


def fill_load_matrix():
    for vertex in Vertex.vertex_dict.values():
        load_matrix[vertex.get_id()] = list()
        for edge in vertex.get_edges_class().get_edges():
            load_matrix[vertex.get_id()].append({'end': edge.get_end_id(),
                                                 'weight': random.randint(5, 100)})


def save_all_data_exit():
    data = dict()
    data['routers'] = Router.create_json_format()
    data['edges'] = Edges.create_json_format()
    data['vertex'] = Vertex.create_json_format()

    with open('data.json', 'w') as write_file:
        json.dump(data, write_file)
    root.destroy()


fill_all_data()
fill_load_matrix()
print(load_matrix)

root = tk.Tk()


class MainWindow:
    def __init__(self):
        root.title('Main')
        draw_button = tk.Button(root, text='Draw', width=10, height=2,
                                command=lambda: DrawWindow(root)).grid(row=0,
                                                                       column=0)
        vertexes_button = tk.Button(root, text='Edit vertexes',
                                    width=10, height=2,
                                    command=lambda: VertexesWindow(root)).grid(row=0,
                                                                               column=1)
        edges_button = tk.Button(root, text='Edit edges',
                                 width=10, height=2,
                                 command=lambda: EdgesWindow(root)).grid(row=0,
                                                                         column=2)

        id_entry = tk.Entry(root, width=8)
        id_entry.grid(row=1,
                      column=0)

        node_info_button = tk.Button(root, text='Vertex info',
                                     width=10, height=2,
                                     command=lambda: VertexInfo(root, int(id_entry.get()))).grid(row=1,
                                                                                                 column=1)
        routers_button = tk.Button(root, text='Routers',
                                   width=10, height=2,
                                   command=lambda: RoutersWindow(root)).grid(row=1,
                                                                             column=2)

        tk.Label(root, text='-----------------------------------', fg='silver') \
            .grid(row=2, columnspan=3)

        tk.Label(root, text='Start id').grid(row=3, column=0)
        tk.Label(root, text='End id').grid(row=3, column=1)
        start_entry = tk.Entry(root, width=9)
        start_entry.grid(row=4, column=0)
        end_entry = tk.Entry(root, width=9)
        end_entry.grid(row=4, column=1)
        draw_optimal = tk.Button(root, text='Draw path',
                                 command=lambda: DrawWindowWithDejikstra(root,
                                                                         start_id=int(start_entry.get()),
                                                                         end_id=int(end_entry.get())))
        draw_optimal.grid(row=4, column=2)

        tk.Label(root, text='-----------------------------------', fg='silver') \
            .grid(row=5, columnspan=3)

        draw_min_spanning_tree = tk.Button(root, command=lambda: DrawMinSpanningTree(root),
                                           text='Minimum spanning tree', height=2)
        draw_min_spanning_tree.grid(row=6, columnspan=2)

        load_matrix_b = tk.Button(root, command=lambda: LoadMatrix(root),
                                  text='Load matrix', height=2)
        load_matrix_b.grid(row=6, column=2)

        calc_throughput = tk.Button(root,
                                    text='Calculate throughput', height=2)
        calc_throughput.grid(row=7, columnspan=2)

        # saving data
        root.protocol('WM_DELETE_WINDOW', save_all_data_exit)
        root.mainloop()


class DrawWindow:
    """Window with Graph"""

    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title('Draw')
        self.draw_panel = tk.Canvas(self.window, width=800, height=800, bg='white')
        self.draw_panel.grid(row=0, column=0)

        self.draw_edges()
        self.draw_vertexes()

    def draw_vertexes(self, *args):
        """Draw vertexes on Canvas(self.draw.panel)"""
        for vertex in Vertex.vertex_dict.values():
            x, y = vertex.get_xy()
            self.draw_panel.create_oval(x - 10, y - 10, x + 10, y + 10, fill='black')
            self.draw_panel.create_text(x, y, text=vertex.get_id(), fill='white')
            self.draw_panel.create_text(x - 18, y - 18, text=str(vertex.get_router().get_throughput()) + 'Mb/s',
                                        fill='red')

    def draw_edges(self, *args):
        """Draw all edges on Canvas"""
        for vertex in Vertex.vertex_dict.values():
            v_edges = vertex.get_edges_class()
            edges = v_edges.get_edges()

            for edge in edges:
                start_x, start_y = vertex.get_xy()
                end_x, end_y = Vertex.vertex_dict[edge.get_end_id()].get_xy()
                self.draw_panel.create_line(start_x, start_y, end_x, end_y)
                self.draw_panel.create_text((start_x + end_x) / 2, (start_y + end_y) / 2,
                                            text=str(edge.get_throughput()) + 'Mb/s', fill='blue2')


class DrawWindowWithDejikstra(DrawWindow):
    def __init__(self, root_d, start_id=0, end_id=0):
        self.optimal_road = self.determine_path(start_id=start_id, end_id=end_id)

        # self.draw_edges()

        super().__init__(root_d)

    def draw_vertexes(self):
        """Draw vertexes on Canvas(self.draw.panel)"""
        for vertex in Vertex.vertex_dict.values():
            if vertex.get_id() in self.optimal_road:
                x, y = vertex.get_xy()
                self.draw_panel.create_oval(x - 10, y - 10, x + 10, y + 10, fill='black')
                self.draw_panel.create_text(x, y, text=vertex.get_id(), fill='white')
                # self.draw_panel.create_text(x - 18, y - 18, text=str(vertex.get_router().get_throughput()) + 'Mb/s',
                #                             fill='red')

    def draw_edges(self, *args):
        points = list()
        for o_vertex in self.optimal_road:
            for vertex in Vertex.vertex_dict.values():
                if vertex.get_edges_class().get_start_id() == o_vertex:
                    points.append(vertex.get_xy())

            for i in range(len(points) - 1):
                start_x, start_y = points[i]
                end_x, end_y = points[i + 1]

                self.draw_panel.create_line(start_x, start_y, end_x, end_y,
                                            arrow=tk.LAST, arrowshape="10 25 10",
                                            fill='blue', dash=(10, 5), width=2)

    @staticmethod
    def determine_path(start_id=None, end_id=None):
        all_weight = dict()

        for vertex in Vertex.vertex_dict.values():
            all_weight[vertex.get_id()] = Edges.get_all_edges(index=vertex.get_id())

        # for index, weight in all_weight.items():
        #     print(index, weight)
        # print('_______________________')

        views = {vertex: False for vertex in all_weight.keys()}

        # for index, view in views.items():
        #     print(index, view)
        # print('_______________________')

        total_weight = {vertex: {'weight': float('inf'), 'path': list()} if vertex != start_id
        else {'weight': 0, 'path': list()}
                        for vertex in all_weight.keys()}

        # for index, weight in total_weight.items():
        #     print(index, weight)
        # print('_______________________')

        total_weight[start_id]['path'] = [start_id, ]

        cur_min = float('inf')
        cur_index = None

        for i in range(len(all_weight.keys())):
            for index, vertex in total_weight.items():
                if vertex['weight'] < cur_min and views[index] is not True:
                    cur_min = vertex['weight']
                    cur_index = index

            try:
                for vertex in all_weight[cur_index]:
                    new_weight = total_weight[cur_index]['weight'] + vertex['weight']
                    if total_weight[vertex['id']]['weight'] > new_weight:
                        total_weight[vertex['id']]['weight'] = new_weight

                        list_v = total_weight[cur_index]['path']
                        new_path = copy.deepcopy(list_v)
                        new_path.append(vertex['id'])

                        total_weight[vertex['id']]['path'] = new_path
            except KeyError:
                continue

            views[cur_index] = True
            cur_min = float('inf')
            cur_index = None

        # for index, weight in total_weight.items():
        #     print(index, weight)
        # print('_______________________')

        return total_weight[end_id]['path']


class DrawMinSpanningTree(DrawWindow):
    def __init__(self, root_s):
        self.all_edges = sorted(self.edges_list(), key=lambda x: x[2])
        self.min_edges = self.kruskal_algorithm(self.all_edges)

        super().__init__(root_s)

    def draw_vertexes(self, *args):
        """Draw vertexes on Canvas(self.draw.panel)"""
        for vertex in Vertex.vertex_dict.values():
            x, y = vertex.get_xy()
            self.draw_panel.create_oval(x - 10, y - 10, x + 10, y + 10, fill='black')
            self.draw_panel.create_text(x, y, text=vertex.get_id(), fill='white')

    def draw_edges(self, *args):
        for edge in self.min_edges[0]:
            start_x, start_y = Vertex.vertex_dict[edge[0]].get_xy()
            end_x, end_y = Vertex.vertex_dict[edge[1]].get_xy()
            self.draw_panel.create_line(start_x, start_y, end_x, end_y)
            # self.draw_panel.create_text((start_x + end_x) / 2, (start_y + end_y) / 2,
            #                             text=str(str(edge[2]) + 'Mb/s'), fill='blue2')

    @staticmethod
    def edges_list():
        result = list()
        for vertex in Vertex.vertex_dict.values():
            edges = vertex.get_edges_class()
            for edge in edges.get_edges():
                result.append([edges.get_start_id(), edge.get_end_id(), edge.get_throughput()])
        return result

    @staticmethod
    def kruskal_algorithm(edges):
        result = list()
        comp = [i for i in range(len(Vertex.vertex_dict))]
        ans = 0
        for start, end, weight in edges:
            if comp[start] != comp[end]:
                ans += weight
                a = comp[start]
                b = comp[end]

                result.append([start, end, weight])

                for i in range(len(Vertex.vertex_dict)):
                    if comp[i] == b:
                        comp[i] = a
        return result, ans


class VertexesWindow:
    """Window for working with nodes"""

    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title('Vertexes')

        self.entry_dict = dict()
        self.create_entry()

        self.add_label = tk.Label(self.window, text='Enter new vertex:').grid(row=len(Vertex.vertex_dict), column=0)
        self.x_entry = tk.Entry(self.window, width=10)
        self.x_entry.grid(row=len(Vertex.vertex_dict), column=1)

        self.y_entry = tk.Entry(self.window, width=10)
        self.y_entry.grid(row=len(Vertex.vertex_dict), column=2)

        self.add_button = tk.Button(self.window,
                                    width=10, height=1,
                                    text='Add',
                                    command=self.add_vertex)

        self.add_button.grid(row=len(Vertex.vertex_dict) + 1, column=1)

        self.edit_button = tk.Button(self.window,
                                     width=10, height=1,
                                     text='Edit',
                                     command=self.edit_vertex)

        self.edit_button.grid(row=len(Vertex.vertex_dict) + 1, column=2)

        self.delete_button = tk.Button(self.window,
                                       width=10, height=1,
                                       text='Delete',
                                       command=self.delete_vertex)

        self.delete_button.grid(row=len(Vertex.vertex_dict) + 1, column=3)

    def create_entry(self):
        """Creates a multiple Entry with node coordinates"""

        # Index - порядковый номер, vertex[0] - vertex id, vertex[1] - vertex obj
        for index, vertex in enumerate(Vertex.vertex_dict.items()):
            id_label = tk.Label(self.window, text=f'Id: {vertex[1].get_id()}').grid(row=index, column=0)

            x_entry = tk.Entry(self.window, width=10)
            x_entry.insert(0, vertex[1].get_x())

            y_entry = tk.Entry(self.window, width=10)
            y_entry.insert(0, vertex[1].get_y())

            throughput_entry = tk.Label(self.window, text=vertex[1].get_router().get_throughput())

            self.entry_dict[vertex[0]] = [x_entry, y_entry]

            x_entry.grid(row=index, column=1)
            y_entry.grid(row=index, column=2)
            throughput_entry.grid(row=index, column=3)

    def add_vertex(self):
        """Creates two entry fields for adding new node"""
        x = int(self.x_entry.get())
        y = int(self.y_entry.get())
        Vertex(x, y)
        self.window.destroy()

    def edit_vertex(self):
        """Save all edits(vertex coordinates)"""
        for index, entry in self.entry_dict.items():
            entry_x = int(entry[0].get())
            entry_y = int(entry[1].get())

            vertex_x = Vertex.vertex_dict[index].get_x()
            vertex_y = Vertex.vertex_dict[index].get_y()

            if entry_x != vertex_x or entry_y != vertex_y:
                Vertex.vertex_dict[index].set_xy(entry_x, entry_y)

        self.window.destroy()

    def delete_vertex(self):
        """Checks the differences in entry and nodes_dict(Node)"""
        delete_list = list()
        for index, entry in self.entry_dict.items():
            entry_x = entry[0].get()
            entry_y = entry[1].get()

            if entry_x == 'd' or entry_y == 'd':
                delete_list.append(index)

        for i in delete_list:
            self.entry_dict.pop(i)
            Vertex.vertex_dict.pop(i)
            Edges.delete_connected_edges(i)
            Vertex.update_routers()

        self.window.destroy()


class EdgesWindow:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title('Edges')
        self.label = tk.Label(self.window, text='Enter comma-separated edges :)').grid(row=0, columnspan=2)
        self.save_button = tk.Button(self.window, text='Save', command=self.save_changes)
        self.entry_dict = dict()

        self.create_entry()
        self.save_button.grid(row=len(self.entry_dict) + 1, columnspan=2)

    def create_entry(self):
        """Create entry fields for inserting in window"""
        for index, vertex in enumerate(Vertex.vertex_dict.items()):
            id_label = tk.Label(self.window, text=f'Edges : {vertex[1].get_id()}').grid(row=index + 1, column=0)
            entry = tk.Entry(self.window)
            entry.insert(0, self.form_text(vertex[1].get_edges_class().get_edges()))
            entry.grid(row=index + 1, column=1)
            self.entry_dict[vertex[1].get_id()] = entry

    def save_changes(self):
        for index, entry in self.entry_dict.items():
            entry_nodes = entry.get()
            vertex_edges = self.form_text(Vertex.vertex_dict[index].get_edges_class().get_edges())
            if entry_nodes != vertex_edges:
                result = self.form_text(entry_nodes, True)
                new_edges = [Edge(e[0], e[1]) for e in result]
                Vertex.vertex_dict[index].get_edges_class().set_edges(new_edges)
                Vertex.update_routers()

        self.window.destroy()

    @staticmethod
    def form_text(edges_list, split=False):
        """Formats edges list for inserting in entry"""
        result = []
        if edges_list:
            if split:
                temp = edges_list.split(', ')
                for id_width in temp:
                    temp2 = id_width.split(':')
                    result.append([int(x) for x in temp2])
                return result
            else:
                temp = []
                for edge in edges_list:
                    _id = edge.get_end_id()
                    _weight = edge.get_throughput()
                    temp.append(f'{_id}:{_weight}')

                result = ', '.join([x for x in temp])
                return result

        else:
            return []


class VertexInfo:
    def __init__(self, root, vertex_id):
        self.window = tk.Toplevel(root)
        self.window.title('Info')

        tk.Label(self.window, text=f'Info about vertex: {vertex_id}').grid(row=0, columnspan=3)

        try:
            x, y = Vertex.vertex_dict[vertex_id].get_xy()
            router = Vertex.vertex_dict[vertex_id].get_router()
        except KeyError:
            tk.Label(self.window, text='----------------------------', fg='silver') \
                .grid(row=1, columnspan=3)
            tk.Label(self.window, text='The vertex with the entered ID \n'
                                       'doesnt exist', fg='red') \
                .grid(row=2, columnspan=4)
        else:
            tk.Label(self.window, text='----------------------------', fg='silver') \
                .grid(row=1, columnspan=3)
            tk.Label(self.window, text='X coordinate:') \
                .grid(row=2, column=0)
            tk.Label(self.window, text='Y coordinate:') \
                .grid(row=2, column=1)

            tk.Label(self.window, text=f'{x}', fg='blue') \
                .grid(row=3, column=0)
            tk.Label(self.window, text=f'{y}', fg='blue') \
                .grid(row=3, column=1)

            tk.Label(self.window, text='----------------------------', fg='silver') \
                .grid(row=4, columnspan=3)

            tk.Label(self.window, text='Throughput:').grid(row=5, column=0)
            tk.Label(self.window, text=f'{router.get_throughput()} Mb/s', fg='blue') \
                .grid(row=6, column=0)

            tk.Label(self.window, text='Router:').grid(row=5, column=1)
            tk.Label(self.window, text=f'Name: {router.get_name()}', fg='blue') \
                .grid(row=6, column=1)
            tk.Label(self.window, text=f'Throughput: {router.get_throughput()} Mb/s', fg='blue') \
                .grid(row=7, column=1)
            tk.Label(self.window, text=f'Cost: {router.get_cost()}', fg='blue') \
                .grid(row=8, column=1)

            tk.Label(self.window, text='----------------------------', fg='silver') \
                .grid(row=9, columnspan=3)

            tk.Label(self.window, text='Connected to vertexes: ').grid(row=10, columnspan=3)
            for vertex in enumerate(sorted(Edges.get_all_edges(vertex_id), key=lambda vertex: vertex['id'])):
                tk.Label(self.window, text=f"Id: {vertex[1]['id']}     throughput: {vertex[1]['weight']}",
                         fg='blue').grid(row=11 + vertex[0], columnspan=3)


class RoutersWindow:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title('Info')

        tk.Label(self.window, text='Info about routers') \
            .grid(row=0, columnspan=4)
        self.create_routers_list()

    def create_routers_list(self):
        for router in enumerate(Router.routers_dict.values()):
            tk.Label(self.window, text=f"Name: {router[1].get_name()}") \
                .grid(row=router[0] + 1, column=1)
            tk.Label(self.window, text=f"Bandwidth: {router[1].get_throughput()}") \
                .grid(row=router[0] + 1, column=2)
            tk.Label(self.window, text=f"Cost: {router[1].get_cost()}") \
                .grid(row=router[0] + 1, column=3)


class LoadMatrix:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title('Load matrix')
        self.fill()

    def fill(self):
        nums = [vertex[0] for vertex in load_matrix.items()]
        for i in range(len(nums)):
            lab = tk.Label(self.window, text=nums[i]) \
                .grid(row=0, column=i + 1)

        for j in range(len(nums)):
            lab = tk.Label(self.window, text=nums[j]) \
                .grid(row=j + 1, column=0)

        for vertex in enumerate(load_matrix.values()):
            for edges in enumerate(vertex[1]):
                lab = tk.Label(self.window, text=edges[1]['weight'])
                lab.grid(row=vertex[0] + 1, column=edges[1]['end'] + 1)

                lab = tk.Label(self.window, text=edges[1]['weight'])
                lab.grid(row=edges[1]['end'] + 1, column=vertex[0] + 1)


MainWindow()
