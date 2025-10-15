from dotenv import load_dotenv
import os
import psycopg2
import numpy as np

from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def str_to_list(strng):
    return [float(i) for i in (strng[1:-1].split(','))]

def to_embeddings(strng):
    return embeddings.embed_documents([strng])

load_dotenv()
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DBNAME = os.getenv("DBNAME")

from flask import Flask, request, jsonify

app = Flask(__name__)

# @app.route('/test', methods=['GET'])
# def process_input():
#     user_input = request.args.get('text', default='')
    
#     if user_input:
#         processed_text = user_input[::-1].upper()
#         return jsonify({
#             "status": "success",
#             "input": user_input,
#             "output": processed_text
#         })
#     else:
#         return jsonify({
#             "status": "error",
#             "message": "Please provide input using the 'text' URL parameter."
#         }), 400
    
@app.route('/db', methods=['GET'])
def process_input():
    user_input_full = request.args.get('text', default='')
    user_input = user_input_full[:9]
    
    requests = ['front_end', 'initial__', 'probe____', 'summary__']
    if user_input in requests:

        try:
            connection = psycopg2.connect(
                user=USER,
                password=PASSWORD,
                host=HOST,
                port=PORT,
                dbname=DBNAME
            )
            print("Connection successful!")
            cursor = connection.cursor()

            if user_input == requests[0]:
                print("Entered route 1!")
                return jsonify({
                    "lastUpdated": "2025-10-11T10:05:00Z",
                    "summaryMetrics": {
                        "totalInterviews": {
                        "current": 1284,
                        "change": 3.2
                        },
                        "positiveSentiment": {
                        "current": 78,
                        "change": 2.2
                        },
                        "avgDuration": {
                        "current": 32,
                        "change": -1.4
                        },
                        "topProduct": {
                        "name": "Razer DeathAdder",
                        "change": 0.5
                        }
                    },
                    "sentimentAnalysis": {
                        "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                        "datasets": [
                        {
                            "label": "Positive",
                            "data": [65, 78, 72, 85, 75, 88, 92]
                        },
                        {
                            "label": "Negative/Neutral",
                            "data": [35, 28, 33, 22, 25, 20, 18]
                        }
                        ]
                    },
                    "interviewDurationDistribution": {
                        "labels": ["0-15min", "15-30min", "30-45min", "45-60min", "60min+"],
                        "data": [48, 118, 104, 66, 29]
                    },
                    "mostUsedProducts": [
                        { "name": "Phone", "value": 25 },
                        { "name": "Laptop", "value": 18 },
                        { "name": "Printer", "value": 12 },
                        { "name": "Mouse", "value": 10 },
                        #{ "name": "Product E", "value": 8 },
                        #{ "name": "Product F", "value": 7 },
                        #{ "name": "Product G", "value": 6 },
                        #{ "name": "Product H", "value": 5 },
                        #{ "name": "Product I", "value": 4 },
                        #{ "name": "Other", "value": 5 }
                    ],
                    "SpiderChart": {
                        "productName": "Razer DeathAdder",
                        "scores": [4, 3, 5, 2, 4]
                    }
                })

            elif user_input == requests[1]:
                print("Entered route 2!")

                user_data = user_input_full[9:]
                # print(user_data)
                data_embed = str(to_embeddings(user_data)[0])
                # print(data_embed)

                query = f"""SELECT
                            module_id,
                            title,
                            points_to_cover,
                            goals,
                            1 - (embeddings <=> '{data_embed}') AS cosine_similarity_score
                        FROM
                            product_strategy_modules
                        ORDER BY
                            cosine_similarity_score DESC
                        LIMIT
                            1;"""
                cursor.execute(query)
                result = cursor.fetchone()

                return jsonify({
                    "title": result[1],
                    "points_to_consider": result[2],
                    "goals": result[3]
                })

            elif user_input == requests[2]:
                print("Entered route 3!")

                user_data = user_input_full[9:]
                data_embed = str(to_embeddings(user_data)[0])

                query = f"""SELECT
                            node_id,
                            label,
                            properties,
                            connected_edges,
                            1 - (embedding <=> '{data_embed}') AS cosine_similarity_score
                        FROM
                            knowledge_graph
                        ORDER BY
                            cosine_similarity_score DESC
                        LIMIT
                            1;"""
                cursor.execute(query)
                result = cursor.fetchone()

                context = result[2]
                for i in range(len(result[3])):
                    context = context + ". " + result[3][i][0] + " " + result[3][i][1].replace("_", " ") + " " + result[1]

                print(result[1])

                iquery = f"""SELECT
                            label, properties, connected_edges
                        FROM
                            knowledge_graph
                        WHERE
                '{result[1]}' = ANY(connected_edges[1:array_upper(connected_edges, 1)][1]);"""
                cursor.execute(iquery)
                result1a = cursor.fetchall()
                # print(result2)
                for result2 in result1a:
                    if result2:
                        if len(result2) > 1:
                            for result3 in result2[2]:
                                if result3[0] == result[1]:
                                    context = context + ". " + result3[0] + " " + result3[1].replace("_", " ") + " " + result2[0]
                                    if result2[0] != "Amazon Fire Tablet":
                                        context = context + ". " + result2[1]

                return jsonify({
                    "label": result[1],
                    "properties": result[2],
                    "connected_edges": result[3],
                    "context": context
                })
            
            elif user_input == requests[3]:
                print("Entered route 3!")

                user_data = user_input_full[9:]
                query = f"""INSERT INTO summary (sum) VALUES ('{user_data}') RETURNING id;"""
                cursor.execute(query)
                cursor.execute("COMMIT;")

                return jsonify({
                    "status": "successfully updated summary"
                })

            return jsonify({
                'status': "kinda bad",
                "what happened": "connection successful but some error in the code"
            })

        except Exception as e:
            print(f"Failed to connect: {e}")
    else:
        return jsonify({
            "status": "error",
            "message": "Please provide input using the 'text' URL parameter."
        }), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)