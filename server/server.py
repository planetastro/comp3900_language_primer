"""
Student Management System: Allows easy organisation of students into groups, tracking group/student names and quantity.

Assumptions:
    - Group/Student IDs are unique
    - When a Group is deleted, all containing students are also deleted
    - There is no maximum number of Groups/Students
    - Group/Student Name must be alphanumeric (e.g., Group 1, Mike! or J3nny)

Edge Cases:
    - Groups cannot be empty (since Groups cannot be edited)
        - Aborts with 400
    - Group/Student Name cannot be empty
        - Aborts with 400
    - Users cannot GET/DELETE non-existent Group IDs
        - Aborts with 404
"""

from flask import Flask, jsonify, request, abort, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class Student:
    __slots__ = 'student_id', 'name'

    def __init__(self, student_id: int, name: str):
        self.student_id = student_id
        self.name = name

    def inner(self) -> dict[str]:
        """Returns a object-format of the given Student."""        
        return { "id": self.student_id, "name": self.name }

class Group:
    __slots__ = 'group_id', 'group_name', 'members'

    def __init__(self, group_id: int, group_name: str, members: list[Student]) -> None:
        self.group_id = group_id
        self.group_name = group_name
        self.members = members

    def summary(self) -> dict[str]:
        """Returns a summary of the given Group."""        
        return {
            "id": self.group_id,
            "groupName": self.group_name,
            "members": [student.student_id for student in self.members]
        }

    def inner(self) -> dict[str]:
        """Returns an object-format of the given Group."""        
        return {
            "id": self.group_id,
            "groupName": self.group_name,
            "members": [student.inner() for student in self.members]
        }

class Groups:
    __slots__ = '_groups', '_auto_group_id', '_auto_member_id'

    def __init__(self) -> None:
        self._groups: dict[int, Group] = {}
        self._auto_group_id = 0
        self._auto_member_id = 0

    def __getitem__(self, group_id) -> Group:
        return self._groups[group_id]

    def __iter__(self):
        return iter(self._groups.values())

    @property
    def next_group_id(self) -> int:
        """The next auto-incremented Group ID to be used.
        NOTE: Fetching this property has the side effect of incrementing it."""
        temp = self._auto_group_id
        self._auto_group_id += 1
        return temp

    @property
    def next_member_id(self) -> int:
        """The next auto-incremented Member ID to be used.
        NOTE: Fetching this property has the side effect of incrementing it."""
        temp = self._auto_member_id
        self._auto_member_id += 1
        return temp

    def group_id_exists(self, group_id: int) -> bool:
        """Returns True if the given Group ID exists."""        
        return group_id in self._groups

    def add_group(self, group_name: str, students: list[str]) -> Group:
        """Stores a new Group with the given name and students and returns the Group."""        
        members = [Student(self.next_member_id, name) for name in students]
        new_group = Group(self.next_group_id, group_name, members)
        self._groups[new_group.group_id] = new_group
        return new_group

    def delete_group(self, group_id: int) -> bool:
        """Checks if the given ID exists and attempts to delete the corresponding Group and Students.
        Returns True if the deletion was successful."""
        if self.group_id_exists(group_id):
            self._groups.pop(group_id)
            return True
        return False

    def get_group(self, group_id) -> dict:
        """Returns a Group object with the specified ID."""
        return self[group_id].inner()

    def get_all_group_summaries(self) -> list[dict]:
        """Returns the Summaries of all existing Groups."""
        return [group.summary() for group in self._groups.values()]

    def get_all_members(self) -> list[dict]:
        """Returns all existing Student objects."""
        return [student.inner() for group in self._groups.values() for student in group.members]

def is_invalid_name(name: str) -> bool:
    """Returns True if the given name is empty or contains non-alphanumeric characters."""
    name = name.strip()
    return not (len(name) > 0 and all(char.isalnum() or char.isspace() for char in name))

def create_json_response(data: any) -> Response:
    """Returns a Response object with the given data parsed into JSON format and logged."""
    response = jsonify(data)
    app.logger.debug(response.json)
    return response

all_groups = Groups()

@app.route('/api/groups', methods=['GET'])
def get_groups():
    """
    Route to get all groups
    return: Array of group objects
    """
    return create_json_response(all_groups.get_all_group_summaries())

@app.route('/api/students', methods=['GET'])
def get_students():
    """
    Route to get all students
    return: Array of student objects
    """
    return create_json_response(all_groups.get_all_members())

@app.route('/api/groups', methods=['POST'])
def create_group():
    """
    Route to add a new group
    param groupName: The name of the group (from request body)
    param members: Array of member names (from request body)
    return: The created group object
    """

    # Getting the request body (DO NOT MODIFY)
    group_data = request.json
    group_name = group_data.get("groupName")
    group_members = group_data.get("members")

    # Edge case 1: Groups cannot be empty
    if len(group_members) == 0:
        abort(400, 'Groups cannot be empty!')

    # Edge case 2: Check if any name is invalid
    for name in [group_name, *group_members]:
        if is_invalid_name(name):
            abort(400, f"The following name is invalid: {name}")

    # Add a new group
    new_group = all_groups.add_group(group_name, group_members)
    return create_json_response(new_group.inner()), 201

@app.route('/api/groups/<int:group_id>', methods=['DELETE'])
def delete_group(group_id: int):
    """
    Route to delete a group by ID
    param group_id: The ID of the group to delete
    return: Empty response with status code 204
    """
    # Edge case 3: Cannot DELETE invalid IDs
    if not all_groups.group_id_exists(group_id):
        abort(404, f"Group not found with ID: {group_id}")

    # Internal server error: could not delete group for some reason
    if not all_groups.delete_group(group_id):
        abort(500, f"Could not delete group with ID: {group_id}")

    return '', 204  # Return 204 (do not modify this line)

@app.route('/api/groups/<int:group_id>', methods=['GET'])
def get_group(group_id: int):
    """
    Route to get a group by ID (for fetching group members)
    param group_id: The ID of the group to retrieve
    return: The group object with member details
    """
    # Edge case 3: Cannot GET invalid IDs
    if not all_groups.group_id_exists(group_id):
        abort(404, f"Group not found with ID: {group_id}")

    return create_json_response(all_groups.get_group(group_id))

if __name__ == '__main__':
    app.run(port=3902, debug=True)
