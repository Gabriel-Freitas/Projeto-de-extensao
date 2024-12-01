# Importando bibliotecas
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.uix.dropdown import DropDown
from functools import partial #import necessario para corrigir os callbacks

# Classe principal do aplicativo
class SatisfactionSurveyApp(App):
    def build(self):
        # Gerenciador de telas
        self.screen_manager = ScreenManager()

        self.categories = {
            "Satisfação": [
                "Em uma escala de 1 a 5, como você avalia sua motivação para participar das aulas e atividades?",
                "As aulas estão atendendo às suas expectativas de aprendizado? (1 a 5)"
            ],
            "Convivência com Colegas": [
                "Você se sente incluído e respeitado pelos colegas? (1 a 5)",
                "Existe colaboração e apoio entre você e os outros alunos? (1 a 5)"
            ],
            "Aprendizado": [
                "Você sente que está entendendo o conteúdo ensinado? (1 a 5)",
                "As aulas ajudam no seu desenvolvimento profissional? (1 a 5)"
            ],
            "Inclusão e Autonomia": [
                "O ambiente do curso é acolhedor e inclusivo para todos os alunos? (1 a 5)",
                "Você se sente à vontade para expressar suas opiniões durante as aulas? (1 a 5)"
            ],
            "Preferência de Aprendizado": [
                "Você prefere aprender com atividades guiadas ou de forma mais independente?"
            ],
        }
        #screen=Screen(name=category)
        #self.screen_manager.add_widget(screen)
        
        # Autenticação no Google Sheets
        self.authenticate_google_sheets()
        
        # Carregar dados do Google Sheets
        self.load_data_from_sheets()
        
        # Criar páginas para cada categoria e tela para o grafico de radar
        self.create_home_screen()
        self.create_category_pages()
        self.create_summary_page() 
       
        
        return self.screen_manager
    
    def authenticate_google_sheets(self):
        """Autenticação no Google Sheets usando gspread e oauth2client."""
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name("credencial_servico.json", scope)
        self.client = gspread.authorize(credentials)
        self.sheet = self.client.open("Formulário de Satisfação do Curso - Pão dos Pobres (respostas)").sheet1  # Nome da planilha
    
    def load_data_from_sheets(self):
        """Carrega os dados da planilha em um DataFrame do Pandas."""
        data = self.sheet.get_all_records()  # Lê todos os dados
        self.df = pd.DataFrame(data)


    def create_home_screen(self):
        """Cria a tela inicial."""
        screen = Screen(name="Início")
        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

    # Título
        layout.add_widget(Label(text="Relatório de Satisfação do Curso", size_hint=(1, 0.2), font_size=24))

     # Botão para Navegar Normalmente
        normal_button = Button(text="Iniciar") 
        normal_button.bind(on_press=partial(self.navigate_to_screen, list(self.categories.keys())[0]))
        layout.add_widget(normal_button)

     # Dropdown para Selecionar Página
        dropdown = DropDown()
        select_button = Button(text="Ir para Página Específica")
        for category in self.categories.keys():
             btn = Button(text=category, size_hint_y=None, height=44)
             btn.bind(on_release=lambda btn: dropdown.select(btn.text))
             dropdown.add_widget(btn)
            
