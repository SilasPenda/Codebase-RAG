import os
import sys
import ast
import uuid
from tqdm import tqdm
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.exception import CustomException
from src.logger import logging
from src.utils import get_device, read_yaml, read_pdf


class Chunker:
    def __init__(self):
        pass

    def parse_repo(self, repo_path):
        try:
            codes = []
            metadatas = []
            ids = []

            for root, dirs, files in os.walk(repo_path):
                repo_name = os.path.basename(repo_path)
                for file in (files):
                    if file.endswith((".py")):
                        file_path = os.path.join(root, file)

                        with open(file_path, "r") as f:
                            code = f.read()
                        tree = ast.parse(code)

                        for node in tree.body:
                            if isinstance(node, ast.ClassDef):
                                # extract class code
                                start_line = node.lineno - 1
                                end_line = node.body[-1].lineno
                                snippet = "\n".join(code.splitlines()[start_line:end_line])
                                node_type = "class"
                                symbol_name = node.name
                                





                                docstring = ast.get_docstring(node)

                                doc_section = docstring if docstring else "No docstring provided"

                                chunk_text = f"""
                                Repository: {repo_name}
                                File: {file_path.split(repo_name)[-1]}

                                Symbol Type: {node_type}
                                Symbol Name: {symbol_name}

                                Docstring:
                                {doc_section}

                                Code:
                                {snippet}
                                """

                            elif isinstance(node, ast.FunctionDef):
                                start_line = node.lineno - 1
                                end_line = node.body[-1].lineno
                                snippet = "\n".join(code.splitlines()[start_line:end_line])
                                node_type = "function"
                                symbol_name = node.name

                            else:
                                continue  # skip anything that isn’t a class or function

                            codes.append(snippet)

                            codes.append(
                                f"""
                            Repository: {repo_name}
                            File: {file_path.split(repo_name)[-1]}
                            Symbol: {symbol_name}
                            Type: {node_type}

                            Code:
                            {snippet}
                            """
                            )
                            metadatas.append({
                                "repo": repo_name,
                                "file": file_path.split(repo_name)[-1],
                                "symbol": symbol_name,
                                "type": node_type
                            })
                            ids.append(str(uuid.uuid4()))

            return ids, metadatas, codes

        except Exception as e:
            raise CustomException(e, sys)