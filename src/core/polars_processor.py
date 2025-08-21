import polars as pl
from polars.exceptions import PolarsError

class DataProcessor:
    """
    Classe responsável por todas as operações de processamento de dados usando Polars.
    """

    def __init__(self):
        # A classe pode ser inicializada com atributos futuros, se necessário.
        pass

    def read_file(self, file_path: str, file_format: str, delimiter: str = None) -> pl.DataFrame:
        """
        Lê um arquivo de dados (xlsx, xls, csv, parquet) e o carrega em um DataFrame do Polars.

        Args:
            file_path (str): O caminho para o arquivo.
            file_format (str): O formato do arquivo ('xlsx', 'xls', 'csv', 'parquet').
            delimiter (str, opcional): O delimitador para arquivos CSV. Padrão para ','.

        Returns:
            pl.DataFrame: O DataFrame do Polars com os dados do arquivo.

        Raises:
            ValueError: Se o formato do arquivo não for suportado.
            PolarsError: Se houver um erro ao carregar o arquivo.
        """
        print(f"Iniciando a leitura do arquivo: {file_path}...")
        
        try:
            if file_format == 'xlsx' or file_format == 'xls':
                # O Polars usa o mesmo leitor para ambos os formatos.
                # A premissa inicial é ler apenas a primeira sheet.
                df = pl.read_excel(file_path, engine='openpyxl')
            elif file_format == 'csv':
                # Lê arquivos CSV, respeitando o delimitador.
                if delimiter is None:
                    delimiter = ',' # Padrão para a vírgula, caso não seja especificado
                df = pl.read_csv(file_path, separator=delimiter)
            elif file_format == 'parquet':
                df = pl.read_parquet(file_path)
            else:
                raise ValueError(f"Formato de arquivo não suportado: {file_format}")
            
            print(f"Arquivo lido com sucesso. Linhas: {len(df):,}, Colunas: {len(df.columns)}")
            return df
            
        except PolarsError as e:
            print(f"Erro ao carregar o arquivo com Polars: {e}")
            raise
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
            raise
    def cruzamento(self, df_a: pl.DataFrame, df_b: pl.DataFrame, on_columns: list) -> pl.DataFrame:
        """
        Realiza o cruzamento (join) de dois DataFrames.

        Args:
            df_a (pl.DataFrame): O DataFrame primário.
            df_b (pl.DataFrame): O DataFrame secundário.
            on_columns (list): Lista de colunas para o join.

        Returns:
            pl.DataFrame: O DataFrame resultante do cruzamento.
        """
        print(f"Iniciando cruzamento (join) dos arquivos usando as chaves: {on_columns}...")
        
        # O Polars faz o join de forma otimizada. Usaremos um left join
        # para manter todas as linhas do arquivo A, conforme a ideia de cruzamento.
        try:
            result_df = df_a.join(df_b, on=on_columns, how='left', suffix='_B')
            print("Cruzamento concluído.")
            return result_df
        except Exception as e:
            print(f"Erro ao realizar o cruzamento: {e}")
            raise
    
    def confronto(self, df_a: pl.DataFrame, df_b: pl.DataFrame, on_columns: list, value_columns: list) -> pl.DataFrame:
        """
        Realiza o confronto de dois DataFrames, subtraindo os valores das colunas especificadas.

        Args:
            df_a (pl.DataFrame): O DataFrame de referência (minuendo).
            df_b (pl.DataFrame): O DataFrame a ser subtraído (subtraendo).
            on_columns (list): Lista de colunas-chave para o join.
            value_columns (list): Lista de colunas numéricas para a subtração.

        Returns:
            pl.DataFrame: Um DataFrame com os resultados do confronto, incluindo a diferença
                          e a diferença percentual para cada coluna de valor.
        """
        print(f"Iniciando confronto de valores usando as chaves: {on_columns}...")
        
        try:
            comparison_df = df_a.join(df_b, on=on_columns, how='inner', suffix='_B')

            for col_name in value_columns:
                col_name_b = f"{col_name}_B"
                
                if col_name not in comparison_df.columns or col_name_b not in comparison_df.columns:
                    print(f"Aviso: A coluna '{col_name}' não foi encontrada em ambos os arquivos e será ignorada.")
                    continue

                comparison_df = comparison_df.with_columns([
                    (pl.col(col_name) - pl.col(col_name_b)).alias(f'DIF_{col_name}'),
                    (
                        pl.when(pl.col(col_name) != 0)
                          # Removido o "* 100" aqui
                          .then((pl.col(col_name) - pl.col(col_name_b)) / pl.col(col_name))
                          .otherwise(None)
                    ).alias(f'DIF_%_{col_name}')
                ])
            
            print("Confronto de valores concluído.")
            return comparison_df

        except Exception as e:
            print(f"Erro ao realizar o confronto: {e}")
            raise
    
    def get_confronto_summary(self, confronto_df: pl.DataFrame, value_columns: list) -> dict:
        """
        Calcula o resumo dos totais para a operação de confronto.

        Args:
            confronto_df (pl.DataFrame): O DataFrame detalhado retornado pelo método confronto.
            value_columns (list): As colunas de valor usadas no confronto.

        Returns:
            dict: Um dicionário com os totais de confronto e a diferença percentual total.
        """
        summary = {}
        
        summary['Linhas com correspondência'] = len(confronto_df)

        for col_name in value_columns:
            col_a = col_name
            col_b = f"{col_name}_B"
            col_diff = f"DIF_{col_name}"
            col_diff_percent = f"DIF_%_{col_name}"

            if col_a in confronto_df.columns and col_b in confronto_df.columns:
                total_a = confronto_df[col_a].sum()
                total_b = confronto_df[col_b].sum()
                total_diff = confronto_df[col_diff].sum()
                
                # Removido o "* 100" aqui também
                total_diff_percent = (total_diff / total_a) if total_a != 0 else 0

                summary[f'Total em "{col_name}" (Arquivo A)'] = total_a
                summary[f'Total em "{col_name}" (Arquivo B)'] = total_b
                summary[f'Diferença Total em "{col_name}"'] = total_diff
                summary[f'Diferença % Total em "{col_name}"'] = total_diff_percent

        return summary

