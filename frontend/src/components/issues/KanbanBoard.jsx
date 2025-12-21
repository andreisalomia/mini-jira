import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Card, Button, Badge, Form, InputGroup } from 'react-bootstrap';
import { projectsAPI, issuesAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import IssueCard from './IssueCard';
import CreateIssueModal from './CreateIssueModal';
import IssueDetailModal from './IssueDetailModal';

const COLUMNS = [
  { id: 'OPEN', title: 'Open', variant: 'secondary' },
  { id: 'IN_PROGRESS', title: 'In Progress', variant: 'primary' },
  { id: 'DONE', title: 'Done', variant: 'success' }
];

const PRIORITY_COLORS = {
  LOW: 'secondary',
  MEDIUM: 'info',
  HIGH: 'warning',
  CRITICAL: 'danger'
};

export default function KanbanBoard() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [project, setProject] = useState(null);
  const [issues, setIssues] = useState([]);
  const [filteredIssues, setFilteredIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedIssue, setSelectedIssue] = useState(null);
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPriority, setFilterPriority] = useState('');
  const [filterAssignee, setFilterAssignee] = useState('');

  useEffect(() => {
    loadData();
  }, [projectId]);

  useEffect(() => {
    applyFilters();
  }, [issues, searchTerm, filterPriority, filterAssignee]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [projectRes, issuesRes] = await Promise.all([
        projectsAPI.get(projectId),
        issuesAPI.list({ project_id: projectId })
      ]);
      
      setProject(projectRes.data);
      setIssues(issuesRes.data);
    } catch (err) {
      if (err.response?.status === 403) {
        setError('You do not have access to this project');
      } else {
        setError('Failed to load project');
      }
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...issues];

    // Search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(issue =>
        issue.title.toLowerCase().includes(term) ||
        (issue.description && issue.description.toLowerCase().includes(term))
      );
    }

    // Priority filter
    if (filterPriority) {
      filtered = filtered.filter(issue => issue.priority === filterPriority);
    }

    // Assignee filter
    if (filterAssignee) {
      if (filterAssignee === 'unassigned') {
        filtered = filtered.filter(issue => !issue.assignee_id);
      } else if (filterAssignee === 'me') {
        filtered = filtered.filter(issue => issue.assignee_id === user.id);
      }
    }

    setFilteredIssues(filtered);
  };

  const getIssuesByStatus = (status) => {
    return filteredIssues.filter(issue => issue.status === status);
  };

  const handleIssueClick = (issue) => {
    setSelectedIssue(issue);
  };

  const handleIssueUpdated = () => {
    loadData();
    setSelectedIssue(null);
  };

  const handleIssueCreated = () => {
    loadData();
    setShowCreateModal(false);
  };

  if (loading) {
    return (
      <Container className="mt-5 text-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="mt-5">
        <Card className="text-center p-5">
          <Card.Body>
            <h5 className="text-danger">{error}</h5>
            <Button variant="primary" onClick={() => navigate('/')}>
              Back to Projects
            </Button>
          </Card.Body>
        </Card>
      </Container>
    );
  }

  return (
    <Container fluid>
      {/* Header */}
      <Row className="mb-4">
        <Col>
          <h2>{project?.name}</h2>
          <p className="text-muted">{project?.description}</p>
        </Col>
        <Col xs="auto">
          <Button variant="primary" onClick={() => setShowCreateModal(true)}>
            + New Issue
          </Button>
        </Col>
      </Row>

      {/* Filters */}
      <Row className="mb-4">
        <Col md={4}>
          <InputGroup>
            <InputGroup.Text>🔍</InputGroup.Text>
            <Form.Control
              placeholder="Search issues..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </InputGroup>
        </Col>
        <Col md={3}>
          <Form.Select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
          >
            <option value="">All Priorities</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="CRITICAL">Critical</option>
          </Form.Select>
        </Col>
        <Col md={3}>
          <Form.Select
            value={filterAssignee}
            onChange={(e) => setFilterAssignee(e.target.value)}
          >
            <option value="">All Assignees</option>
            <option value="me">Assigned to me</option>
            <option value="unassigned">Unassigned</option>
          </Form.Select>
        </Col>
        <Col md={2} className="text-muted">
          {filteredIssues.length} of {issues.length} issues
        </Col>
      </Row>

      {/* Kanban Board */}
      <Row>
        {COLUMNS.map((column) => {
          const columnIssues = getIssuesByStatus(column.id);
          
          return (
            <Col key={column.id} md={4} className="mb-4">
              <Card>
                <Card.Header className={`bg-${column.variant} text-white`}>
                  <div className="d-flex justify-content-between align-items-center">
                    <strong>{column.title}</strong>
                    <Badge bg="light" text="dark">{columnIssues.length}</Badge>
                  </div>
                </Card.Header>
                <Card.Body style={{ minHeight: '500px', maxHeight: '70vh', overflowY: 'auto' }}>
                  {columnIssues.length === 0 ? (
                    <div className="text-center text-muted p-4">
                      <p>No issues</p>
                    </div>
                  ) : (
                    <div className="d-grid gap-3">
                      {columnIssues.map((issue) => (
                        <IssueCard
                          key={issue.id}
                          issue={issue}
                          onClick={() => handleIssueClick(issue)}
                          priorityColor={PRIORITY_COLORS[issue.priority]}
                        />
                      ))}
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Col>
          );
        })}
      </Row>

      {/* Modals */}
      <CreateIssueModal
        show={showCreateModal}
        onHide={() => setShowCreateModal(false)}
        projectId={projectId}
        members={project?.members || []}
        onSuccess={handleIssueCreated}
      />

      {selectedIssue && (
        <IssueDetailModal
          show={!!selectedIssue}
          onHide={() => setSelectedIssue(null)}
          issueId={selectedIssue.id}
          members={project?.members || []}
          onUpdate={handleIssueUpdated}
        />
      )}
    </Container>
  );
}