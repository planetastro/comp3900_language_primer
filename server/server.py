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

class Group:
    def __init__(self, group_id: int, group_name: str, group_members: list[int]) -> None:
        self.group_id = group_id
        self.group_name = group_name
        self.group_members = group_members

    def to_dict(self) -> dict:
        return {
            "id": self.group_id,
            "groupName": self.group_name,
            "members": self.group_members
        }

class Groups:
    def __init__(self) -> None:
        self.groups: dict[int, Group] = {}
        self.members: dict[int, str] = {}
        self.auto_group_id = 0
        self.auto_member_id = 0

    @property
    def next_group_id(self) -> int:
        self.auto_group_id += 1
        return self.auto_group_id

    @property
    def next_member_id(self) -> int:
        self.auto_member_id += 1
        return self.auto_member_id

    def group_id_exists(self, group_id) -> bool:
        return group_id in self.groups

    def member_id_exists(self, member_id) -> bool:
        return member_id in self.members

    def add_group(self, group_name: str, group_members: list[str]) -> Group:
        # Add members
        member_ids = []
        for member in group_members:
            member_id = self.next_member_id
            self.members[member_id] = member
            member_ids.append(member_id)

        # Add group
        new_group = Group(self.next_group_id, group_name, member_ids)
        self.groups[new_group.group_id] = new_group

        return new_group

    def get_group(self, group_id) -> Group:
        return self.groups[group_id]

    def delete_member(self, member_id) -> bool:
        if self.member_id_exists(member_id):
            self.members.pop(member_id)
            return True
        return False

    def delete_group(self, group_id) -> bool:
        # Delete group
        if self.group_id_exists(group_id):
            deleted_group = self.groups.pop(group_id)
            return all(self.delete_member(member_id) for member_id in deleted_group.group_members)
        return False

    def get_member_dict(self, member_id) -> dict:
        return { "id": member_id, "name": self.members[member_id] }

    def get_group_dict(self, group_id) -> dict:
        group_dict = self.get_group(group_id).to_dict()

        # Map members to list[dict]
        member_ids = group_dict['members']
        group_dict['members'] = [self.get_member_dict(member_id) for member_id in member_ids]

        return group_dict

    def get_groups_dict(self) -> list[dict]:
        return [group.to_dict() for group in self.groups.values()]

    def get_members_dict(self) -> list[dict]:
        return [self.get_member_dict(member_id) for member_id in self.members]

all_groups = Groups()

@app.route('/api/groups', methods=['GET'])
def get_groups():
    """
    Route to get all groups
    return: Array of group objects
    """
    response = jsonify(all_groups.get_groups_dict())
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
    new_group = all_groups.add_group(group_name, group_members)

    response = jsonify(new_group.to_dict())
    app.logger.debug(response.json)
    return response, 201

@app.route('/api/groups/<int:group_id>', methods=['DELETE'])
def delete_group(group_id):
    """
    Route to delete a group by ID
    param group_id: The ID of the group to delete
    return: Empty response with status code 204
    """
    all_groups.delete_group(group_id)

    app.logger.debug(all_groups.get_groups_dict())
    return '', 204  # Return 204 (do not modify this line)

@app.route('/api/groups/<int:group_id>', methods=['GET'])
def get_group(group_id):
    """
    Route to get a group by ID (for fetching group members)
    param group_id: The ID of the group to retrieve
    return: The group object with member details
    """
    if not all_groups.group_id_exists(group_id):
        abort(404, "Group not found")

    response = jsonify(all_groups.get_group_dict(group_id))
    app.logger.debug(response.json)
    return response

if __name__ == '__main__':
    app.run(port=3902, debug=True)