if __name__ == '__main__':
    # Exemplo de uso para testes manuais
    processor = DataProcessor()
    
    # --- Teste de Cruzamento (sem alteração) ---
    print("\n--- Teste de Cruzamento ---")
    df_a_cruz = pl.DataFrame({"ID": [1, 2, 3], "Produto": ["A", "B", "C"]})
    df_b_cruz = pl.DataFrame({"ID": [2, 3, 4], "Preco": [10, 20, 30]})
    try:
        cruzamento_df = processor.cruzamento(df_a_cruz, df_b_cruz, on_columns=["ID"])
        # Para o cruzamento, o resumo pode ser simplesmente o total de linhas.
        cruzamento_summary = {'Total de linhas': len(cruzamento_df)}
    except Exception:
        cruzamento_df = pl.DataFrame()
        cruzamento_summary = {'Total de linhas': 0}

    # --- Teste de Confronto (nova lógica de resumo) ---
    print("\n--- Teste de Confronto (Subtração de Valores) ---")
    df_a_confr = pl.DataFrame({"ID": [1, 2, 3], "Vendas": [100, 200, 150]})
    df_b_confr = pl.DataFrame({"ID": [1, 2, 3], "Vendas": [120, 180, 150]})
    
    try:
        value_cols = ["Vendas"]
        confronto_df = processor.confronto(df_a_confr, df_b_confr, on_columns=["ID"], value_columns=value_cols)
        confronto_summary = processor.get_confronto_summary(confronto_df, value_columns=value_cols)
        
        print("\nDataFrame de Confronto Detalhado:")
        print(confronto_df)
        print("\nResumo do Confronto:")
        print(confronto_summary)

    except Exception:
        confronto_df = pl.DataFrame()
        confronto_summary = {}