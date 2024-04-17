import base64
import json
import shutil
from itertools import product, islice
from io import BytesIO
from tabulate import tabulate
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from PIL import Image, ImageTk
import sys
import time
import os
import copy

import plotly.express as px
import plotly.graph_objects as go

import matplotlib.pyplot as plt

from Panthera import Panthera

from flask import (
    Flask,
    request,
    redirect,
    url_for,
    render_template,
    send_file,
    send_from_directory,
)

from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)

app = Flask(__name__)

#### GLOBAL VARIABLES ####
#### Panthera Global Variables ####
global punteggi  # global dataframe
global OUTPUTFOLDER  # global output folder
OUTPUTFOLDER = "downloads/Panthera"
# create the output folder if it does not exist
if not os.path.exists(OUTPUTFOLDER):
    os.makedirs(OUTPUTFOLDER)
global ROOFTOP  # global rooftop


#### INDEX ####
@app.route("/")
def index():
    return render_template("index.html")


#### PANTHERA ####
#### Landing Page ####
@app.route("/panthera_landing")
def panthera():
    return render_template("Panthera/panthera.html")


#### Download xlsx template ####
@app.route("/download")
def download_file():
    filename = "Template.xlsx"  # Replace with your actual file name
    return send_file(filename, as_attachment=True)


#### Upload and check xlsx file ####
@app.route("/uploadxls", methods=["POST", "GET"])
def upload_file_xls():
    if request.method == "POST":
        f = request.files["file"]
        # IF THERE IS NO FILE SELECTED
        if f.filename == "":
            return render_template(
                "Panthera/panthera.html", message="Nessun file selezionato"
            )
        # check if the file is an xls file
        xlsx, nullVals, ncols, nrows = check_xls(f)
        if not xlsx:
            return render_template(
                "Panthera/panthera.html", message="Il file non è un xlsx"
            )
        else:
            # clean uploads folder
            files = os.listdir("uploads/Panthera/")
            for file in files:
                os.remove("uploads/Panthera/" + file)
            # convert xlsx in csv
            df = pd.read_excel(f)
            df.to_csv("uploads/Panthera/panthera.csv", sep=";", index=False)
            # # save the file
            # f.save("uploads/Panthera/" + f.filename)
            # make the 'runPanthera' html element visible
            return render_template(
                "Panthera/panthera.html",
                message="File caricato con successo",
                pos=f"Numero di colonne: {ncols}",
                crit=f"Numero di righe: {nrows}",
                nullVals="Nessun valore nullo" if nullVals else "Ci sono valori nulli",
                execVisible=True,
            )


def check_xls(file):

    xlsx, nullVals = True, True
    ncols = 0
    nrows = 0
    # check if the file is an xls file
    if file.filename.split(".")[-1] != "xlsx":
        xlsx = False

    # check if there are empty cells
    print(file)
    df = pd.read_excel(file)
    if df.isnull().values.any():
        nullVals = False
    else:
        nullVals = True

    # check the number of cols
    ncols = len(df.columns)
    nrows = len(df.columns[0])

    return xlsx, nullVals, ncols, nrows


#### Main execution of panthera ####
@app.route("/panthera_main", methods=["POST"])
async def panthera_main():

    if request.method == "POST":
        # get the value from html element with name "rooftop"
        ROOFTOP = int(request.form["rooftop"])
        print(ROOFTOP)

    # read the only file in the folder
    mainRoot = "uploads"
    subroot = "Panthera"
    path = os.path.join(mainRoot, subroot)
    files = os.listdir(path)
    if len(files) == 0:
        punteggi = pd.DataFrame()
        return render_template("Panthera/panthera.html", message="Nessun file caricato")
    else:
        file = files[0]
        path = os.path.join(mainRoot, subroot)
        punteggi = pd.read_csv(os.path.join(path, file), sep=";")

    # create Panthera object
    panthera = Panthera(roof=ROOFTOP, outputFolder=OUTPUTFOLDER, df=punteggi)
    panthera.main()

    return render_template(
        "Panthera/panthera.html", message="File generato con successo"
    )


@app.route("/panthera_download")
def panthera_download():
    
    # delete the folder if exists
    if os.path.exists(OUTPUTFOLDER):
        # create a function that takes the output folder, zips it and downloads it
        zipf = shutil.make_archive(OUTPUTFOLDER, "zip", OUTPUTFOLDER)
        shutil.rmtree(OUTPUTFOLDER)
        return (send_file(zipf, as_attachment=True))
    else:
        return render_template("Panthera/panthera.html", message="Nessun file generato")

if __name__ == "__main__":
    # app.run()
    app.run(host="0.0.0.0", port=8080, debug=True)
    # app.run(host='0.0.0.0', port=3003, debug=True,
    #         ssl_context=('/etc/ssl/certs/selfsigned.crt', '/etc/ssl/private/selfsigned.key'))
