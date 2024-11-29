# Missing Person Finder - Using Face Recognition

This project enables users to find missing persons through two methods: by searching their personal details (name, age, hometown, etc.) or through face recognition. The app stores and manages the missing persons' data in a local SQLite database and utilizes the DeepFace library for facial comparison. The web interface is built using Streamlit, making it interactive and user-friendly.

## Features

1. **Find a Person by Details**: Allows users to search for a missing person using their first name, last name, age, and hometown.
2. **Find a Person by Face Recognition**: Users can upload a photo for face recognition, which is then compared with images stored in the database.
3. **Add a New Missing Person**: Users can add a missing person’s record, including their details and a photo.
4. **View the List of Missing Persons**: Displays all missing persons stored in the database in a tabular format.

## Technologies Used

- **Streamlit**: A Python library to create interactive web applications with minimal effort.
- **SQLite3**: A lightweight database engine used to store the missing person data.
- **Pandas**: Used to manage data within the application, particularly for querying and displaying records.
- **Pillow**: Used for image processing (loading and saving images).
- **DeepFace**: A face recognition library that allows for the comparison of facial features from different images.

## Setup Instructions

### Requirements

Before running this project, ensure you have the following Python libraries installed:

- streamlit
- sqlite3
- pandas
- pillow
- deepface

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Rxghav1103/Missing-Person-Finder.git
   cd Missing-Person-Finder
   ```

2. Create a `requirements.txt` file:
   To install the required dependencies, you can use the `requirements.txt` generated earlier. Here is the content for the `requirements.txt`:
   
   ```
   streamlit
   sqlite3
   pandas
   Pillow
   deepface
   ```

   Then install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit application:
   ```bash
   streamlit run final.py
   ```

4. Access the application:
   After running the above command, Streamlit will display a URL in the terminal, typically something like `http://localhost:8501`. Open this URL in your browser to use the application.

### Database Setup

The app uses a local SQLite database (`people.db`) to store the missing persons' records. The database will automatically be created when the app runs, but here’s the SQL query to manually create the table if needed:

```sql
CREATE TABLE persons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    age INTEGER,
    hometown TEXT,
    shelter_name TEXT,
    photo BLOB
);
```

This table stores:
- **id**: Unique identifier for each person.
- **first_name**: The first name of the person.
- **last_name**: The last name of the person.
- **age**: The age of the person.
- **hometown**: The hometown of the person.
- **shelter_name**: The name of the shelter where the person might be located (optional).
- **photo**: A binary large object (BLOB) to store the person’s photo.

## How It Works

### User Interface (Streamlit)

The app uses Streamlit’s simple and interactive components to allow the user to:
- **Select an action**: Either search for a missing person or add a new record.
- **Search by Details**: Enter details like first name, last name, age, and hometown to search for a person in the database.
- **Search by Face Recognition**: Upload a photo for face recognition, which will be compared against images stored in the database.
- **Add a Missing Person Record**: Enter details of a new missing person and upload their photo.

### Core Functions

1. **`get_db_connection()`**: Establishes a connection to the SQLite database.
2. **`display_persons()`**: Retrieves all persons stored in the database and displays them in a DataFrame.
3. **`get_person_details(person_id)`**: Fetches the detailed record of a person based on their unique ID.
4. **`compare_images(image1, image_paths)`**: Compares the uploaded image (`image1`) against all images stored in the database using the DeepFace library. It returns the most matching person ID, image, and similarity score (distance).
5. **Streamlit UI Components**:
   - `st.slider`: Allows users to choose between finding a person or adding a new missing person.
   - `st.text_input` and `st.number_input`: For entering the missing person’s details.
   - `st.file_uploader`: For uploading a photo for face recognition.
   - `st.button`: For triggering actions like searching or submitting new records.

### Face Recognition Workflow

- The uploaded image is compared to images stored in the database using DeepFace’s `verify` function. The function computes a similarity score (distance) between the images.
- The app then displays the person’s details with the highest similarity score.

## Usage

1. **Find a Person**:
   - Select **Find a Person** from the slider.
   - Choose the search method: **Search by Details** (enter first name, last name, age, and hometown) or **Search by Face Recognition** (upload a photo).
   
2. **Add a Missing Person**:
   - Select **Add a Missing Person Record** from the slider.
   - Fill out the form with the person’s details (name, age, hometown) and upload a photo.
   
3. **List of Persons**:
   - The app will display a table listing all the persons stored in the database.

## Future Enhancements

- **Improved Face Recognition**: Integrate advanced models for better accuracy in face comparison.
- **Authentication**: Add user authentication and authorization to secure access to sensitive data.
- **Admin Panel**: Build a panel for administrators to manage records and data.
- **User Feedback**: Allow users to report errors in the face recognition process or incorrect records.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Note**: Ensure that the `photos_db` folder exists in the working directory for storing the uploaded photos, or modify the code to handle this folder creation automatically.


### Steps to Add the README to Your GitHub Repository:

1. In your project folder, create a new file called `README.md`.
2. Copy the above content into the `README.md` file.
3. Commit and push it to your GitHub repository:

```bash
git add README.md
git commit -m "Added detailed README"
git push origin main
```

This README will provide a comprehensive, detailed explanation of your project, installation instructions, usage, and the technologies used.