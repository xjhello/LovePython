from sklearn.datasets import load_boston
import matplotlib.pyplot as plt
import random
import numpy as np
# 出图像

# 得到了X,Y
data = load_boston()
X, Y = data['data'], data['target']
room_index = 5
X_rm = X[:, room_index]
print(X.shape)


# 求偏导
# 对k求

def partial_k(y_ture, y_guess, x):
    return -2 * np.mean((np.array(y_ture) - np.array(y_guess)) * np.array(x))

# 对b求
def partial_b(y_ture, y_guess):
    return -2 * np.mean((np.array(y_ture) - np.array(y_guess)))
# 求损失
def l2_loss(y_ture, y_guess):
    return np.mean((np.array(y_ture) - np.array(y_guess)) ** 2)


# y_hat
def y_guess(k, x, b):
    return k * x + b


trying_time = 20000
min_loss = float('inf')
best_k, best_b = None, None
learning_rate = 1e-4
k = random.randint(0, 50)
b = random.randint(-50, 50)

plt.figure()
plt.scatter(X_rm, Y, color='red', alpha=0.5)
plt.figure()
plt.scatter(X_rm, Y, color='red', alpha=0.5)
plt.plot(X_rm, y_guess(k, X_rm, b), color='green')
plt.show()



for i in range(trying_time):
    # 将当前损失于最小损失相比较
    yhat = y_guess(k, X_rm, b)
    L2_loss = l2_loss(Y, yhat)

    if L2_loss < min_loss:
        best_k = k
        best_b = b
        min_loss = L2_loss

    # 找更合适的k与b

    k = k - partial_k(Y, yhat, X_rm) * learning_rate
    b = b - partial_b(Y, yhat) * learning_rate
print('L2loss=', min_loss)
plt.scatter(X_rm, Y, color='red')
plt.plot(X_rm, y_guess(best_k, X_rm, best_b), color='blue')
print('y = {} * x {}'.format(best_k, best_b))
plt.show()
