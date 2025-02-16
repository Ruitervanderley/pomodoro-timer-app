import time

class Cronometro:
    def __init__(self):
        self.tempo_inicial = 0
        self.tempo_final = 0
        self.tempo_pausado = 0
        self.em_andamento = False
        self.em_pausa = False
        self.duracao = 0  # Em segundos

    def definir_duracao(self, duracao):
        """
        Define a duração total do cronômetro em segundos.
        """
        self.duracao = duracao

    def iniciar(self):
        """
        Inicia o cronômetro.
        """
        if not self.em_andamento and not self.em_pausa:
            self.tempo_inicial = time.time()
            self.em_andamento = True
        elif self.em_pausa:
            self.em_andamento = True
            self.em_pausa = False
            # Ajusta o tempo inicial para compensar o tempo em pausa
            self.tempo_inicial += time.time() - self.tempo_pausado

    def parar(self):
        """
        Para o cronômetro.
        """
        if self.em_andamento:
            self.tempo_final = time.time()
            self.em_andamento = False
            self.em_pausa = False

    def reiniciar(self):
        """
        Reinicia o cronômetro para o tempo configurado.
        """
        self.tempo_inicial = 0
        self.tempo_final = 0
        self.tempo_pausado = 0
        self.em_andamento = False
        self.em_pausa = False

    def pausar(self):
        """
        Pausa o cronômetro.
        """
        if self.em_andamento:
            self.em_andamento = False
            self.em_pausa = True
            self.tempo_pausado = time.time()

    def tempo_restante(self):
        """
        Calcula o tempo restante em segundos.
        """
        if self.em_andamento:
            tempo_decorrido = time.time() - self.tempo_inicial
            return max(0, self.duracao - tempo_decorrido)
        elif self.em_pausa:
            tempo_decorrido = self.tempo_pausado - self.tempo_inicial
            return max(0, self.duracao - tempo_decorrido)
        else:
            return max(0, self.duracao)

    def tempo_decorrido(self):
        """
        Calcula o tempo decorrido em segundos.
        """
        if self.em_andamento:
            return time.time() - self.tempo_inicial
        elif self.em_pausa:
            return self.tempo_pausado - self.tempo_inicial
        else:
            return 0
