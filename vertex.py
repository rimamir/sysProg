import json

from edges import Edges
from router import Router


class Vertex:
    vertex_dict = {}
    vertex_id = [0, ]

    def __init__(self, x, y, vertex_id=None):
        self._id = self.set_id(vertex_id)
        self._x = self.set_x(x)
        self._y = self.set_y(y)
        self._edges = self.set_edge()
        self._router = self.set_router()

        Vertex.vertex_dict[self._id] = self

    def get_xy(self):
        return self.get_x(), \
               self.get_y()

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def set_xy(self, x, y):
        self._x = self.set_x(x)
        self._y = self.set_y(y)

    def set_edge(self):
        if self.get_id() in Edges.edges_dict.keys():
            return Edges.edges_dict[self.get_id()]
        else:
            return Edges(self.get_id())

    def get_edges_class(self):
        return self._edges

    @staticmethod
    def set_x(x):
        if x < 0 or x > 800:
            print('Incorrect value.\n The X value cannot be less than 0 or greater than 800.')
        else:
            return x

    @staticmethod
    def set_y(y):
        if y < 0 or y > 800:
            print('Incorrect value.\n The Y value cannot be less than 0 or greater than 800.')
        else:
            return y

    def get_id(self):
        return self._id

    @staticmethod
    def set_id(vertex_id):
        Vertex.vertex_id.sort()
        if vertex_id is not None and vertex_id >= 0:
            if vertex_id in Vertex.vertex_id and vertex_id != 0:
                temp_id = Vertex.vertex_id[-1] + 1
                Vertex.vertex_id.append(temp_id)
                return Vertex.vertex_id[-1]
            else:
                if vertex_id == 0:
                    return Vertex.vertex_id[-1]
                else:
                    Vertex.vertex_id.append(vertex_id)
                    return Vertex.vertex_id[-1]
        else:
            temp_id = Vertex.vertex_id[-1] + 1
            Vertex.vertex_id.append(temp_id)
            return Vertex.vertex_id[-1]

    def get_router(self):
        return self._router

    def set_router(self):
        return Router.predict_router(self._edges.total_flow(self._id))

    def update_router(self):
        self._router = Router.predict_router(self._edges.total_flow(self._id))

    @classmethod
    def update_routers(cls):
        for vertex in cls.vertex_dict.values():
            vertex.update_router()

    @classmethod
    def create_json_format(cls):
        json_format = []
        for vertex in cls.vertex_dict.values():
            json_format.append({'id': vertex.get_id(),
                                'x': vertex.get_x(),
                                'y': vertex.get_y()
                                })
        return json_format

    @classmethod
    def fill_from_json(cls, json_file):
        with open(json_file, 'r') as read_file:
            data = json.load(read_file)

        for vertex in data['vertex']:
            vertex_id = vertex['id']
            x = vertex['x']
            y = vertex['y']
            Vertex(x, y, vertex_id)
