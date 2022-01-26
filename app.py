from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

def aa(a:int) ->int:
    pass

if __name__ == '__main__':
    # app.run()
    int('36000.0')