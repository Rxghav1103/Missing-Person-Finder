import streamlit as st
import sqlite3
import pandas as pd
import os
from PIL import Image
from io import BytesIO
from deepface import DeepFace

# Custom CSS for UI enhancement
st.markdown("""
    <style>
        .css-1d391kg {
            padding: 20px;
        }
        .css-1yqoi70 {
            margin-top: 20px;
        }
        .css-1ghxggd {
            padding: 15px;
            border-radius: 10px;
            background-color: #F0F8FF;
        }
        .css-1q8kcm7 {
            font-size: 20px;
        }
        .css-1v3q8c3 {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 16px;
        }
        .css-1v3q8c3:hover {
            background-color: #45a049;
        }
        .css-17p8tw5 {
            background-color: #f44336;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 16px;
        }
        .css-17p8tw5:hover {
            background-color: #da190b;
        }
        .image-container {
            border: 2px solid #cccccc;
            border-radius: 8px;
            padding: 10px;
            margin-top: 10px;
            background-color: #f9f9f9;
        }
        .person-card {
            background-color: #f1f1f1;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            transition: all 0.3s ease-in-out;
        }
        .person-card:hover {
            background-color: #e2e2e2;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Function to create a connection to the database
def get_db_connection():
    conn = sqlite3.connect('people.db')
    return conn

# Function to display all persons in the database
def display_persons():
    conn = get_db_connection()
    df = pd.read_sql('SELECT * FROM persons', conn)
    conn.close()
    return df

# Function to fetch the details of a person by their ID
def get_person_details(person_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM persons WHERE id = ?", (person_id,))
    person_details = cursor.fetchone()  
    conn.close()
    
    if person_details:
        first_name = person_details[1]
        last_name = person_details[2]
        age = person_details[3]
        hometown = person_details[4]
        shelter_name = person_details[5]
        photo = person_details[6]
        return first_name, last_name, age, hometown, shelter_name, photo
    else:
        return None

# Function to save the uploaded image and perform the comparison
def compare_images(image1, image_paths):
    most_matching_id = None
    most_matching_image = None
    lowest_distance = float("inf")

    for person_id, image_path in image_paths:
        try:
            result = DeepFace.verify(image1, image_path, enforce_detection=False)
            distance = result['distance']
            if distance < lowest_distance:
                lowest_distance = distance
                most_matching_id = person_id
                most_matching_image = image_path
        except Exception as e:
            print(f"Error comparing {image1} with {image_path}: {e}")
    
    return most_matching_id, most_matching_image, lowest_distance

# Streamlit UI
st.title("Missing Persons Registry")

option = st.slider("Choose an action", 0, 1, 0, step=1, format="Find a Person/ Add a Missing Person Record")
slider_labels = ["Find a Person", "Add a Missing Person Record"]
st.write(f"Selected Option: {slider_labels[option]}")

if option == 0:
    # Option 0: Find a Person
    st.subheader("Find a Person")
    
    search_method = st.radio("Select Search Method", ("Search by Details", "Search by Face Recognition"))
    
    if search_method == "Search by Details":
        first_name = st.text_input("First Name", key="find_first_name")
        last_name = st.text_input("Last Name", key="find_last_name")
        age = st.number_input("Age", min_value=0, max_value=150)
        hometown = st.text_input("Hometown", key="find_hometown")
        shelter_name = st.text_input("Shelter Name (optional)", key="find_shelter")

        if st.button("Search by Details", key="search_button"):
            with st.spinner("Searching... Please wait."):
                if first_name and last_name:
                    conn = get_db_connection()
                    cursor = conn.cursor()

                    query = '''
                        SELECT * FROM persons
                        WHERE first_name LIKE ? AND last_name LIKE ? AND age = ? AND hometown LIKE ?
                    '''
                    cursor.execute(query, (f"%{first_name}%", f"%{last_name}%", age, f"%{hometown}%"))
                    result = cursor.fetchall()

                    conn.close()

                    if result:
                        for row in result:
                            st.success(f"Person Found: {row[1]} {row[2]}")
                            st.write(f"Age: {row[3]}, Hometown: {row[4]}, Shelter: {row[5]}")
                            st.image(row[6], caption=f"{row[1]} {row[2]}", use_column_width=True)
                    else:
                        st.warning("No match found for the entered details.")
                else:
                    st.error("Please enter at least the first and last name.")

    elif search_method == "Search by Face Recognition":
        uploaded_photo = st.file_uploader("Upload a photo for Face Recognition", type=["jpg", "jpeg", "png"])

        if uploaded_photo:
            st.image(uploaded_photo, caption="Uploaded Photo", use_column_width=True)

            if st.button("Search by Face Recognition"):
                input_image_path = "temp_uploaded_image.jpg"
                with open(input_image_path, "wb") as f:
                    f.write(uploaded_photo.getbuffer())

                output_dir = "photos_db"
                os.makedirs(output_dir, exist_ok=True)

                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id, photo FROM persons;")
                photos = cursor.fetchall()

                image_paths = []
                for row in photos:
                    person_id, photo_blob = row
                    if photo_blob:
                        image = Image.open(BytesIO(photo_blob))
                        image_path = os.path.join(output_dir, f"{person_id}.jpg")
                        image.save(image_path)
                        image_paths.append((person_id, image_path))

                conn.close()

                most_matching_id, most_matching_image, lowest_distance = compare_images(input_image_path, image_paths)

                if most_matching_id:
                    st.success(f"Best Match Found! Similarity: {100 - (lowest_distance * 100):.2f}%")
                    person_details = get_person_details(most_matching_id)
                    
                    if person_details:
                        first_name, last_name, age, hometown, shelter_name, photo = person_details
                        st.image(photo, caption=f"Person ID: {most_matching_id}", use_column_width=True)
                        st.write(f"Name: {first_name} {last_name}")
                        st.write(f"Age: {age}, Hometown: {hometown}")
                        st.write(f"Shelter Name: {shelter_name}")
                    else:
                        st.warning("Details not found for the matching person.")
                else:
                    st.warning("No suitable match found for the uploaded photo.")

elif option == 1:
    st.subheader("Add a Missing Person Record")
    
    photo = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"])
    first_name = st.text_input("First Name", key="add_first_name")
    last_name = st.text_input("Last Name", key="add_last_name")
    age = st.number_input("Age", min_value=0, max_value=150)
    hometown = st.text_input("Hometown", key="add_hometown")
    shelter_name = st.text_input("Shelter Name (optional)", key="add_shelter")

    if st.button("Submit", key="submit_button"):
        with st.spinner("Submitting... Please wait."):
            if photo and first_name and last_name and hometown:
                photo_binary = photo.read()
                conn = get_db_connection()
                cursor = conn.cursor()

                cursor.execute('INSERT INTO persons (first_name, last_name, age, hometown, shelter_name) VALUES (?, ?, ?, ?, ?)',
                               (first_name, last_name, age, hometown, shelter_name))

                person_id = cursor.lastrowid

                cursor.execute('UPDATE persons SET photo = ? WHERE id = ?', (photo_binary, person_id))

                conn.commit()
                conn.close()

                photo_path = os.path.join("photos_db", f"{person_id}.jpg")
                with open(photo_path, "wb") as f:
                    f.write(photo_binary)

                st.success("Person added successfully!")
            else:
                st.error("Please fill in all required fields and upload a photo.")

# Display all persons
st.subheader("List of Persons")
persons_df = display_persons()

if not persons_df.empty:
    st.dataframe(persons_df)
else:
    st.write("No persons added yet.")
