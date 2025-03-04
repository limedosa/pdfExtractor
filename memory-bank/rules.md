# Project Rules and Guidelines

## Code Structure Rules
1. Modular Design
   - Separate components into distinct modules
   - Clear interface definitions
   - Single responsibility principle

2. Style Guidelines
   - Follow Python PEP 8
   - Use type hints
   - Maximum line length: 88 characters
   - Use docstrings for all public functions

3. Error Handling
   - Use custom exception classes
   - Implement comprehensive error messages
   - Log all errors with context
   - Provide recovery mechanisms where possible

## Naming Conventions
1. Files
   - lowercase with underscores
   - descriptive names
   - _test suffix for test files

2. Classes
   - CapitalizedWords (PascalCase)
   - Clear, descriptive names
   - Avoid abbreviations

3. Functions
   - lowercase_with_underscores
   - verb_noun naming pattern
   - clear purpose indication

4. Variables
   - lowercase_with_underscores
   - descriptive names
   - no single-letter names except in loops

## Documentation Requirements
1. Code Documentation
   - Docstrings for all modules
   - Function parameter documentation
   - Return type documentation
   - Usage examples in docstrings

2. README Requirements
   - Installation instructions
   - Usage examples
   - Configuration options
   - Troubleshooting guide

## Testing Standards
1. Unit Tests
   - One test file per module
   - Test all public interfaces
   - Mock external dependencies
   - >80% code coverage

2. Integration Tests
   - Test component interactions
   - Test main workflows
   - Include error cases
   - Test configuration variations

## Version Control
1. Commit Messages
   - Clear, descriptive messages
   - Present tense
   - Reference issue numbers
   - Include context when needed

2. Branch Strategy
   - main: stable release
   - develop: active development
   - feature/: new features
   - fix/: bug fixes

## Performance Guidelines
1. Resource Usage
   - Memory efficient processing
   - Proper resource cleanup
   - Connection pooling
   - Timeout handling

2. Optimization Rules
   - Profile before optimizing
   - Document performance decisions
   - Consider memory vs speed tradeoffs
   - Implement caching where beneficial

## Security Rules
1. Input Validation
   - Validate all URL inputs
   - Sanitize output data
   - Implement timeout limits
   - Handle malformed input gracefully

2. Network Security
   - Verify SSL certificates
   - Implement rate limiting
   - Follow robots.txt rules
   - Handle redirects safely

These rules should be implemented in the project's .clinerules file and enforced through code review and automated checks.