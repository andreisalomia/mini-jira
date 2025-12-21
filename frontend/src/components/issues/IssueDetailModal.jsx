import { useState, useEffect } from 'react';
import { Modal, Form, Button, Alert, Badge, Card, ListGroup, Tab, Tabs } from 'react-bootstrap';
import { issuesAPI, commentsAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const PRIORITY_COLORS = {
  LOW: 'secondary',
  MEDIUM: 'info',
  HIGH: 'warning',
  CRITICAL: 'danger'
};

const STATUS_COLORS = {
  OPEN: 'secondary',
  IN_PROGRESS: 'primary',
  DONE: 'success'
};

export default function IssueDetailModal({ show, onHide, issueId, members, onUpdate }) {
  const { user } = useAuth();
  const [issue, setIssue] = useState(null);
  const [auditLog, setAuditLog] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updating, setUpdating] = useState(false);

  // Edit mode
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({});

  // Comments
  const [newComment, setNewComment] = useState('');
  const [addingComment, setAddingComment] = useState(false);

  useEffect(() => {
    if (show && issueId) {
      loadIssue();
    }
  }, [show, issueId]);

  const loadIssue = async () => {
    setLoading(true);
    try {
      const [issueRes, auditRes] = await Promise.all([
        issuesAPI.get(issueId),
        issuesAPI.getAuditLog(issueId)
      ]);
      
      setIssue(issueRes.data);
      setAuditLog(auditRes.data);
      setFormData({
        title: issueRes.data.title,
        description: issueRes.data.description || '',
        status: issueRes.data.status,
        priority: issueRes.data.priority,
        assignee_id: issueRes.data.assignee_id || ''
      });
    } catch (err) {
      setError('Failed to load issue');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setError('');
    setUpdating(true);

    try {
      const data = {
        ...formData,
        assignee_id: formData.assignee_id ? parseInt(formData.assignee_id) : null
      };

      await issuesAPI.update(issueId, data);
      setIsEditing(false);
      onUpdate();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update issue');
    } finally {
      setUpdating(false);
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    setAddingComment(true);
    setError('');

    try {
      await commentsAPI.create({
        content: newComment,
        issue_id: issueId
      });
      
      setNewComment('');
      loadIssue(); // Reload to get new comment
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to add comment');
    } finally {
      setAddingComment(false);
    }
  };

  const handleDeleteComment = async (commentId) => {
    if (!window.confirm('Delete this comment?')) return;

    try {
      await commentsAPI.delete(commentId);
      loadIssue();
    } catch (err) {
      setError('Failed to delete comment');
    }
  };

  const canEdit = () => {
    if (!issue || !user) return false;
    return issue.reporter_id === user.id || issue.assignee_id === user.id;
  };

  const canChangeStatus = (newStatus) => {
    if (newStatus === 'DONE' && issue.assignee_id !== user.id) {
      return false;
    }
    return true;
  };

  if (loading) {
    return (
      <Modal show={show} onHide={onHide} size="lg">
        <Modal.Body className="text-center p-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </Modal.Body>
      </Modal>
    );
  }

  if (!issue) return null;

  return (
    <Modal show={show} onHide={onHide} size="lg">
      <Modal.Header closeButton>
        <Modal.Title>
          Issue #{issue.id}
          <Badge bg={STATUS_COLORS[issue.status]} className="ms-2">
            {issue.status.replace('_', ' ')}
          </Badge>
          <Badge bg={PRIORITY_COLORS[issue.priority]} className="ms-2">
            {issue.priority}
          </Badge>
        </Modal.Title>
      </Modal.Header>

      {error && <Alert variant="danger" className="m-3">{error}</Alert>}

      {isEditing ? (
        <Form onSubmit={handleUpdate}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Title</Form.Label>
              <Form.Control
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={4}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Status</Form.Label>
              <Form.Select
                value={formData.status}
                onChange={(e) => {
                  if (canChangeStatus(e.target.value)) {
                    setFormData({ ...formData, status: e.target.value });
                  } else {
                    setError('Only assignees can move issues to DONE');
                  }
                }}
              >
                <option value="OPEN">Open</option>
                <option value="IN_PROGRESS">In Progress</option>
                <option value="DONE">Done</option>
              </Form.Select>
              <Form.Text className="text-muted">
                {issue.status === 'OPEN' && 'Can move to: In Progress'}
                {issue.status === 'IN_PROGRESS' && 'Can move to: Open, Done (assignee only)'}
                {issue.status === 'DONE' && 'Can move to: In Progress'}
              </Form.Text>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Priority</Form.Label>
              <Form.Select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
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
                value={formData.assignee_id}
                onChange={(e) => setFormData({ ...formData, assignee_id: e.target.value })}
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
            <Button variant="secondary" onClick={() => setIsEditing(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit" disabled={updating}>
              {updating ? 'Saving...' : 'Save Changes'}
            </Button>
          </Modal.Footer>
        </Form>
      ) : (
        <>
          <Modal.Body>
            <Tabs defaultActiveKey="details" className="mb-3">
              <Tab eventKey="details" title="Details">
                <div className="mb-4">
                  <h5>{issue.title}</h5>
                  <p className="text-muted">{issue.description || 'No description'}</p>
                  
                  <div className="mt-3">
                    <strong>Assignee:</strong>{' '}
                    {issue.assignee_id ? (
                      <span>{members.find(m => m.id === issue.assignee_id)?.email || 'Unknown'}</span>
                    ) : (
                      <span className="text-muted">Unassigned</span>
                    )}
                  </div>
                  
                  <div className="mt-2">
                    <strong>Reporter:</strong>{' '}
                    {members.find(m => m.id === issue.reporter_id)?.email || 'Unknown'}
                  </div>
                  
                  <div className="mt-2 small text-muted">
                    Created: {new Date(issue.created_at).toLocaleString()}
                    <br />
                    Updated: {new Date(issue.updated_at).toLocaleString()}
                  </div>
                </div>

                {canEdit() && (
                  <Button variant="outline-primary" size="sm" onClick={() => setIsEditing(true)}>
                    Edit Issue
                  </Button>
                )}
              </Tab>

              <Tab eventKey="comments" title={`Comments (${issue.comments?.length || 0})`}>
                <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                  {issue.comments && issue.comments.length > 0 ? (
                    <ListGroup variant="flush">
                      {issue.comments.map((comment) => (
                        <ListGroup.Item key={comment.id}>
                          <div className="d-flex justify-content-between align-items-start">
                            <div className="flex-grow-1">
                              <small className="text-muted">
                                {comment.author_email} • {new Date(comment.created_at).toLocaleString()}
                              </small>
                              <p className="mb-0 mt-1">{comment.content}</p>
                            </div>
                            {comment.author_id === user?.id && (
                              <Button
                                variant="link"
                                size="sm"
                                className="text-danger p-0"
                                onClick={() => handleDeleteComment(comment.id)}
                              >
                                Delete
                              </Button>
                            )}
                          </div>
                        </ListGroup.Item>
                      ))}
                    </ListGroup>
                  ) : (
                    <p className="text-muted text-center p-4">No comments yet</p>
                  )}
                </div>

                <Form onSubmit={handleAddComment} className="mt-3">
                  <Form.Group>
                    <Form.Control
                      as="textarea"
                      rows={3}
                      placeholder="Add a comment..."
                      value={newComment}
                      onChange={(e) => setNewComment(e.target.value)}
                    />
                  </Form.Group>
                  <Button
                    variant="primary"
                    type="submit"
                    className="mt-2"
                    size="sm"
                    disabled={addingComment || !newComment.trim()}
                  >
                    {addingComment ? 'Adding...' : 'Add Comment'}
                  </Button>
                </Form>
              </Tab>

              <Tab eventKey="activity" title="Activity">
                <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                  {auditLog.length > 0 ? (
                    <ListGroup variant="flush">
                      {auditLog.map((log) => (
                        <ListGroup.Item key={log.id}>
                          <small className="text-muted">
                            {new Date(log.timestamp).toLocaleString()}
                          </small>
                          <div>
                            <strong>{log.action.replace('_', ' ')}</strong>
                            {log.old_value && log.new_value && (
                              <span className="text-muted">
                                {' '}: {log.old_value} → {log.new_value}
                              </span>
                            )}
                          </div>
                        </ListGroup.Item>
                      ))}
                    </ListGroup>
                  ) : (
                    <p className="text-muted text-center p-4">No activity yet</p>
                  )}
                </div>
              </Tab>
            </Tabs>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={onHide}>
              Close
            </Button>
          </Modal.Footer>
        </>
      )}
    </Modal>
  );
}