import pandas as pd
import numpy as np
from itertools import product, islice
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import sys
import time
import os
import copy

# from tqdm import tqdm
from tqdm.tk import tqdm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import matplotlib.pyplot as plt
plt.switch_backend('agg')


class Panthera:

    def __init__(self, roof, outputFolder, df):
        self.ROOFTOP = roof
        self.OUTPUTFOLDER = outputFolder
        self.punteggi = df

    def main(self):
        # sort values by column Punteggi
        self.punteggi = self.punteggi.sort_values(by="Punteggi", ascending=True)

        # drop column Punteggi
        self.punteggi = self.punteggi.drop(columns="Punteggi")
        # Format the values of the dataframe to 2 decimal places, from the second column to the end
        self.punteggi.iloc[:, 1:] = self.punteggi.iloc[:, 1:].applymap(
            lambda x: round(x, 2)
        )
        # criteri is the list of the unique value in the column 'Criterio'
        criteri = self.punteggi["Criteri"].unique()

        listOfPunteggi = self.createCombinationsBaseline(self.punteggi)
        sys.stdout.write("Score List Updated\n")

        # compute the mean and the standard deviation of the list of punteggi
        sys.stdout.write("Calcolo media e deviazione standard...\n")
        mean, std = self.computeMeanStd(listOfPunteggi)

        # create a list of the cartesian product of the punteggi
        sys.stdout.write("Creazione combinazioni...\n")
        # Gather only the first 60000 combinations
        combo = list(
            islice(self.generate_combinations(listOfPunteggi, mean, std), self.ROOFTOP)
        )
        # combo = product(*listOfPunteggi)
        print("Combinazioni create \n")

        # create a dataframe with the cartesian product of the punteggi
        df = pd.DataFrame(combo, columns=criteri)
        print(df.head())
        # print the number of rows
        sys.stdout.write(f"Numero di combinazioni: {len(df)}\n")
        # export the dataframe to a txt file
        df.to_csv(f"{self.OUTPUTFOLDER}/Combinazioni.csv", sep=";", index=False)

        # calculate at first the sum of the values in each row of the dataframe, and put them into a list
        sumList = df.sum(axis=1).tolist()
        # round the values of the list to 2 decimal places
        sumList = [round(x, 2) for x in sumList]
        # sort the list for non ascending order
        sumList.sort(reverse=True)

        # from sumList create a matrix
        triMat = self.createTriangularCompares(sumList)

        # analyse the matrix
        dictValReduced = self.analyseTriMat(triMat)

        sys.stdout.write("Creazione grafico...\n")
        # plot the graph
        self.plotGraph(dictValReduced)

        sys.stdout.write("Esecuzione completata\n")

    def createCombinationsBaseline(self, punteggi):
        """
        Create a list of lists of the values of the dataframe punteggi, starting from the second column
        """
        # posizioni is the number of columns in the dataframe punteggi, starting from the third one
        posizioni = punteggi.columns[2:]
        posizioni = len(posizioni)

        # for each row of the dataframe, create a list and then put it in list of lists (keep only the values of columns 2 and after)
        punteggi = [punteggi.iloc[i, 1:].values for i in range(len(punteggi))]

        listOfPunteggi = []
        for punteggio in punteggi:
            punteggioList = []
            for i in range(len(punteggio)):
                punteggioList.append(punteggio[i])
            listOfPunteggi.append(punteggioList)

        return listOfPunteggi

    def computeMeanStd(self, listOfPunteggi):
        # maxVal which is the maximum value obtainable from list of punteggi
        maxVal = sum([max(i) for i in listOfPunteggi])
        # minVal which is the minimum value obtainable from list of punteggi
        minVal = sum([min(i) for i in listOfPunteggi])
        sys.stdout.write(f"Valore massimo: {maxVal}\n")
        sys.stdout.write(f"Valore minimo: {minVal}\n")
        # compute mean and std of a normal with that min and max
        mean = round((maxVal + minVal) / 2, 2)
        std = round((maxVal - minVal) / 8, 2)
        sys.stdout.write(f"Media: {mean}\n")
        sys.stdout.write(f"Deviazione standard: {std}\n")

        return mean, std

    def generate_combinations(self, listOfPunteggi: list, mean: float, std: float):
        """
        Generate all the possible combinations of the values in the dataframe punteggi
        """
        for comb in product(*listOfPunteggi):
            # yeld if sum of the combination is between mean +2*std and mean -2*std
            # if sum(comb) <= mean + 3 * std and sum(comb) >= mean - 1.5 * std:
            yield comb

    def createTriangularCompares(self, sumList):
        """
        Create a triangular matrix of the differences between the values of the list sumList
        """
        # export the distribution of the values to a plot

        fig = plt.figure(figsize=(15, 10))
        plt.hist(sumList, bins=30, density=True)
        plt.xlabel("Value")
        plt.ylabel("Frequency")
        plt.title("Distribuzione dei punteggi")
        plt.axvline(x=np.mean(sumList), color="red", linewidth=2, label="Mean")
        plt.axvline(x=np.median(sumList), color="yellow", linewidth=2, label="Median")
        plt.legend()
        # plt.show()
        fig.savefig(f"{self.OUTPUTFOLDER}/Distribuzione.png")
        # print mean and std
        sys.stdout.write(f"Mean: {np.mean(sumList)}\n")
        sys.stdout.write(f"Std: {np.std(sumList)}\n")
        # triMat is a vector of 1 dimension of size len(sumList)*log_n(len(sumList))
        # triMat = np.zeros(len(sumList) * math.ceil(math.log(len(sumList))))
        triMat = list()
        sys.stdout.write("Popolamento matrice...\n")
        # for each row of the matrix
        for i in range(1, len(sumList)):
            # for each column of the matrix
            for j in range(i, -1, -1):
                if sumList[j] - sumList[i] > 0:
                    # the value of the cell is the sum of the two values of the previous row, if positive
                    # triMat[i * len(sumList) + j] = sumList[i] - sumList[j]
                    # get the difference between the two values and append it to the list
                    diff = sumList[j] - sumList[i]
                    # round the difference to 2 decimal places
                    diff = round(diff, 2)
                    triMat.append(diff)
            # sys.stdout.write(f"Popolamento matrice... {i}\n")
        sys.stdout.write("Matrice popolata\n")
        sys.stdout.write("Numero di valori: " + str(len(triMat)) + "\n")

        return triMat

    def analyseTriMat(self, array: np.ndarray):
        # print first 10 elements of the array
        sys.stdout.write("Primi 10 elementi della matrice...\n")
        print(array[:10])
        sys.stdout.write("Analisi valori...\n")

        # # round all values to 2 decimal places
        # sys.stdout.write("Arrotondamento valori...\n")
        # array = np.round(array, 2)

        # generate a dictionary in which every value in values is the key, and its value is the number of times it appears
        sys.stdout.write("Conteggio valori...\n")
        step = 100 / len(array)
        dictVal = {}
        for val in array:
            if val in dictVal:
                dictVal[val] += 1
            else:
                dictVal[val] = 1

        dictVal = dict(sorted(dictVal.items(), key=lambda item: item[0]))
        # save the dictionary into a txt file
        with open(f"{self.OUTPUTFOLDER}/ValuesCount.txt", "w") as f:
            for key, value in dictVal.items():
                f.write("%s:%s\n" % (key, value))

        # create a dict of reduced keys with minimum and maximum value taken from the previous dictionarie and a step of 0.5
        sys.stdout.write("Riduzione valori...\n")
        dictValReduced = {}
        step = 0.5
        start = 0
        end = 0.5

        for key, value in dictVal.items():
            # if the key is between start and end, we increment the value of the key, if the key exists
            if key > start and key <= end:
                if start in dictValReduced:
                    dictValReduced[start] += value
                else:
                    dictValReduced[start] = value
            # if the key is greater than end, we increment the start and end and we add the key to the dictionary
            elif key > end:
                start += step
                end += step
                dictValReduced[start] = value

        return dictValReduced

    def plotGraph(self, dictValReduced):
        # clean the plot
        plt.clf()
        # create the figure
        fig = plt.figure(figsize=(15, 10))
        plt.bar(dictValReduced.keys(), dictValReduced.values())
        plt.xlabel("Value")
        plt.ylabel("Frequency")
        plt.title("Frequency of values")
        plt.xticks(list(dictValReduced.keys()))
        # rotate the x axis labels
        plt.xticks(rotation=90)
        # plt.show()

        # compute the weighted mean
        mean = 0
        total = 0
        for key, value in dictValReduced.items():
            mean += key * value
            total += value
        mean = mean / total
        print("Mean: ", mean)
        # compute the weighted percentiles and print them
        percentiles = [0.10, 0.25, 0.75, 0.9]
        for percentile in percentiles:
            perc = 0
            total = 0
            for key, value in dictValReduced.items():
                total += value
                if total > sum(dictValReduced.values()) * percentile:
                    perc = key
                    break
            print(f"{percentile * 100}th percentile: ", perc)

        # compute the wighted median
        median = 0
        total = 0
        for key, value in dictValReduced.items():
            total += value
            if total > sum(dictValReduced.values()) / 2:
                median = key
                break
        print("Median: ", median)

        # compute the weighted mode
        mode = 0
        maxValue = 0
        for key, value in dictValReduced.items():
            if value > maxValue:
                maxValue = value
                mode = key
        print("Mode: ", mode)

        # put the mean, median and mode on the plot
        plt.axvline(x=mean, color="red", linewidth=2, label="Mean")
        plt.axvline(x=median, color="yellow", linewidth=2, label="Median")
        plt.axvline(x=mode, color="blue", linewidth=2, label="Mode")
        plt.legend()
        # plt.show()
        fig.savefig(f"{self.OUTPUTFOLDER}/Scarti.png")

        # write the information on a txt file
        with open(f"{self.OUTPUTFOLDER}/Info.txt", "w") as f:
            f.write(f"Mean: {mean}\n")
            f.write(f"Median: {median}\n")
            f.write(f"Mode: {mode}\n")
            f.write(f"10th percentile: {percentiles[0]}\n")
            f.write(f"25th percentile: {percentiles[1]}\n")
            f.write(f"75th percentile: {percentiles[2]}\n")
            f.write(f"90th percentile: {percentiles[3]}\n")
