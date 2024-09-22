'''
Edge case:
    Empty group name / Empty group members?
Solution:
    Group class requires a group name to be given?

Assumptions:
    - Group IDs are unique
    - Member IDs are unique
    - When a Group is deleted, all its members are also deleted
    - There is no maximum number of Groups/Members
    - Group/Member names can be any character
'''
from flask import Flask, jsonify, request, abort
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class Student:
    __slots__ = 'student_id', 'name'

    def __init__(self, student_id: int, name: str):
        self.student_id = student_id
        self.name = name

    def to_dict(self) -> dict[str]:
        return { "id": self.student_id, "name": self.name }

class Group:
    __slots__ = 'group_id', 'group_name', 'members'

    def __init__(self, group_id: int, group_name: str, members: list[Student]) -> None:
        self.group_id = group_id
        self.group_name = group_name
        self.members = members

    def to_summary(self) -> dict[str]:
        return {
            "id": self.group_id,
            "groupName": self.group_name,
            "members": [student.student_id for student in self.members]
        }

    def to_dict(self) -> dict[str]:
        return {
            "id": self.group_id,
            "groupName": self.group_name,
            "members": [student.to_dict() for student in self.members]
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
        temp = self._auto_group_id
        self._auto_group_id += 1
        return temp

    @property
    def next_member_id(self) -> int:
        temp = self._auto_member_id
        self._auto_member_id += 1
        return temp

    def group_id_exists(self, group_id: int) -> bool:
        return group_id in self._groups

    def add_group(self, group_name: str, group_members: list[str]) -> Group:
        members = [Student(self.next_member_id, name) for name in group_members]
        new_group = Group(self.next_group_id, group_name, members)
        self._groups[new_group.group_id] = new_group
        return new_group

    def delete_group(self, group_id: int) -> bool:
        # Delete group
        if self.group_id_exists(group_id):
            self._groups.pop(group_id)
            return True
        return False

    def get_group_dict(self, group_id) -> dict:
        return self[group_id].to_dict()

    def get_group_summaries(self) -> list[dict]:
        return [group.to_dict() for group in self._groups.values()]

    def get_members_dict(self) -> list[dict]:
        return [student.to_dict() for group in self._groups.values() for student in group.members]

def is_invalid_name(name: str) -> bool:
    return not name.isalpha()

all_groups = Groups()

@app.route('/api/groups', methods=['GET'])
def get_groups():
    """
    Route to get all groups
    return: Array of group objects
    """
    response = jsonify(all_groups.get_group_summaries())
    app.logger.debug(response.json)
    return response

@app.route('/api/students', methods=['GET'])
def get_students():
    """
    Route to get all students
    return: Array of student objects
    """
    response = jsonify(all_groups.get_members_dict())
    app.logger.debug(response.json)
    return response

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

    # Add a new group
    if any(is_invalid_name(name) for name in [group_name, *group_members]):
        abort(400, 'A name given is not fully alphabetical')

    new_group = all_groups.add_group(group_name, group_members)

    response = jsonify(new_group.to_dict())
    app.logger.debug(response.json)
    return response, 201

@app.route('/api/groups/<int:group_id>', methods=['DELETE'])
def delete_group(group_id: int):
    """
    Route to delete a group by ID
    param group_id: The ID of the group to delete
    return: Empty response with status code 204
    """
    if not all_groups.group_id_exists(group_id):
        abort(404, 'Group not found')

    all_groups.delete_group(group_id)
    return '', 204  # Return 204 (do not modify this line)

@app.route('/api/groups/<int:group_id>', methods=['GET'])
def get_group(group_id: int):
    """
    Route to get a group by ID (for fetching group members)
    param group_id: The ID of the group to retrieve
    return: The group object with member details
    """
    if not all_groups.group_id_exists(group_id):
        abort(404, 'Group not found')

    response = jsonify(all_groups.get_group_dict(group_id))
    app.logger.debug(response.json)
    return response

if __name__ == '__main__':
    app.run(port=3902, debug=True)
