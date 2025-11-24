# Contributing to FlowSentinel

Thank you for your interest in contributing to FlowSentinel! This document provides guidelines for contributing to the project.

## 🎯 Project Overview

FlowSentinel is an AI-powered autonomous project intelligence system built for the IBM watsonx Challenge 2025. It uses IBM's Granite 3 8B Instruct model to monitor and analyze software development workflows in real-time.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/flowsentinel.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes thoroughly
6. Commit your changes: `git commit -m "Add: your feature description"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## 📝 Code Style

### Python (Backend)
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and single-purpose
- Maximum line length: 100 characters

Example:
```python
def analyze_events(events: List[Event], team_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze a list of events and return insights.
    
    Args:
        events: List of Event objects to analyze
        team_id: Optional team ID to filter events
        
    Returns:
        Dictionary containing analysis results
    """
    # Implementation here
    pass
```

### TypeScript (Frontend)
- Use TypeScript strict mode
- Define interfaces for data structures
- Use functional components with hooks
- Follow React best practices
- Use meaningful variable names

Example:
```typescript
interface ProjectState {
  status: 'GREEN' | 'YELLOW' | 'RED';
  blockers: string[];
  risks: string[];
  completed_today: string[];
}

const Dashboard: React.FC = () => {
  const [state, setState] = useState<ProjectState | null>(null);
  // Component implementation
};
```

## 🧪 Testing

### Backend Tests
- Write tests for all new endpoints
- Maintain or improve code coverage (currently 88%)
- Use pytest fixtures for common setup
- Test both success and error cases

```bash
# Run tests
pytest tests/ -v --cov=src

# Run specific test file
pytest tests/test_api.py -v
```

### Frontend Tests
- Test components with React Testing Library
- Test user interactions and edge cases
- Mock API calls appropriately

## 📚 Documentation

- Update README.md if adding new features
- Add docstrings to Python functions
- Comment complex logic
- Update API documentation in code comments
- Add examples for new endpoints

## 🔄 Pull Request Process

1. **Title**: Use clear, descriptive titles
   - ✅ "Add: Team health monitoring endpoint"
   - ✅ "Fix: Memory leak in autonomous agent"
   - ✅ "Update: Improve error handling in analytics"
   - ❌ "Update code"
   - ❌ "Fix bug"

2. **Description**: Include:
   - What changes were made
   - Why the changes were necessary
   - How to test the changes
   - Screenshots (for UI changes)
   - Related issues

3. **Testing**: Ensure all tests pass before submitting

4. **Code Review**: Be responsive to feedback and questions

## 🐛 Bug Reports

When reporting bugs, please include:

- **Description**: Clear description of the bug
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: OS, Python version, Node version, etc.
- **Logs**: Relevant error messages or logs
- **Screenshots**: If applicable

Example bug report:
```markdown
### Description
Agent fails to start when using PostgreSQL database

### Steps to Reproduce
1. Set DATABASE_URL to PostgreSQL connection string
2. Start backend with `python src/main.py`
3. Observe error in logs

### Expected Behavior
Agent should start successfully with PostgreSQL

### Actual Behavior
Error: "relation 'events' does not exist"

### Environment
- OS: macOS 14.1
- Python: 3.11.6
- PostgreSQL: 15.4

### Logs
```
ERROR: relation 'events' does not exist
```
```

## ✨ Feature Requests

When requesting features, please include:

- **Use Case**: Why this feature would be useful
- **Proposed Solution**: Your idea for implementing it
- **Alternatives**: Other approaches you considered
- **Additional Context**: Any other relevant information

## 🏗️ Architecture Guidelines

### Backend
- Keep endpoint functions focused and small
- Use dependency injection for database sessions
- Handle errors gracefully with appropriate status codes
- Log important events and errors
- Use environment variables for configuration

### Frontend
- Use React hooks for state management
- Keep components small and reusable
- Use TanStack Query for API calls
- Handle loading and error states
- Follow accessibility best practices

## 📋 Commit Messages

Use conventional commit format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```bash
git commit -m "feat: add deadline risk prediction endpoint"
git commit -m "fix: resolve memory leak in event processor"
git commit -m "docs: update API documentation for webhooks"
git commit -m "refactor: simplify analytics calculation logic"
```

## 🔒 Security

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Report security vulnerabilities privately
- Follow OWASP security best practices

## 📞 Questions?

- Open an issue for questions about the codebase
- Tag issues with appropriate labels
- Be respectful and constructive in discussions

## 🙏 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow
- Celebrate contributions of all sizes

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to FlowSentinel! 🚀
