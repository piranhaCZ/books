
class Tools:
    def replace(path_name: str):
        text = open(path_name, "r")
        text = ''.join([i for i in text]) \
            .replace(r'\"', "")
        x = open(path_name, "w")
        x.writelines(text)
        x.close()
        return

