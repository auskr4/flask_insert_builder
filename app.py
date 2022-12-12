from flask import Flask, render_template, request, send_file
import os
import csv
from werkzeug.utils import secure_filename

#if not os.path.isdir('/uploads'): 
   #os.makedirs('/uploads')

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files['file']
        fname = secure_filename(file.filename)
        file.save('uploads/'+fname)
        
        # Read the CSV file
        with open('uploads/'+fname, encoding='utf-8') as df:
            csv_data = csv.reader(df)
            data_rows = list(csv_data)
        
        # Strip out blank values from extra cols
        def remove_blanks(data_row):
            cleaned = []
            for i in range(len(data_row)):
                if data_row[i] != '':
                    cleaned.append(data_row[i])  
            return cleaned
        
        # Gather column names from first row of CSV
        columns = []
        for col in data_rows[1]:
            if col != '':
                columns.append(col)
        colstr = ','.join(columns) #join list to be used in insert_str
        
        # Get the name of the table to insert into from the user
        dest_table = request.form['dest_table']
        
        # Open the output file
        with open('insert.sql', mode='w+', newline='') as output_file:
            for r in data_rows[2:]:
                values = ""
                clean_row = remove_blanks(r)
                for i in range(len(clean_row)):
                    tmp = ""
                    if clean_row[i] != '':
                        tmp += "'"+clean_row[i]+"'"
                        values += tmp
                        if len(clean_row) - i > 1:
                            values += ","
                insert_str = "INSERT into {} ({})\nVALUES ({});".format(dest_table, colstr, values)
                output_file.write(insert_str+'\n')
        
        # Return the output file to the user
        return send_file('insert.sql')
    
    # If the request is a GET request, render the HTML form
    return render_template("index.html")