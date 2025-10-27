from aimu.models import OllamaClient as ModelClient

SYSTEM_PROMPT = "You are a helpful assistant that helps users write clear and concise cover letters."
RESUME_PROMPT = "Keep the following resume in memory to help write a cover letter:\n\nResume:\n{resume}"
EXAMPLE_COVER_LETTER_PROMPT = "Keep the following example cover letter in memory, to use as an example for writing a new cover letter:\n\nCover Letter:\n{cover_letter}"
COVER_LETTER_PROMPT = "Write a cover letter for the following job description based on the resume you have in memory:\n\nJob Description:\n{job_description}"

RESUME = """
John Doe
123 Main St, Anytown, USA
Email: john.doe@email.com
Phone: (123) 456-7890

Overview:
Experienced software developer with a strong background in Python and machine learning. Proven ability to design and implement efficient algorithms and work collaboratively in team environments.

Skills:
- Programming Languages: Python, Java, C++
- Frameworks: TensorFlow, PyTorch, Django
- Tools: Git, Docker, Kubernetes
- Databases: MySQL, PostgreSQL, MongoDB
- Cloud Platforms: AWS, GCP, Azure

Experience:
Software Developer | Tech Solutions Inc. | June 2018 - Present
- Developed and maintained web applications using Django and Flask.
- Implemented machine learning models for data analysis and prediction tasks.
- Collaborated with cross-functional teams to deliver high-quality software solutions.

Intern | Innovative Apps | Jan 2017 - May 2018
- Assisted in the development of mobile applications using Java and Kotlin.
- Participated in code reviews and contributed to team meetings.

Education:
Bachelor of Science in Computer Science | State University | Graduated May 2018
- Relevant Coursework: Data Structures, Algorithms, Machine Learning, Database Systems
- Activities: Member of the Computer Science Club, Volunteer Tutor for Programming Courses
"""

COVER_LETTER = """
Dear Hiring Manager,
I am writing to express my interest in the Python Developer position at Some Company Inc. With a strong background in software development and machine learning, I am confident in my ability to contribute effectively to your AI team.
My experience at Tech Solutions Inc. has equipped me with the skills necessary to design and implement efficient algorithms, as well as collaborate with cross-functional teams to deliver high-quality software solutions.
I have a proven track record of working with Python and machine learning frameworks such as TensorFlow and PyTorch, which I believe aligns well with the requirements of this role.
I am excited about the opportunity to bring my expertise to Some Company Inc. and contribute to the success of your projects. Thank you for considering my application. I look forward to the possibility of discussing how my skills and experiences align with your needs.
Sincerely,
John Doe
"""

JOB_DESCRIPTION = """
Some Company Inc. is seeking a skilled Python developer to join our AI team. The ideal candidate will have experience in developing machine learning models and working with cloud platforms.
Responsibilities include designing algorithms, collaborating with team members., and contributing to the overall success of our projects.
Qualifications:
- Proficiency in Python and machine learning frameworks such as TensorFlow or PyTorch.
- Experience with cloud platforms like AWS or GCP.
- Strong problem-solving skills and ability to work in a team environment.
- Excellent communication skills.
"""

def main():
    print("Initializing model client...")
    client = ModelClient(ModelClient.MODELS.QWEN_3_8B, system_message=SYSTEM_PROMPT)

    resume_text = RESUME
    with open('input/resume.txt', 'r') as file:
        resume_text = file.read()

    print("Providing resume to the model...")
    client.chat(RESUME_PROMPT.format(resume=resume_text))

    cover_letter_text = COVER_LETTER
    with open('input/cover_letter.txt', 'r') as file:
        cover_letter_text = file.read()

    print("Providing example cover letter to the model...")
    client.chat(EXAMPLE_COVER_LETTER_PROMPT.format(cover_letter=cover_letter_text))

    job_description_text = JOB_DESCRIPTION
    with open('input/job_description.txt', 'r') as file:
        job_description_text = file.read()

    print("Generating cover letter...")
    response = client.chat(COVER_LETTER_PROMPT.format(job_description=job_description_text))

    print(f"COVER LETTER:\n\n{response}")

if __name__ == "__main__":
    main()
