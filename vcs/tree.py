class Tree:
    """
    Объект представления директории, находящейся в репозитории
    """
    def __init__(self, name):
        self.name = name
        self.blobs = list()
        self.trees = list()
