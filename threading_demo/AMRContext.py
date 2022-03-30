class A():
    def aa(self):
        print(111)



obj = A()
class B():
    def __getattr__(self, item, *args, **kwargs):
        if hasattr(obj, item):
            return getattr(obj,item)
        else:
            raise
B().aa1()
