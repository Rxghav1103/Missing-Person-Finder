import streamlit as st
import sqlite3
import pandas as pd
import os
from PIL import Image
from io import BytesIO
from deepface import DeepFace

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
# Function to fetch the details of a person by their ID
def get_person_details(person_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM persons WHERE id = ?", (person_id,))
    person_details = cursor.fetchone()  # This will return a tuple with all columns
    conn.close()
    
    if person_details:
        # Adjusted to unpack only the required fields
        first_name = person_details[1]  # Assuming first_name is at index 1
        last_name = person_details[2]   # Assuming last_name is at index 2
        age = person_details[3]         # Assuming age is at index 3
        hometown = person_details[4]    # Assuming hometown is at index 4
        shelter_name = person_details[5]  # Assuming shelter_name is at index 5
        photo = person_details[6]       # Assuming photo is at index 6
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
            # Analyze similarity using DeepFace
            result = DeepFace.verify(image1, image_path, enforce_detection=False)
            distance = result['distance']

            # Track the best match (lowest distance)
            if distance < lowest_distance:
                lowest_distance = distance
                most_matching_id = person_id
                most_matching_image = image_path

        except Exception as e:
            print(f"Error comparing {image1} with {image_path}: {e}")
    
    return most_matching_id, most_matching_image, lowest_distance

# Streamlit UI
st.title("Missing Persons Registry")

# Slider to select an option
option = st.slider("Choose an action", 0, 1, 0, step=1, format="Find a Person/ Add a Missing Person Record")

# Set the labels for the slider
slider_labels = ["Find a Person", "Add a Missing Person Record"]
st.write(f"Selected Option: {slider_labels[option]}")

if option == 0:
    # Option 0: Find a Person
    st.subheader("Find a Person")
    
    # Select Search Method (by details or face recognition)
    search_method = st.radio("Select Search Method", ("Search by Details", "Search by Face Recognition"))
    
    if search_method == "Search by Details":
        # Input fields for searching a person by details
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        age = st.number_input("Age", min_value=0, max_value=150)
        hometown = st.text_input("Hometown")
        shelter_name = st.text_input("Shelter Name (optional)")

        if st.button("Search by Details"):
            if first_name and last_name:
                conn = get_db_connection()
                cursor = conn.cursor()

                # Search query for matching details
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
        # Upload a photo for face recognition
        uploaded_photo = st.file_uploader("Upload a photo for Face Recognition", type=["jpg", "jpeg", "png"])

        if uploaded_photo:
            st.image(uploaded_photo, caption="Uploaded Photo", use_column_width=True)

            if st.button("Search by Face Recognition"):
                # Save uploaded image temporarily
                input_image_path = "temp_uploaded_image.jpg"
                with open(input_image_path, "wb") as f:
                    f.write(uploaded_photo.getbuffer())

                # Create a folder for photos if it doesn't exist
                output_dir = "photos_db"
                os.makedirs(output_dir, exist_ok=True)

                # Extract images from the 'photo' column in the 'persons' table
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id, photo FROM persons;")
                photos = cursor.fetchall()

                image_paths = []
                for row in photos:
                    person_id, photo_blob = row
                    if photo_blob:  # Check if photo is not null
                        image = Image.open(BytesIO(photo_blob))
                        image_path = os.path.join(output_dir, f"{person_id}.jpg")
                        image.save(image_path)
                        image_paths.append((person_id, image_path))

                conn.close()

                # Compare the uploaded image with the database images
                most_matching_id, most_matching_image, lowest_distance = compare_images(input_image_path, image_paths)

                # Output the most matching result
                if most_matching_id:
                    st.success(f"Best Match Found! Similarity: {100 - (lowest_distance * 100):.2f}%")
                    
                    # Get full details of the person with the matching ID
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
    # Option 1: Add a Missing Person Record
    st.subheader("Add a Missing Person Record")
    
    # Upload Photo
    photo = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"])

    # Input fields for person details
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    age = st.number_input("Age", min_value=0, max_value=150)
    hometown = st.text_input("Hometown")
    shelter_name = st.text_input("Shelter Name (optional)")

    if st.button("Submit"):
        if photo is not None and first_name and last_name and hometown:
            # Convert uploaded photo to binary (BLOB)
            photo_binary = photo.read()

            # Create a new person in the database and save the photo as BLOB
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert the person into the database (without the photo)
            cursor.execute('INSERT INTO persons (first_name, last_name, age, hometown, shelter_name) VALUES (?, ?, ?, ?, ?)',
                           (first_name, last_name, age, hometown, shelter_name))

            # Get the last inserted person's ID
            person_id = cursor.lastrowid

            # Save the photo as BLOB for that person
            cursor.execute('UPDATE persons SET photo = ? WHERE id = ?', (photo_binary, person_id))

            conn.commit()
            conn.close()

            # Optionally, save the photo in the local directory based on the person's ID
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
