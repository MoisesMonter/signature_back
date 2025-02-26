import sys
import subprocess
import re
import os
import time

filter = True
class Mutacao:
    def __init__(self,filter,router):
        self.__toml = []
        self.__sqlite = []
        self.__data = []
        self.filter = filter or True
        self.router = router

    '''listen'''
    def listen(self):
        arquivos = os.listdir(self.router+".")  # Lista arquivos e pastas no diretório atual
        print("Arquivos e pastas no diretório atual:")
        for arquivo in arquivos:
            if '.tom' in arquivo:
                self.__toml.append(arquivo)
                self.__sqlite.append(arquivo[:-5]+'.sqlite')

    '''create'''
    def create(self,data):
        self.subprocess("cosmic-ray init "+self.router+self.__toml[data]+" "+self.router+self.__sqlite[data])

    '''exec'''
    def exec(self,data):
        self.subprocess("cosmic-ray exec "+self.router+self.__toml[data]+" "+self.router+self.__sqlite[data])
    
    '''show'''
    def show(self,data):
        local_data = self.subprocess("cr-report "+self.router+self.__sqlite[data]+" --show-pending")
        return local_data.stdout

    '''cmd'''
    def subprocess(self,MetaData):
        return subprocess.run(MetaData, shell=True, text=True, capture_output=True)
    
    '''✅❌'''
    def end_process_icon(self,data):
        padrao = r"surviving mutants: (\d+) \(.*\)"

        resultado = re.search(padrao, data)

        if resultado:
            numero_mutantes = int(resultado.group(1))
            if numero_mutantes ==0:
                return "\t✅"
            else:
                return "\t❌"

    def run(self):
 
        self.listen()
        print('\n',self.__toml,'\n\n')
        for i in range(0,len(self.__toml)):
            self.create(i)
            self.exec(i)
            self.__data.append(self.show(i))

        for i in range(0,len(self.__data)):
            if self.filter:
                match = list(re.finditer(r'total jobs: \d+', self.__data[i]))
                if match:
                    ultima_ocorrencia = match[-1].start() 
                    self.__data[i] = self.__data[i][ultima_ocorrencia:]
                    
            print('Mutacao: ',str(self.__toml[i])[:-5],self.__data[i],self.end_process_icon(self.__data[i]),"\n--------------------\n")




if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print("Uso: python mutants.py <texto> necessita da rota exemplo ('signatures/mutants/') ou ('.' para indicar local)")
    #     sys.exit(1)  # Sai do programa com código de erro
    router = ''
    try:
        router = sys.argv[1]
    except:
        pass
    if router == '.':
        router = ''
    start_time = time.time()
    Mutacao(filter,router).run()
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Tempo de execução: {execution_time} segundos")
