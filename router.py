import json


class Router:
    routers_dict = {}
    routers_id = [0]

    def __init__(self, name, throughput, cost, router_id=None):
        self._id = self.set_id(router_id)
        self._name = name
        self._throughput = throughput
        self._cost = cost

        Router.routers_dict[self._id] = self

    def get_id(self):
        return self._id

    @staticmethod
    def set_id(router_id):
        Router.routers_id.sort()
        if router_id is not None:
            if router_id in Router.routers_id:
                temp_id = Router.routers_id[-1] + 1
                Router.routers_id.append(temp_id)
                return Router.routers_id[-1]
            else:
                if router_id == 0:
                    return Router.routers_id[-1]
                else:
                    Router.routers_id.append(router_id)
                    return Router.routers_id[-1]
        else:
            temp_id = Router.routers_id[-1] + 1
            Router.routers_id.append(temp_id)
            return Router.routers_id[-1]

    def get_name(self):
        return self._name

    def get_throughput(self):
        return self._throughput

    def get_cost(self):
        return self._cost

    def get_info(self):
        return f'Name: {self._name}, throughput: {self._throughput}, cost: {self._cost}'

    @classmethod
    def predict_router(cls, total_flow):
        routers_list = list(Router.routers_dict.items())
        routers_list.sort(key=lambda i: i[1].get_throughput())

        current_choice_id = None
        for router in routers_list:
            if total_flow > router[1].get_throughput():
                continue
            else:
                current_choice_id = router[1].get_id()
                return cls.routers_dict[current_choice_id]

    @classmethod
    def create_json_format(cls):
        json_format = []
        for router in cls.routers_dict.values():
            json_format.append({'id': router.get_id(),
                                'name': router.get_name(),
                                'throughput': router.get_throughput(),
                                'cost': router.get_cost()})
        return json_format

    @classmethod
    def fill_from_json(cls, json_file):
        with open(json_file, 'r') as read_file:
            data = json.load(read_file)

        for router in data['routers']:
            router_id = router['id']
            name = router['name']
            throughput = router['throughput']
            cost = router['cost']
            Router(name, throughput, cost, router_id)
