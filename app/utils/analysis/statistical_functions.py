import numpy as np

class StatisticalFunctions:
    @staticmethod
    def calculate_mean(coleccion):
        coleccion=np.array(coleccion)
        if coleccion.size==0:
            return None
        return np.mean(coleccion)
    @staticmethod
    def calculate_population_std(coleccion):
        coleccion=np.array(coleccion)
        if coleccion.size==0:
            return None
        return np.std(coleccion)
    @staticmethod
    def calculate_coefficient_variation(media, desvEst):
        if media is None or desvEst is None:
            return None
        if media <= 0:
            return None
        return round((desvEst / media) * 100, 2)
    @staticmethod
    def classify_coefficient_variation(cv):
        if cv is None or cv < 0:
            return None
        if cv <= 15:
            return "Variabilidad Baja"
        elif cv <= 30:
            return "Variabilidad Moderada"
        else:
            return "Variabilidad Alta"
