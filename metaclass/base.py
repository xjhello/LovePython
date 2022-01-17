#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/24 3:18 下午
# @Author  : Xujian

#  类的产生过程其实就是元类的调用过程
class Mymeta(type):  # 只有继承了type类才能称之为一个元类，否则就是一个普通的自定义类
    def __new__(cls, class_name, class_bases, class_dic):

        print(cls)  # <class '__main__.OldboyTeacher'>
        print(class_bases)  # (<class 'object'>,)
        print(class_dic)  # {'__module__': '__main__', '__qualname__': 'OldboyTeacher', 'school': 'oldboy', '__init__': <function OldboyTeacher.__init__ at 0x102b95ae8>, 'say': <function OldboyTeacher.say at 0x10621c6a8>}

        if class_name.islower():
            raise TypeError('类名%s请修改为驼峰体' % class_name)

        if '__doc__' not in class_dic or len(class_dic['__doc__'].strip(' \n')) == 0:
            raise TypeError('类中必须有文档注释，并且文档注释不能为空')

        return type.__new__(cls, class_name, class_bases, class_dic)

    def __init__(self, class_name, class_bases, class_dic):
        super().__init__(class_name, class_bases, class_dic)
        print(111111111)

    # def __init__(self, class_name, class_bases, class_dic):
    #     print(self)  # <class '__main__.OldboyTeacher'>
    #     print(class_bases)  # (<class 'object'>,)
    #     print(class_dic)  # {'__module__': '__main__', '__qualname__': 'OldboyTeacher', 'school': 'oldboy', '__init__': <function OldboyTeacher.__init__ at 0x102b95ae8>, 'say': <function OldboyTeacher.say at 0x10621c6a8>}
    #     super(Mymeta, self).__init__(class_name, class_bases, class_dic)  # 重用父类的功能
    #
    #     if class_name.islower():
    #         raise TypeError('类名%s请修改为驼峰体' % class_name)
    #
    #     if '__doc__' not in class_dic or len(class_dic['__doc__'].strip(' \n')) == 0:
    #         raise TypeError('类中必须有文档注释，并且文档注释不能为空')


class OldboyTeacher(object,metaclass=Mymeta): # OldboyTeacher=Mymeta('OldboyTeacher',(object),{...})
    """
    类OldboyTeacher的文档注释
    """
    school='oldboy'

    def __init__(self,name,age):
        self.name=name
        self.age=age

    def say(self):
        print('%s says welcome to the oldboy to learn Python' %self.name)

OldboyTeacher("demo",  11)