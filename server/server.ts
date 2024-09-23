/**
 * Student Management System: Allows easy organisation of students into groups, tracking group/student names and quantity.
 * 
 * Assumptions:
 *  - Group/Student IDs are unique
 *  - When a Group is deleted, all containing students are also deleted
 *  - There is no maximum number of Groups/Students
 *  - Group/Student Name must be alphanumeric (e.g., Group 1, Mike! or J3nny)
 * 
 * Edge Cases:
 *  - Groups cannot be empty (since Groups cannot be edited)
 *    - Aborts with 400
 *  - Group/Student Name cannot be empty
 *    - Aborts with 400
 *  - Users cannot GET/DELETE non-existent Group IDs
 *    - Aborts with 404
 */

import express, { Request, Response } from 'express';
import cors from 'cors';

// NOTE: you may modify these interfaces
interface Student {
  id: number;
  name: string;
}

interface GroupSummary {
  id: number;
  groupName: string;
  members: number[];
}

interface Group {
  id: number;
  groupName: string;
  members: Student[];
}

////////////////////////////////////////////////////////////////////////////////////////////////////
class Groups {
  groups: Group[];
  autoGroupId: number;
  autoStudentId: number;

  constructor() {
    this.groups = [];
    this.autoGroupId = 0;
    this.autoStudentId = 0;
  }

  /**
   * Returns a Group object with the specified ID.
   * @returns {Group | undefined} - If found, a group object
   */
  getGroup(id: number): Group | undefined {
    return this.groups.find(group => group.id == id);
  }

  /**
   * Returns the Summaries of all existing Groups.
   * @returns {GroupSummary[]} - Array of group summaries
   */
  getAllGroupSummaries(): GroupSummary[] {
    return this.groups.map(this.createGroupSummary);
  }

  /**
   * Returns all existing Student objects.
   * @returns {Student[]} - Array of student objects
   */
  getAllStudents(): Student[] {
    return this.groups.flatMap(group => group.members);
  }

  /**
   * Creates a Summary of the given Group.
   * @returns {GroupSummary} - A group summary
   */
  createGroupSummary(group: Group): GroupSummary {
    return {
      id: group.id,
      groupName: group.groupName,
      members: group.members.map(student => student.id)
    };
  }

  /**
   * Stores a new Group with the given name and students and returns the Group.
   * @returns {GroupSummary} - A group summary
   */
  createGroup(groupName: string, members: string[]): GroupSummary {
    const newGroup: Group = {
      id: this.autoGroupId++,
      groupName,
      members: members.map(this.createStudent, this)
    };
    this.groups.push(newGroup);

    return this.createGroupSummary(newGroup);
  }

  /**
   * Creates a new Student with the given name and returns the Student.
   * @returns {Student} - A student
   */
  createStudent(name: string): Student {
    return {
      id: this.autoStudentId++,
      name
    };
  }

  /**
   * Checks if the given ID exists and attempts to delete the corresponding Group and Students.
   * @returns {boolean} - Returns True if the deletion was successful
   */
  deleteGroup(id: number): boolean {
    const index = this.groups.findIndex(group => group.id == id);;
    if (index != -1) {
      this.groups.splice(index, 1);
      return true;
    }
    return false;
  }
}

function is_invalid_name(name: string): boolean {
  name = name.trim();
  const is_valid = name.length > 0 && name.match(/^[a-zA-Z0-9 ]+$/);
  return !is_valid;
}
////////////////////////////////////////////////////////////////////////////////////////////////////

const app = express();
const port = 3902;

app.use(cors());
app.use(express.json());

const allGroups = new Groups();

/**
 * Route to get all groups
 * @route GET /api/groups
 * @returns {GroupSummary[]} - Array of group objects
 */
app.get('/api/groups', (req: Request, res: Response) => {
  res.json(allGroups.getAllGroupSummaries());
});

/**
 * Route to get all students
 * @route GET /api/students
 * @returns {Student[]} - Array of student objects
 */
app.get('/api/students', (req: Request, res: Response) => {
  res.json(allGroups.getAllStudents());
});

/**
 * Route to add a new group
 * @route POST /api/groups
 * @param {string} req.body.groupName - The name of the group
 * @param {string[]} req.body.members - Array of member names
 * @returns {GroupSummary} - The created group object
 */
app.post('/api/groups', (req: Request, res: Response) => {
  const { groupName, members } = req.body;

  // Edge case 1: Groups cannot be empty
  if (members.length == 0) {
    res.status(400).send("Groups cannot be empty!");
    return;
  }

  // Edge case 2: Check if any name is invalid
  for (const name of [groupName].concat(members)) {
    if (is_invalid_name(name)) {
      res.status(400).send(`The following name is invalid: ${name}`);
      return;
    }
  }

  // Add a new group
  res.json(allGroups.createGroup(groupName, members));
});

/**
 * Route to delete a group by ID
 * @route DELETE /api/groups/:id
 * @param {number} req.params.id - The ID of the group to delete
 * @returns {void} - Empty response with status code 204
 */
app.delete('/api/groups/:id', (req: Request, res: Response) => {
  const id = parseInt(req.params.id);

  // Edge case 3: Cannot DELETE invalid IDs
  const group = allGroups.getGroup(id);
  if (group == undefined) {
    res.status(404).send(`Group not found with ID: ${id}`);
    return;
  }

  // Internal server error: could not delete group for some reason
  if (!allGroups.deleteGroup(id)) {
    res.status(500).send(`Could not delete group with ID: ${id}`);
    return;
  }

  res.sendStatus(204); // send back a 204 (do not modify this line)
});

/**
 * Route to get a group by ID (for fetching group members)
 * @route GET /api/groups/:id
 * @param {number} req.params.id - The ID of the group to retrieve
 * @returns {Group} - The group object with member details
 */
app.get('/api/groups/:id', (req: Request, res: Response) => {
  const id = parseInt(req.params.id);
  
  // Edge case 3: Cannot GET invalid IDs
  const group = allGroups.getGroup(id);
  if (group == undefined) {
    res.status(404).send(`Group not found with ID: ${id}`);
    return;
  }
  
  res.json(group);
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
