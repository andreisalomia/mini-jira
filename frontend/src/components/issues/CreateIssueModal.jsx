import { useState } from 'react';
import { Modal, Form, Button, Alert } from 'react-bootstrap';
import { issuesAPI } from '../../services/api';

export default function CreateIssueModal({ show, onHide, projectId, members, onSuccess }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'MEDIUM',
    assignee_id: ''
  });
  const [error, setError] = useState('');
  const [creating, setCreating] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setCreating(true);

    try {
      const data = {
        ...formData,
        project_id: parseInt(projectId),
        assignee_id: formData.assignee_id ? parseInt(formData.assignee_id) : null
      };

      await issuesAPI.create(data);
      setFormData({ title: '', description: '', priority: 'MEDIUM', assignee_id: '' });
      onSuccess();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create issue');
    } finally {
      setCreating(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>Create New Issue</Modal.Title>
      </Modal.Header>
      <Form onSubmit={handleSubmit}>
        <Modal.Body>
          {error && <Alert variant="danger">{error}</Alert>}

          <Form.Group className="mb-3">
            <Form.Label>Title *</Form.Label>
            <Form.Control
              type="text"
              name="title"
              placeholder="Enter issue title"
              value={formData.title}
              onChange={handleChange}
              required
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Description</Form.Label>
            <Form.Control
              as="textarea"
              rows={4}
              name="description"
              placeholder="Describe the issue..."
              value={formData.description}
              onChange={handleChange}
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Priority *</Form.Label>
            <Form.Select
              name="priority"
              value={formData.priority}
              onChange={handleChange}
              required
            >
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="CRITICAL">Critical</option>
            </Form.Select>
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Assignee</Form.Label>
            <Form.Select
              name="assignee_id"
              value={formData.assignee_id}
              onChange={handleChange}
            >
              <option value="">Unassigned</option>
              {members.map((member) => (
                <option key={member.id} value={member.id}>
                  {member.email}
                </option>
              ))}
            </Form.Select>
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={onHide}>
            Cancel
          </Button>
          <Button variant="primary" type="submit" disabled={creating}>
            {creating ? 'Creating...' : 'Create Issue'}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}