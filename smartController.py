from bottle import route, run, template

@route('/hello/<name>')
def index(name):
    return template('Hello {{ name }}', name=name)



run(host='127.0.0.1', port=8000)
