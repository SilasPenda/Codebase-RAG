import os
import sys
from tqdm import tqdm
from qdrant_client import QdrantClient
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from dotenv import load_dotenv

from ingestion.chunking import Chunker
from ingestion.embed_upsert import EmbedUpsert
from src.exception import CustomException
from src.utils import get_next_collection_name


load_dotenv()


class CodebaseIngestor:
    def __init__(self):
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        base_name = os.getenv("CODEBASE_COLLECTION_BASENAME")
        self.ingested_codebases_txt = os.path.join(os.getcwd(), "ingested_codebases.txt")
        
        # Qdrant setup
        self.client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key
            )
        
        self.collection_name = get_next_collection_name(self.client, base_name)
        self.codebase_dir = os.path.join(os.getcwd(), base_name)
        self.chunker = Chunker()
        self.embed_upsert = EmbedUpsert(self.client)

    def run_pipeline(self):
        try:
            codes_list = []
            code_texts_list = []
            metadatas_list = []
            ids_list = []
            ingested_codebases  = []

            if os.path.exists(self.ingested_codebases_txt):
                # Read existing collection names into the list
                with open(self.ingested_codebases_txt, "r") as f:
                    ingested_codebases = [line.strip() for line in f if line.strip()]

            for repo_name in tqdm(os.listdir(self.codebase_dir), desc="Processing codebases"):
                if repo_name in ingested_codebases:
                    print(f"Skipping already ingested codebase: {repo_name}")
                    continue

                ingested_codebases.append(repo_name)

                repo_path = os.path.join(self.codebase_dir, repo_name)
                ids, metadatas, codes, code_texts = self.chunker.parse_repo(repo_path)

                codes_list.extend(codes)
                code_texts_list.extend(code_texts)
                metadatas_list.extend(metadatas)
                ids_list.extend(ids)

            embedings = self.embed_upsert.get_embeddings(code_texts_list)
            self.embed_upsert.upsert(codes_list, metadatas_list, ids_list, embedings, self.collection_name)

            # Save the updated list of ingested codebases back to the file
            with open(self.ingested_codebases_txt, "w") as f:
                for codebase in ingested_codebases:
                    f.write(f"{codebase}\n")

        except Exception as e:
            raise CustomException(e, sys)
        


if __name__ == "__main__":
    ingestor = CodebaseIngestor()
    ingestor.run_pipeline()    