from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from flipkart.config import Config

class RAGChainBuilder:
    def __init__(self,vector_store):
        self.vector_store=vector_store
        self.model = ChatGroq(model=Config.RAG_MODEL , temperature=0.5)
        self.history_store={}

    def _get_history(self,session_id:str) -> BaseChatMessageHistory:
        if session_id not in self.history_store:
            self.history_store[session_id] = ChatMessageHistory()
        return self.history_store[session_id]
    
    def build_chain(self):
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

        # Create history-aware retriever chain
        context_prompt = ChatPromptTemplate.from_messages([
            ("system", "Given the chat history and user question, rewrite it as a standalone question."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        # Rewrite the question to be standalone, then retrieve documents
        history_aware_retriever = (
            context_prompt 
            | self.model 
            | StrOutputParser() 
            | retriever
        )

        # Format retrieved documents into context
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        # Create QA chain
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", """You're an e-commerce bot answering product-related queries using reviews and titles.
                          Stick to context. Be concise and helpful.\n\nCONTEXT:\n{context}\n\nQUESTION: {input}"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        # Build the full RAG chain
        rag_chain = (
            RunnablePassthrough.assign(
                context=lambda x: format_docs(history_aware_retriever.invoke(x))
            )
            | qa_prompt
            | self.model
            | StrOutputParser()
        )

        # Wrap output as dict with "answer" key and return with message history
        final_chain = RunnableLambda(lambda x: {"answer": rag_chain.invoke(x)})

        return RunnableWithMessageHistory(
            final_chain,
            self._get_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer"
        )


