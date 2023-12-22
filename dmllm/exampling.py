class Person:
    def __init__(self, name):
        self.name = name
        self.info = {}

    def sayname(self):
        print(f"My name is {self.name}")

    def setinfo(self, k, v):
        self.info[k] = v

    def __repr__(self):
        return f"SomePerson({self.name}, {self.info})"
    
    def __getitem__(self, key):
        print("My balls!")
        return self.info[key]


al = Person("Alec")
al.setinfo("age", 30)
print(al['age'])