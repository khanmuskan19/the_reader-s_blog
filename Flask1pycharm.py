from flask import Flask, render_template
app=Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/')
def home():
    return "Hello World!"
@app.route('/about')
def about_novel():
    name="Muskan Khan"
    return render_template('index2nd.html',name2=name)

@app.route('/MK')
def Mkhan():
    return "Muskan Khan"

@app.route('/bootstrap') #search bootstrap templates
def bootstrap():
    return render_template('bootstrap.html')



if __name__=='__main__':
    app.run(debug=True)

