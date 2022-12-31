from flask import Flask, render_template, request, send_file
import os
import csv
import magic
from werkzeug.utils import secure_filename


# Create uploads folder if it doesn't exist
path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'uploads')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files['file']
        fname = secure_filename(file.filename)
        file.save('uploads/'+fname)
        
        # Read the CSV file into csv_data
        with open('uploads/'+fname, encoding='utf-8') as df:
            csv_data = csv.reader(df)

            # If not blank, extract column name to columns list from first row of csv_data
            columns = [column for column in next(csv_data) if column]

            # Create dictionary with a key for each column in columns, empty list for values
            coldata = {column: [] for column in columns}

            # Fill coldata dict with corresponding values
            for row in csv_data:
                for i, column in enumerate(columns):
                    coldata[column].append(row[i])

                 
        # Get the name of the table to insert into from the user
        dest_table = request.form['dest_table']

        insert_stmts = []
        
        for i in range(len(coldata[columns[0]])):
            insert_stmt = "INSERT INTO {} ({}) VALUES ({})".format(
                dest_table,
                ', '.join(["'{}'".format(column) for column in columns]),
                ', '.join(["'{}'".format(coldata[column][i]) for column in columns])
            )
            insert_stmts.append(insert_stmt)
        
        with open('insert.sql', mode='w+',newline='') as output_file:
            for row in insert_stmts:
                output_file.write(row + '\n')
                
        try:
            return send_file('insert.sql')
        except FileNotFoundError:
            abort(404)
    
    # If the request is a GET request, render the HTML form
    return render_template("index.html")