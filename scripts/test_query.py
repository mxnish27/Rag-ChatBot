import sys
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src import RAGChain, log


def main():
    parser = argparse.ArgumentParser(
        description="Test the RAG system with a query"
    )
    parser.add_argument(
        "question",
        type=str,
        help="Question to ask the chatbot"
    )
    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Number of documents to retrieve"
    )
    
    args = parser.parse_args()
    
    try:
        log.info("Initializing RAG chain...")
        rag_chain = RAGChain()
        
        log.info(f"Querying: {args.question}")
        result = rag_chain.query(
            question=args.question,
            k=args.k
        )
        
        print("\n" + "="*80)
        print("ANSWER:")
        print("="*80)
        print(result["answer"])
        
        print("\n" + "="*80)
        print(f"SOURCES ({result['num_sources']}):")
        print("="*80)
        for i, source in enumerate(result["sources"], 1):
            print(f"\n{i}. {source['source']}")
            print(f"   {source['content']}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        log.error(f"Error during query: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
