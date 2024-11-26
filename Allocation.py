import mysql.connector

# MySQL database connection
connection = mysql.connector.connect(
    host="localhost",          # Change to your MySQL host
    user="root",               # Your MySQL username
    password="Akshat@1249",    # Your MySQL password
    database="vp_doc_db"       # Your MySQL database name
)

cursor = connection.cursor()

# Function to allocate doctor to the patient based on disorder
def allocate_doctor_scheduling_db(connection, disorder, patient_id):
    cursor = connection.cursor()

    # Step 1: Fetch doctors for the predicted disorder who are available
    query = """
    SELECT 
        Doctor_ID, Doctor_Name, Expertise, Experience, Availability, Patient_Allocated
    FROM 
        doctors
    WHERE 
        Expertise = %s AND Availability = 1
    """
    cursor.execute(query, (disorder,))
    available_doctors = cursor.fetchall()

    if not available_doctors:
        print("No doctors available for the predicted disorder.")
        return None, None

    # Step 2: Calculate workload and sort doctors
    doctors = []
    for doctor in available_doctors:
        doctor_id, doctor_name, expertise, experience, availability, patient_allocated = doctor
        workload = len(patient_allocated.split(",")) if patient_allocated else 0
        doctors.append((doctor_id, doctor_name, expertise, experience, availability, workload, patient_allocated))

    # Sort by workload (ascending) and experience (descending)
    doctors.sort(key=lambda x: (x[5], -x[3]))

    # Step 3: Allocate the patient to the doctor with the least workload
    selected_doctor = doctors[0]
    doctor_id, doctor_name, expertise, experience, availability, workload, patient_allocated = selected_doctor

    # Update the patient's allocation in the database
    if patient_allocated:
        updated_allocation = f"{patient_allocated},{patient_id}"
    else:
        updated_allocation = patient_id

    # Update the doctor's availability and workload
    MAX_WORKLOAD = 5
    new_availability = 0 if workload + 1 >= MAX_WORKLOAD else 1

    update_query = """
    UPDATE doctors
    SET Patient_Allocated = %s, Availability = %s
    WHERE Doctor_ID = %s
    """
    cursor.execute(update_query, (updated_allocation, new_availability, doctor_id))
    connection.commit()

    return doctor_name, doctor_id

# Function to allow the user to input predicted disorder
def get_predicted_disorder():
    """
    Allow the user to input the predicted disorder.
    :return: Predicted disorder as a string
    """
    disorder = input("Enter the predicted disorder (e.g., Autism Spectrum Disorder): ")
    return disorder

# Dynamic input for patient and symptoms
new_patient_id = input("Enter Patient ID: ")

# Get the predicted disorder from the user
predicted_disorder = get_predicted_disorder()

# Allocate a doctor for the patient
doctor_name, doctor_id = allocate_doctor_scheduling_db(connection, predicted_disorder, new_patient_id)

if doctor_name:
    print(f"Patient {new_patient_id} allocated to {doctor_name} ({doctor_id}).")

# Verify the update in the database
verify_query = "SELECT * FROM doctors WHERE Expertise = %s"
cursor.execute(verify_query, (predicted_disorder,))
updated_doctors = cursor.fetchall()

print("\nUpdated Doctor Data:")
for doctor in updated_doctors:
    print(doctor)

# Close the database connection
connection.close()
