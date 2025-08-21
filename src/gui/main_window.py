import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QTextEdit, QProgressBar
)
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Analisador de Dados Corporativo")
        self.setGeometry(100, 100, 800, 600)

        # Widget Central e Layout Principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Seção de Seleção de Arquivos ---
        file_selection_layout = QHBoxLayout()

        # Arquivo A
        file_a_layout = QVBoxLayout()
        self.label_a = QLabel("Arquivo A:")
        self.path_a_line = QLineEdit()
        self.path_a_line.setPlaceholderText("Selecione o caminho para o Arquivo A...")
        self.btn_browse_a = QPushButton("Procurar...")
        file_a_layout.addWidget(self.label_a)
        file_a_layout.addWidget(self.path_a_line)
        file_a_layout.addWidget(self.btn_browse_a)

        # Arquivo B
        file_b_layout = QVBoxLayout()
        self.label_b = QLabel("Arquivo B:")
        self.path_b_line = QLineEdit()
        self.path_b_line.setPlaceholderText("Selecione o caminho para o Arquivo B...")
        self.btn_browse_b = QPushButton("Procurar...")
        file_b_layout.addWidget(self.label_b)
        file_b_layout.addWidget(self.path_b_line)
        file_b_layout.addWidget(self.btn_browse_b)

        file_selection_layout.addLayout(file_a_layout)
        file_selection_layout.addLayout(file_b_layout)
        main_layout.addLayout(file_selection_layout)

        # --- Seção de Parâmetros ---
        params_layout = QVBoxLayout()
        self.label_keys = QLabel("Colunas-Chave (separadas por vírgula):")
        self.keys_line = QLineEdit()
        self.keys_line.setPlaceholderText("Ex: ID_Produto, Cod_Cliente")
        
        # Adicionaremos o campo para colunas de valor do confronto aqui
        self.label_values = QLabel("Colunas de Valor para Confronto (separadas por vírgula):")
        self.values_line = QLineEdit()
        self.values_line.setPlaceholderText("Ex: Vendas, Estoque")

        params_layout.addWidget(self.label_keys)
        params_layout.addWidget(self.keys_line)
        params_layout.addWidget(self.label_values)
        params_layout.addWidget(self.values_line)
        main_layout.addLayout(params_layout)

        # --- Seção de Ações ---
        actions_layout = QHBoxLayout()
        self.btn_cruzamento = QPushButton("Realizar Cruzamento")
        self.btn_confronto = QPushButton("Realizar Confronto")
        actions_layout.addWidget(self.btn_cruzamento)
        actions_layout.addWidget(self.btn_confronto)
        main_layout.addLayout(actions_layout)

        # --- Seção de Progresso e Log ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True) # Apenas para exibir informações

        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.log_console)

        # --- Conectar Sinais e Slots (eventos) ---
        self.btn_browse_a.clicked.connect(lambda: self.browse_file(self.path_a_line))
        self.btn_browse_b.clicked.connect(lambda: self.browse_file(self.path_b_line))

    def browse_file(self, line_edit):
        """Abre uma janela para selecionar um arquivo e insere o caminho no QLineEdit."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Arquivo",
            "",
            "Todos os Arquivos (*);;Excel (*.xlsx *.xls);;CSV (*.csv);;Parquet (*.parquet)"
        )
        if file_path:
            line_edit.setText(file_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())