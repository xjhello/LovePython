#!/usr/bin/env python
# -*- coding: utf-8 -*-

class A():
    x = "A"

class B(A):
    pass

class C(A):
    x = "C"

class D(B, C):
    pass

print(D().x)