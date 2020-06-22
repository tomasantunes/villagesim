1. Install [Visual Studio Code](https://code.visualstudio.com/)
2. Create a folder for your project
3. Create a file called main.py and two folders named “static” and “templates”

_main.py_
```
from flask import Flask, flash, redirect, render_template, request, session, abort

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
```

_home.html_
```
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home</title>
</head>
<body>
    <h1>Home</h1>
</body>
</html>
```