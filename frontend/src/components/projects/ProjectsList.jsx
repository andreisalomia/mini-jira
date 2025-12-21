import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Container, Row, Col, Card, Button, Modal, Form, Alert, Badge } from 'react-bootstrap';
import { projectsAPI } from '../../services/api';

export default function ProjectsList() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [newProject, setNewProject] = useState({ name: '', description: '' });
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const response = await projectsAPI.list();
      setProjects(response.data);
    } catch (err) {
      setError('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setCreating(true);
    setError('');

    try {
      await projectsAPI.create(newProject);
      setShowModal(false);
      setNewProject({ name: '', description: '' });
      loadProjects();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create project');
    } finally {
      setCreating(false);
    }
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

  return (
    <Container>
      <Row className="mb-4">
        <Col>
          <h2>Projects</h2>
        </Col>
        <Col xs="auto">
          <Button variant="primary" onClick={() => setShowModal(true)}>
            + New Project
          </Button>
        </Col>
      </Row>

      {error && <Alert variant="danger">{error}</Alert>}

      {projects.length === 0 ? (
        <Card className="text-center p-5">
          <Card.Body>
            <h5 className="text-muted">No projects yet</h5>
            <p className="text-muted">Create your first project to get started</p>
            <Button variant="primary" onClick={() => setShowModal(true)}>
              Create Project
            </Button>
          </Card.Body>
        </Card>
      ) : (
        <Row>
          {projects.map((project) => (
            <Col key={project.id} md={6} lg={4} className="mb-4">
              <Card className="h-100">
                <Card.Body>
                  <Card.Title>{project.name}</Card.Title>
                  <Card.Text className="text-muted">
                    {project.description || 'No description'}
                  </Card.Text>
                  <div className="mt-3">
                    <Link to={`/projects/${project.id}`} className="btn btn-primary btn-sm">
                      View Board
                    </Link>
                  </div>
                </Card.Body>
                <Card.Footer className="text-muted small">
                  Created {new Date(project.created_at).toLocaleDateString()}
                </Card.Footer>
              </Card>
            </Col>
          ))}
        </Row>
      )}

      {/* Create Project Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Create New Project</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleCreate}>
          <Modal.Body>
            {error && <Alert variant="danger">{error}</Alert>}
            
            <Form.Group className="mb-3">
              <Form.Label>Project Name</Form.Label>
              <Form.Control
                type="text"
                placeholder="Enter project name"
                value={newProject.name}
                onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                placeholder="Enter project description"
                value={newProject.description}
                onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={creating}>
              {creating ? 'Creating...' : 'Create Project'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </Container>
  );
}