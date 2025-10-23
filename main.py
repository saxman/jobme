from aimu.models import OllamaClient as ModelClient

SYSTEM_PROMPT = "You are a helpful assistant that helps users write clear and concise cover letters."
RESUME_PROMPT = "Keep the following resume in memory to help write a cover letter:\n\nResume:\n{resume}"
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

    print("Providing resume to the model...")
    client.chat(RESUME_PROMPT.format(resume=RESUME))

    print("Generating cover letter...")
    response = client.chat(COVER_LETTER_PROMPT.format(job_description=JOB_DESCRIPTION))

    print(f"COVER LETTER:\n\n{response}")

if __name__ == "__main__":
    main()
