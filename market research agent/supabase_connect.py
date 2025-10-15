import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DBNAME = os.getenv("DBNAME")

def db_init():
    # Connect to the database
    try:
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )
        print("Connection successful!")
        
        # Create a cursor to execute SQL queries
        cursor = connection.cursor()

        # Create a table if not exists
        create_table = """CREATE TABLE product_strategy_modules (
    module_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL UNIQUE,
    points_to_cover TEXT[] NOT NULL,
    goals TEXT[] NOT NULL,
    embeddings vector(384)
);"""

        create_table = """CREATE TABLE knowledge_graph (
    node_id SERIAL PRIMARY KEY,
    label VARCHAR(255) NOT NULL UNIQUE,
    properties TEXT,
    connected_edges TEXT[][],
    embedding VECTOR(384)
);"""

        create_table = """CREATE TABLE summary (
        id SERIAL PRIMARY KEY,
        sum TEXT NOT NULL
        );"""

        cursor.execute(create_table)
        cursor.execute("COMMIT;")
        # cursor.execute("SELECT * FROM k_graph;")
        # result = cursor.fetchall()
        # print("Result:", result)
        
        # Close the cursor and connection
        cursor.close()
        connection.close()
        print("Connection closed.")

    except Exception as e:
        print(f"Failed to connect: {e}")

