import os
import sqlite3
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Function to get SQL query from LLM
def get_sql_query(user_query):
    groq_sys_prompt = ChatPromptTemplate.from_template("""
                    You are an expert in converting English questions to SQL queries.
                    The SQL database is named STUDENT with columns: NAME, COURSE, SECTION, MARKS.
                    
                    Examples:
                    - "How many records exist?" → SELECT COUNT(*) FROM STUDENT;
                    - "List students in Data Science" → SELECT * FROM STUDENT WHERE COURSE="Data Science";
                    
                    Return **ONLY the SQL query**, no explanations, no extra words.
                    Convert the following question into SQL: {user_query}
                    """)

    model = "llama3-8b-8192"
    llm = ChatGroq(
        groq_api_key=os.environ.get("GROQ_API_KEY"),
        model_name=model
    )

    chain = groq_sys_prompt | llm | StrOutputParser()
    return chain.invoke({"user_query": user_query}).strip()

# Function to execute SQL query
@st.cache_data  # Caches results to avoid repeated executions
def return_sql_response(sql_query):
    database = "student.db"
    with sqlite3.connect(database) as conn:
        return list(set(conn.execute(sql_query).fetchall()))  #  Remove duplicates

def main():
    st.set_page_config(page_title="Text To SQL")
    st.header("Talk to your Database!")

    # Initialize session state
    if "sql_query" not in st.session_state:
        st.session_state.sql_query = None
    if "query_result" not in st.session_state:
        st.session_state.query_result = None
    if "submit_clicked" not in st.session_state:
        st.session_state.submit_clicked = False

    # User input
    user_query = st.text_input("Enter your question:")

    # Button logic (Prevents multiple submissions)
    if st.button("Enter") and not st.session_state.submit_clicked:
        st.session_state.submit_clicked = True  # Set flag
        st.session_state.sql_query = get_sql_query(user_query)  # Generate SQL
        try:
            st.session_state.query_result = return_sql_response(st.session_state.sql_query)  # Fetch result
        except Exception as e:
            st.session_state.query_result = f"Error: {e}"

    # Display results (if available)
    if st.session_state.sql_query:
     st.subheader(f"Query Executed: `{st.session_state.sql_query}`")

    if isinstance(st.session_state.query_result, str):  # Error handling
        st.error(st.session_state.query_result)
    elif st.session_state.query_result:
        st.write("### Query Results:")

        #  Convert to a set to remove duplicates
        unique_results = list(set(st.session_state.query_result))  

        for row in unique_results:
            st.write(", ".join(map(str, row)))  # Prints each row in a readable format
    else:
        st.write("No records found.")

if __name__ == '__main__':
    main()