# Botão Principal para Selecionar
        #select_button = Button(text="Ir para Página Específica", size_hint=(1, 0.2))  #tirar size_hint se...
        select_button.bind(on_release=dropdown.open)
        #dropdown.bind(on_select=lambda instance, x: self.select_page(select_button, x)) #se n funcionar retorne self.navigate_to_screen(x)
        #test[
        def on_select(instance, value):
            select_button.text=f"Selecionado: {value}"
            self.navigate_to_screen(value)

        #test
        dropdown.bind(on_select=on_select) #test
        layout.add_widget(select_button)

 # Adicionar ao layout
        screen.add_widget(layout)
        self.screen_manager.add_widget(screen)
    
    
    def create_category_pages(self):
        """Cria telas para cada categoria de perguntas."""
       
        categories=self.categories


        # Mapear perguntas para rótulos curtos
        short_labels = {
            "Em uma escala de 1 a 5, como você avalia sua motivação para participar das aulas e atividades?": "Motivação",
            "As aulas estão atendendo às suas expectativas de aprendizado? (1 a 5)": "Expectativas",
            "Você se sente incluído e respeitado pelos colegas? (1 a 5)": "Inclusão",
            "Existe colaboração e apoio entre você e os outros alunos? (1 a 5)": "Colaboração",
            "Você sente que está entendendo o conteúdo ensinado? (1 a 5)": "Compreensão",
            "As aulas ajudam no seu desenvolvimento profissional? (1 a 5)": "Desenvolvimento",
            "O ambiente do curso é acolhedor e inclusivo para todos os alunos? (1 a 5)": "Acolhimento",
            "Você se sente à vontade para expressar suas opiniões durante as aulas? (1 a 5)": "Expressão",
            "Você prefere aprender com atividades guiadas ou de forma mais independente?": "Preferência"
        }


        category_names = list(categories.keys()) #!!
        for idx, (category, questions) in enumerate(categories.items()): 
            screen = Screen(name=category)            
            
            layout = BoxLayout(orientation="vertical")
            
            # Título da categoria
            layout.add_widget(Label(text=f"Categoria: {category}", size_hint=(1, 0.1)))
            
            # Gráficos ou texto com base nas perguntas
            if category == "Preferência de Aprendizado":
                self.plot_multiple_choice_question(layout, short_labels) 
            else:
                self.plot_category_mean(layout, questions, short_labels) 
            
            # Botões de navegação
            nav_buttons = BoxLayout(size_hint=(1, 0.1))
            if idx > 0:  # Botão "Voltar"
                back_button = Button(text="Voltar")
                back_button.bind(on_press=partial(self.navigate_to_screen, list(categories.keys())[idx - 1])) ##Se não funcionar, colocar devolta category_names[idx - 1]
                nav_buttons.add_widget(back_button)
            
            if idx < len(categories) - 1:  # Botão "Avançar"
                next_button = Button(text="Avançar")
                next_button.bind(on_press=partial(self.navigate_to_screen, list(categories.keys())[idx + 1])) ##Se não funcionar, colocar devolta category_names[idx + 1]
                nav_buttons.add_widget(next_button)

            # Botão Resumo Geral. 
            summary_button = Button(text="Resumo Geral")
            summary_button.bind(on_press=partial(self.navigate_to_screen, "Resumo"))
            nav_buttons.add_widget(summary_button)

            
            layout.add_widget(nav_buttons)
            screen.add_widget(layout)
            self.screen_manager.add_widget(screen)

    #teste[
    def select_page(self, button, page_name):
        """Atualiza o texto do botão e navega para a página selecionada."""
        button.text = f"Selecionado: {page_name}"  # Atualiza o texto do botão principal
        self.navigate_to_screen(page_name)  # Navega para a tela selecionada


    
    def create_summary_page(self):
        """Cria uma página de resumo com um gráfico de radar."""
        screen = Screen(name="Resumo")
        layout = BoxLayout(orientation="vertical")
        
        # Título
        layout.add_widget(Label(text="Resumo Geral das Categorias", size_hint=(1, 0.1)))
        
        # Gráfico de Radar
        self.plot_radar_chart(layout)
        
        # Botão Voltar
        back_button = Button(text="Voltar", size_hint=(1, 0.1))
        back_button.bind(on_press=partial(self.navigate_to_screen, "Início")) ##Se não func, devolver list(self.categories.keys())[0]
        layout.add_widget(back_button)
        
        screen.add_widget(layout)
        self.screen_manager.add_widget(screen)


    def plot_category_mean(self, layout, questions, short_labels):
        """Cria um gráfico de médias para as perguntas da categoria."""
        # Selecionar as colunas relacionadas às perguntas
        relevant_columns = [col for col in self.df.columns if col in questions]
        if not relevant_columns:
            layout.add_widget(Label(text="Nenhuma pergunta encontrada nesta categoria."))
            return

         # Substituir nomes longos por rótulos curtos
        short_column_labels = [short_labels.get(col, col) for col in relevant_columns]
        
        fig, ax = plt.subplots(figsize=(3,1)) 
        means = self.df[relevant_columns].mean()  # Calcula a média das perguntas da categoria
        means.index = short_column_labels #substituir rotulos. 
        means.plot(kind="bar", color="skyblue", ax=ax)
        ax.set_title("Média das Respostas")
        ax.set_ylabel("Média (1 a 5)")
        ax.set_xticklabels(means.index, rotation=0, ha="right") 
        
        # Adicionar o gráfico ao layout
        layout.add_widget(FigureCanvasKivyAgg(fig))

    def plot_multiple_choice_question(self, layout, short_labels): 
        """Cria um gráfico de pizza para a pergunta de múltipla escolha."""
        question_col = "Você prefere aprender com atividades guiadas ou de forma mais independente?"
        if question_col in self.df.columns:
            fig, ax = plt.subplots(figsize=(4,4)) 
            preferences = self.df[question_col].value_counts()  # Contar frequência das opções
            preferences.index = [short_labels.get(opt, opt) for opt in preferences.index]  # Rótulos curtos.
            preferences.plot(kind="pie", autopct="%1.1f%%", ax=ax, startangle=90, colors=["skyblue", "lightgreen", "orange"])
            ax.set_title("Preferência de Aprendizado")
            ax.set_ylabel("") 
            
            # Adicionar o gráfico ao layout
            layout.add_widget(FigureCanvasKivyAgg(fig))

    
    def plot_radar_chart(self, layout):
        """Cria um gráfico de radar para exibir estatísticas gerais das categorias."""
        categories = list(self.categories.keys())[:-1]  
        means = [
            self.df[questions].mean().mean()
            for category, questions in self.categories.items() if category in categories
        ]
        
        # Configurar os dados do gráfico de radar
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        stats = means + means[:1]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(2, 2), subplot_kw={"polar": True})
        ax.plot(angles, stats, color="blue", linewidth=2, marker="o")
        ax.fill(angles, stats, color="skyblue", alpha=0.4)
        ax.set_yticks(range(1, 6))
        ax.set_yticklabels(["1", "2", "3", "4", "5"])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_title("Estatísticas Gerais por Categoria")
        layout.add_widget(FigureCanvasKivyAgg(fig))
          


    def navigate_to_screen(self, screen_name, instance=None): 
        """navega para a tela especificada"""
        if screen_name in self.screen_manager.screen_names:  # Verifica se a tela existe
             self.screen_manager.current=screen_name #Manter apenas essa linha se nao funcionar(Essas notas sao so para mim, caso esqueca de apagar)
        else:
             print(f"Erro: Tela '{screen_name}' não encontrada!")
        
# Executar o aplicativo
if __name__ == '__main__':
    SatisfactionSurveyApp().run()