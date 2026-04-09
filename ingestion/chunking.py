import os
import sys
import uuid
from tqdm import tqdm

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from langchain_classic.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.exception import CustomException
from src.utils import get_llm
from deployment.templates import code_description_template


class Chunker:
    def __init__(self):
        self.llm_model = get_llm()

    def generate_code_description(self, code_snippet):
        try:
            prompt_description = ChatPromptTemplate.from_template(code_description_template)

            generate_description = (
                prompt_description
                | self.llm_model
                | StrOutputParser()
            )

            description = generate_description.invoke({"code_snippet": code_snippet})
            return description

        except Exception as e:
            raise CustomException(e, sys)

    def parse_repo(self, repo_path):
        try:
            codes = []
            code_texts = []
            metadatas = []
            ids = []

            repo_name = os.path.basename(repo_path)

            for root, dirs, files in os.walk(repo_path):
                for file in files:
                    if not file.endswith(".py"):
                        continue
                    # if file.endswith(".py"):
                    file_path = os.path.join(root, file)

                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        code = f.read()

                    description = self.generate_code_description(code)

                    code_text = f"""Repository: {repo_name}
                        File: {file_path.split(repo_name)[-1]}

                        Symbol Type: file
                        Symbol Name: {file}

                        Description: {description}

                        Code:
                        {code}
                        """

                    codes.append(code)
                    code_texts.append(code_text)

                    metadatas.append({
                        "repo": repo_name,
                        "file": file_path.split(repo_name)[-1],
                        "symbol": file,
                        "type": "file"
                    })

                    ids.append(str(uuid.uuid4()))

            return ids, metadatas, codes, code_texts

        except Exception as e:
            raise CustomException(e, sys)