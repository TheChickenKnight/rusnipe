from rusnipe.agent import root_agent


if __name__ == "__main__":
    print(root_agent.name)
from datetime import date
import requests

response = requests.get("https://classes.rutgers.edu//soc/api/courses.json?campus=NB&year=2026&term=9")
data = response.json()

units = set()
courses = set()
subjects = set()
for course_item in data:
    units.add(course_item["coreCodes"][0]["unit"] if course_item["coreCodes"] else None)
    courses.add(course_item["coreCodes"][0]["course"] if course_item["coreCodes"] else None)
    subjects.add(course_item["coreCodes"][0]["subject"] if course_item["coreCodes"] else None)
print(units)
print("------------------")
print(courses)
print("------------------")
print(subjects)