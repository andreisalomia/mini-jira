import { Card, Badge } from 'react-bootstrap';

export default function IssueCard({ issue, onClick, priorityColor }) {
  return (
    <Card 
      className="cursor-pointer hover-shadow" 
      onClick={onClick}
      style={{ cursor: 'pointer', transition: 'box-shadow 0.2s' }}
      onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)'}
      onMouseLeave={(e) => e.currentTarget.style.boxShadow = 'none'}
    >
      <Card.Body>
        <div className="d-flex justify-content-between align-items-start mb-2">
          <Badge bg={priorityColor} className="mb-2">
            {issue.priority}
          </Badge>
          <small className="text-muted">#{issue.id}</small>
        </div>
        
        <Card.Title className="h6 mb-2">{issue.title}</Card.Title>
        
        {issue.description && (
          <Card.Text className="text-muted small" style={{ 
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden'
          }}>
            {issue.description}
          </Card.Text>
        )}
        
        <div className="mt-2 d-flex justify-content-between align-items-center">
          <small className="text-muted">
            {issue.assignee_id ? (
              <span>👤 Assigned</span>
            ) : (
              <span className="text-warning">⚠️ Unassigned</span>
            )}
          </small>
          
          <small className="text-muted">
            {new Date(issue.created_at).toLocaleDateString()}
          </small>
        </div>
      </Card.Body>
    </Card>
  );
}