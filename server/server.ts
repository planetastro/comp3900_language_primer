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

  getGroup(id: number): Group | undefined {
    return this.groups.find(group => group.id == id);
  }

  getAllGroups(): Group[] {
    return this.groups;
  }

  getAllGroupSummaries(): GroupSummary[] {
    return this.groups.map(this.createGroupSummary);
  }

  getAllStudents(): Student[] {
    return this.groups.flatMap(group => group.members);
  }

  createGroupSummary(group: Group): GroupSummary {
    return {
      id: group.id,
      groupName: group.groupName,
      members: group.members.map(student => student.id)
    };
  }

  createGroup(groupName: string, members: string[]): GroupSummary {
    const newGroup: Group = {
      id: this.autoGroupId++,
      groupName,
      members: members.map(this.createStudent, this)
    };
    this.groups.push(newGroup);

    return this.createGroupSummary(newGroup);
  }

  createStudent(name: string): Student {
    return {
      id: this.autoStudentId++,
      name
    };
  }

  deleteGroup(id: number): boolean {
    const index = this.findGroupIndex(id);
    if (index != -1) {
      this.groups.splice(index, 1);
      return true;
    }
    return false;
  }

  findGroupIndex(id: number): number {
    return this.groups.findIndex(group => group.id == id);
  }
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
  // TODO: (sample response below)
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
  allGroups.deleteGroup(id);
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
  const group = allGroups.getGroup(id);

  if (group == undefined) {
    res.status(404).send("Group not found");
  } else {
    res.json(group);
  }
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
