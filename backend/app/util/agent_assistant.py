from typing import List

def format_docs(docs : List) -> str:
    formatted_docs = []
    for i in range(len(docs)):
        if i % 2 ==0:
            formatted_docs.append(f"질문{i + 1} - {docs[i].content}")
        else:
            formatted_docs.append(f"답변{i + 1} - {docs[i].content}")
        
    return "\n\n".join(formatted_docs)


def format_retriever(docs : List) -> str:
    return "\n\n".join(doc.page_content for doc in docs)