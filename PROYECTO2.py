# -*- coding: utf-8 -*-
"""
Created on Fri May 12 11:12:15 2023
@author: BUENO
"""

from scipy.io import wavfile
from scipy import signal
import scipy.spatial.distance as dist
import matplotlib.pyplot as plt
import numpy as np
import winsound 
import pyaudio
import wave
import serial

#Esta parte del codigo establece la conexion serial al modulo 
#"COM8": Especifica el nombre del puerto serial al que se desea conectar.
#9600:la velocidad de transmisión de datos en bits 
#timeout=1:tiempo máximo en segundos que se espera para recibir datos durante
ser = serial.Serial("COM8", 9600, timeout=1)  # Cambia el nombre del puerto COM... y la velocidad de baudios


#Envia datos codificados ,el sistema de codificacion que usa es ASCII
#ASCII asigna un numero unico a cada caracter 
def sendCommand(command):
    ser.write(command.encode('ascii'))  # Envia el comando codificado como ASCII al modulo

#recuperar datos utilizando una conexión serial
def retrieveData():
    #Envía el comando b'1'(secuencia de bytes) a través de la conexión serial 
    ser.write(b'1')
    #ser.readline:Lee datos del modulo
    data = ser.readline().decode('ascii')
    #Se decodifican a Unicode utilizando decode('ascii') y se devuelve como resultado

    return data

#Calcula la distancia DTW
def dista_dtw(matriz_distancia):
    N,M = matriz_distancia.shape
    matriz_costo = np.zeros((N+1,M+1))
    for i in range(1,N+1):
        matriz_costo[i,0] = np.inf
    for i in range(1,M+1):
        matriz_costo[0,i] = np.inf
    for i in range(N):
        for j in range(M):
            penalty = [matriz_costo[i,j],
                       matriz_costo[i,j+1],
                       matriz_costo[i+1,j]]
            i_penalty = np.argmin(penalty)
            matriz_costo[i+1,j+1] = matriz_distancia[i,j]+penalty[i_penalty]
    matriz_costo = matriz_costo[1:,1:]
    return matriz_costo

#_________________________________________________________________________________________________________________________________________________________________________________
while True:
    #------------------------GRABA UN AUDIO Y LO REPRODUCE--------------------------------------
    chunk = 512   # paquetes
    sample_format = pyaudio.paInt16   #
    channels = 2  # Canales de la computadora, eso varía en la computadora 
    fs = 48000     # Frecuencia de muestreo, se capturan 8000 muestras por segundo
    seconds = 3   # El tiempo en el que puedes decir una palabra, eso depende del usuario
    filename = 'Prueba.wav'     # Archivo completo que no tiene compresión 
    audio_obj = pyaudio.PyAudio() # Es un streaming de audio con un solo vector 
    input('Presiona una tecla para continuar...')
    print('Inicia grabación')
    stream = audio_obj.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True)  # Podemos hacer la grabación
    tramas = []
    sonido = []
    for i in range(0, int(fs/chunk*seconds)):
        datos = stream.read(chunk)
        tramas.append(datos)
        sonido.append(np.frombuffer(datos, dtype=np.int16))
    stream.stop_stream()
    stream.close()
    audio_obj.terminate()
    print('Termina grabación')

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(audio_obj.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(tramas))
    wf.close()
    winsound.PlaySound(filename, winsound.SND_FILENAME|winsound.SND_ASYNC)
    #------------------------------------------Datos del audio grabado -----------------------------
    # PRUEBA
    muestreop, datosp = wavfile.read('Prueba.wav')
    tp = np.arange(len(datosp)) / float(muestreop)
    datosp = datosp[:,0] / (2**15) #Normalizacion de los datos
    #---------------------------------------Datos de la base de datos------------------------------
    # ADELANTE
    muestreo1, datos1 = wavfile.read('Adelante.wav')
    t1 = np.arange(len(datos1)) / float(muestreo1)
    datos1 = datos1[:,0] / (2**15)
    # ATRAS
    muestreo2, datos2 = wavfile.read('Atras.wav')
    t2 = np.arange(len(datos2)) / float(muestreo2)
    datos2 = datos2[:,0] / (2**15)
    # IZQUIERDA
    muestreo3, datos3 = wavfile.read('Izquierda.wav')
    t3 = np.arange(len(datos3)) / float(muestreo3)
    datos3 = datos3[:,0] / (2**15)
    # DERECHA
    muestreo4, datos4 = wavfile.read('Derecha.wav')
    t4 = np.arange(len(datos4)) / float(muestreo4)
    datos4 = datos4[:,0] / (2**15)

    #----------------------------------------------------datos,frec muestreo,tam de ventana,100 vecinos ,longitud de cada segmento
    frecuenciap, tiempop, espectrop = signal.spectrogram(datosp, muestreop, nfft=1024, noverlap=100, nperseg=1024)
    frecuencia1, tiempo1, espectro1 = signal.spectrogram(datos1, muestreo1, nfft=1024, noverlap=100, nperseg=1024)
    frecuencia2, tiempo2, espectro2 = signal.spectrogram(datos2, muestreo2, nfft=1024, noverlap=100, nperseg=1024)
    frecuencia3, tiempo3, espectro3 = signal.spectrogram(datos3, muestreo3, nfft=1024, noverlap=100, nperseg=1024)
    frecuencia4, tiempo4, espectro4 = signal.spectrogram(datos4, muestreo4, nfft=1024, noverlap=100, nperseg=1024)

    distancia1 = dist.cdist(np.log(espectro1.T), np.log(espectrop.T), 'euclidean')
    costo1 = dista_dtw(distancia1)
    distancia2 = dist.cdist(np.log(espectro2.T), np.log(espectrop.T), 'euclidean')
    costo2 = dista_dtw(distancia2)
    distancia3 = dist.cdist(np.log(espectro3.T), np.log(espectrop.T), 'euclidean')
    costo3 = dista_dtw(distancia3)
    distancia4 = dist.cdist(np.log(espectro4.T), np.log(espectrop.T), 'euclidean')
    costo4 = dista_dtw(distancia4)

    costos = [costo1[-1,-1], costo2[-1,-1], costo3[-1,-1], costo4[-1,-1]]
    print(costos)

    if min(costos) == costos[0]:
        sendCommand('adelante')
        print("Adelante")
    elif min(costos) == costos[1]:
        sendCommand('atras')
        print("Atras")
    elif min(costos) == costos[2]:
        sendCommand('izquierda')
        print("izquierda")
    elif min(costos) == costos[3]:
        sendCommand('derecha')
        print("Derecha")

    uInput = input("¿Quieres volver a decir algo? (y/n) ")
    if uInput.lower() == 'n':
        ser.close()  # Cierra la conexión serial con el módulo
        break  # Termina el programa si se presiona 'n'
