from flask import Flask, render_template, request
from whisky_manager import WhiskyManager
app = Flask(__name__)

whisky_manager = WhiskyManager('database.json')

@app.route('/', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        query = request.form.get('search')
        results = whisky_manager.search_bottles(query)
    return render_template('search.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
