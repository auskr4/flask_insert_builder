from flask import Flask, render_template, request, send_file, flash
import os
import csv
import magic
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.debug=True

# Load config from config file
app.config.from_pyfile('config.py')
ALLOWED_FILE_TYPES = app.config['ALLOWED_FILE_TYPES']
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
path = os.getcwd()
upload_path = os.path.join(path, UPLOAD_FOLDER)
if not os.path.isdir(upload_path):
    os.mkdir(upload_path)

#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files['file']
        fname = secure_filename(file.filename)

        file_type = magic.from_buffer(file.read(), mime=True)
        if file_type not in ALLOWED_FILE_TYPES:
            #ft_error = "Invalid File Type.  Please choose a CSV file."
            return render_template("index.html", error="Invalid File Type.  Please choose a CSV file.")

        file.seek(0)
        file.save(os.path.join(upload_path, fname))

        file_path = os.path.join(upload_path, fname)
        print(file_path)
        if not os.path.exists(file_path):
            return render_template("index.html", error="The chosen file no longer exists.  Please try again.")

        # Read the CSV file into csv_data
        with open('uploads/'+fname, encoding='utf-8') as df:
            csv_data = csv.reader(df)

            columns = [column for column in next(csv_data) if column]
            
            coldata = {column: [] for column in columns}

            for row in csv_data:
                for i, column in enumerate(columns):
                    coldata[column].append(row[i])

        # Get table name from user input         
        dest_table = request.form['dest_table']

        insert_stmts = []

        print(columns)
        for i in range(len(coldata[columns[0]])):
            insert_stmt = "INSERT INTO {} ({}) VALUES ({})".format(
                dest_table,
                ', '.join(["{}".format(column) for column in columns]),
                ', '.join(["'{}'".format(coldata[column][i]) for column in columns])
            )
            insert_stmts.append(insert_stmt)
        
        # Write to output file
        with open('insert.sql', mode='w+',newline='') as output_file:
            for row in insert_stmts:
                output_file.write(row + '\n')
                
        try:
            return send_file('insert.sql')
        except FileNotFoundError:
            return render_template("index.html", error="Your file couldn’t be accessed. It may have been moved, edited")
    
    # If the request is a GET request, render the HTML form
    return render_template("index.html")