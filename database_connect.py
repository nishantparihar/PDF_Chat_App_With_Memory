import streamlit as st
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.sql import select
import os
from dotenv import load_dotenv

load_dotenv()


def getConnection():
    try:
        #if os.getenv('usernamee') and os.getenv('password') and os.getenv('host') and os.getenv('mydatabase'):

        ms_uri = f"mssql+pyodbc://{os.getenv('usernamee')}:{os.getenv('password')}@{os.getenv('host')}:{os.getenv('port')}/{os.getenv('mydatabase')}?driver=ODBC+Driver+17+for+SQL+Server"
        engine = create_engine(ms_uri)
        
        return engine
    except Exception as e:
        # Handle any errors that occur
        st.error("Error in connection: {}".format(e))
        st.write(e)


def getTitles():
    try:
        # Create a cursor to execute SQL statements
        engine = getConnection()

        if engine:
            with engine.connect() as connection:
                result = connection.execute(sa.text("SELECT conversation_id, title FROM dbo.conversations"))
                conversation_data = []

                for row in result:
                    conversation_data.append((row[0], row[1]))  # Extract conversation_id and title from each row
                    
                conversation_data.reverse()  # Reverse the order of the conversation data

            return conversation_data
        

    except Exception as e:
        # Handle any errors that occur
        st.error("Error retrieving conversation titles: {}".format(e))




def getFromDatabase(title):
     
    try:
        engine = getConnection()
        if engine:
            # Prompt the user for the conversation title
            conversation_title = title

            # Fetch the conversation content
            # Construct the SELECT query to retrieve the conversation content with the specified title
            stmt = select(sa.text("content")).from_(sa.text("dbo.conversations")).where(sa.text("title") == conversation_title)

            # Execute the SELECT query and fetch the conversation content
            with engine.connect() as connection:
                result = connection.execute(stmt)
                conversation_content = result.fetchone()
            # Display the retrieved conversation content
            if conversation_content is not None:
                return conversation_content
            else:
                return {}

    except Exception as e:
        # Handle any errors that occur
        st.error("Error accessing conversation: {}".format(e))



def saveIntoDatabase(title, content):
    try:
         # Create a cursor to execute SQL statements
        engine = getConnection()
        if engine:
            # Prompt the user for the conversation title and content
            conversation_title = title
            

            query = "INSERT INTO dbo.conversations (title) VALUES (:title)"
            query2 = "SELECT TOP 1 conversation_id FROM dbo.conversations ORDER BY conversation_id DESC"
            parameters= {"title": conversation_title}

            stmt = sa.text(query)
            stmt2 = sa.text(query2)
            # Execute the INSERT query to insert the new conversation
            with engine.connect() as connection:
                connection.execute(stmt, parameters=parameters)
                result = connection.execute(stmt2)
                inserted_row = result.fetchone()
                conversation_id = inserted_row[0]
                connection.commit()
            

            query3 = "INSERT INTO dbo.chats(conversation_id, title, content) VALUES (:conversation_id, :title, :content)"
            stmt3 = sa.text(query3)
            for message in content:
                cont = message["content"]
                parameters= {"conversation_id": conversation_id,"title": conversation_title, "content": cont}
                with engine.connect() as connection:
                    connection.execute(stmt3, parameters=parameters)
                    connection.commit()


    except Exception as e:
    # Handle any errors that occur
        st.error("Error in connection: {}".format(e))