def db_free():
    # Connect to the database
    try:
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )
        print("Connection successful!")
        
        # Create a cursor to execute SQL queries
        cursor = connection.cursor()

        # framework_questions = []
        node_data = []
        
        from langchain_huggingface import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        # framework_texts = [f"Title: {q[0]}"+
        #            f"\nPoint to Cover: {', '.join(q[1])}"+
        #            f"\nGoals: {', '.join(q[2])}" for q in framework_questions]
        # framework_embeddings = embeddings.embed_documents(framework_texts)
        # print(framework_embeddings)

        reviews = [
    (
  1,
  'Amazon Fire Tablet',
  'A budget-conscious tablet optimized for media and children''s content. Features 8-inch display, 2.0 GHz Quad-core processor, 2–3 GB RAM, 32 GB storage expandable to 1 TB, 11–12 hour battery life, USB-C charging, Fire OS, and Amazon Appstore limitations.',
  [["Display", "has_component"], ["Processor", "has_component"], ["RAM", "has_component"], ["Storage", "has_component"], ["Battery", "has_component"], ["Charging System", "has_component"], ["Camera", "has_component"], ["Audio", "has_component"], ["Connectivity", "has_component"], ["Software", "has_component"]],
  '[0.12, 0.45, 0.67, 0.23, 0.56, 0.89, 0.44, 0.11]'
),
(
  2,
  'Display',
  '8-inch 1280x800 resolution. Adequate for viewing but pixelated in detailed images. Dull and low-density compared to phones. Perfect for kids and educational apps. Not usable outdoors due to low brightness.',
  [["Amazon Fire Tablet", "component_of"]],
  '[0.33, 0.66, 0.27, 0.41, 0.82, 0.12, 0.19, 0.64]'
),
(
  3,
  'Processor',
  '2.0 GHz Quad-core CPU. Handles media and simple apps well. Upgrade from 1.3 GHz version offers smoother performance. Adequate for price but struggles with 3D games.',
  [["RAM", "works_with"], ["Storage", "affects"], ["Amazon Fire Tablet", "component_of"]],
  '[0.41, 0.72, 0.35, 0.21, 0.55, 0.33, 0.14, 0.65]'
),
(
  4,
  'RAM',
  'Available in 2 GB and 3 GB versions. 3 GB version offers smooth multitasking and faster app switching. 2 GB model struggles with multitasking and causes slowdowns. Users wish for 4 GB version.',
  [["Processor", "paired_with"], ["Amazon Fire Tablet", "component_of"]],
  '[0.28, 0.58, 0.76, 0.31, 0.60, 0.25, 0.15, 0.70]'
),
(
  5,
  'Storage',
  '32 GB internal storage with only 24 GB usable. Quickly fills up. Supports up to 1 TB MicroSD expansion. External cards improve usability for movies, books, and apps.',
  [["MicroSD Slot", "expanded_by"], ["Processor", "depends_on"], ["Amazon Fire Tablet", "component_of"]],
  '[0.34, 0.55, 0.23, 0.78, 0.60, 0.11, 0.50, 0.66]'
),
(
  6,
  'MicroSD Slot',
  'Supports up to 1 TB expansion. Essential due to limited internal memory. Enables smoother media usage and content storage. Performs fast even on 512 GB cards.',
  [["Storage", "expands"], ["Amazon Fire Tablet", "component_of"]],
  '[0.39, 0.44, 0.25, 0.51, 0.75, 0.19, 0.35, 0.80]'
),
(
  7,
  'Battery',
  '11–12 hour battery life. Best aspect of the device. Ideal for travel and video playback. Extended charging time due to slow 5W charger.',
  [["Charging System", "powered_by"], ["Amazon Fire Tablet", "component_of"]],
  '[0.22, 0.61, 0.34, 0.44, 0.68, 0.18, 0.31, 0.73]'
),
(
  8,
  'Charging System',
  'Ships with 5W slow charger taking 4–5 hours. Supports USB-C, replacing fragile micro USB. USB-C port is sturdy and child-friendly. Users upgrade to 15W fast chargers for convenience.',
  [["Battery", "charges"], ["USB-C Port", "includes"], ["Amazon Fire Tablet", "component_of"]],
  '[0.26, 0.73, 0.48, 0.32, 0.59, 0.28, 0.22, 0.61]'
),
(
  9,
  'USB-C Port',
  'Durable, reversible connector. Major improvement from micro USB which failed often. Easier for kids to plug in correctly. Slow charging remains a drawback.',
  [["Charging System", "part_of"], ["Amazon Fire Tablet", "component_of"]],
  '[0.25, 0.67, 0.38, 0.47, 0.64, 0.22, 0.33, 0.77]'
),
(
  10,
  'Camera',
  '2 MP front and rear cameras. Poor image quality, low light sensitivity. 720p video recording limit. Suitable only for basic video calls.',
  [["Amazon Fire Tablet", "component_of"]],
  '[0.30, 0.53, 0.29, 0.61, 0.45, 0.27, 0.40, 0.63]'
),
(
  11,
  'Audio',
  'Stereo speakers are loud and clear. Integrated microphone is muffled and low-quality. Suitable for casual media, not ideal for calls or classes.',
  [["Amazon Fire Tablet", "component_of"]],
  '[0.21, 0.62, 0.30, 0.48, 0.72, 0.15, 0.34, 0.58]'
),
(
  12,
  'Connectivity',
  'Dual-band Wi-Fi (2.4/5 GHz) provides stable, fast streaming. Bluetooth 5.0 ensures seamless headphone pairing. Excellent for wireless media consumption.',
  [["Amazon Fire Tablet", "component_of"]],
  '[0.29, 0.50, 0.37, 0.55, 0.71, 0.19, 0.26, 0.60]'
),
(
  13,
  'Software',
  'Fire OS restricts users to Amazon Appstore. No official Google Play support, limiting app variety. OS feels snappy on higher RAM versions but sluggish otherwise.',
  [["RAM", "performance_depends_on"], ["Amazon Fire Tablet", "component_of"]],
  '[0.36, 0.48, 0.29, 0.62, 0.67, 0.24, 0.31, 0.54]'
),
(
  14,
  'Build Quality',
  'Plastic build but durable for kids. Slightly heavy due to large battery. Feels solid, built to withstand casual drops.',
  [["Battery", "weight_contributor"], ["Amazon Fire Tablet", "component_of"]],
  '[0.40, 0.55, 0.24, 0.53, 0.61, 0.28, 0.20, 0.73]'
),
(
  15,
  'User Experience',
  'Smooth and responsive on 3 GB RAM variant. Frustrating lag on 2 GB version. Overall usability boosted by MicroSD and battery life but hindered by Fire OS and slow charging.',
  [["RAM", "influences"], ["Software", "affected_by"], ["Battery", "influences"], ["Storage", "influences"]],
  '[0.27, 0.60, 0.39, 0.45, 0.68, 0.32, 0.21, 0.58]'
),
(
  16,
  'Performance',
  'Dependent on combination of processor, RAM, and storage speed. 3 GB version feels snappy, while 2 GB version lags heavily when multitasking.',
  [["Processor", "affects"], ["RAM", "depends_on"], ["Storage", "depends_on"]],
  '[0.31, 0.49, 0.44, 0.52, 0.63, 0.18, 0.29, 0.71]'
),
(
  17,
  'Value',
  'At around $100, offers excellent value for basic media and education. Limitations in speed, camera, and app store are acceptable trade-offs for the price.',
  [["Amazon Fire Tablet", "evaluates"]],
  '[0.20, 0.57, 0.32, 0.43, 0.69, 0.16, 0.30, 0.65]'
)
]
        def format_2d_array(lst):
            def format_inner_list(inner_list):
                return '{"' + '", "'.join(inner_list) + '"}'
            formatted_rows = [format_inner_list(row) for row in lst]
            return '{' + ', '.join(formatted_rows) + '}'

        reviews = []
        for node_id, label, properties, connected_edges, _ in reviews:

            formatted_edges = format_2d_array(connected_edges)

            vector_embedding = embeddings.embed_documents([properties])[0]
            vector_string = '[' + ','.join(map(str, vector_embedding)) + ']'

            Q_query = f"INSERT INTO knowledge_graph (node_id, label, properties, connected_edges, embedding) VALUES ({node_id}, '{label}', '{properties}', '{formatted_edges}', '{vector_string}') RETURNING node_id;"
            cursor.execute(Q_query)
        cursor.execute("COMMIT;")

        # Ask queries and execute
        while True:
            free_query = input("Enter SQL query:")
            if free_query == "q":
                break
            cursor.execute(free_query)
            result = cursor.fetchall()
            print("Result:", result)
            break
        
        # Close the cursor and connection
        cursor.close()
        connection.close()
        print("Connection closed.")

    except Exception as e:
        print(f"Failed to connect: {e}")
        return 1

if __name__ == "__main__":
    db_init()