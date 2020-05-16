class Edge:

    def __init__(self, end_id, throughput=None):
        self._end_id = None
        self._throughput = None

        self.set_throughput(throughput)
        self.set_end_id(end_id)

    def get_end_id(self):
        return self._end_id

    def set_end_id(self, end_id):
        self._end_id = end_id

    def get_throughput(self):
        return self._throughput

    def set_throughput(self, throughput):
        if throughput >= 0:
            self._throughput = throughput
        return None

    def get_info(self):
        return f'End id: {self.get_end_id()}, throughput: {self.get_throughput()}'
